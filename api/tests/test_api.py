import requests
import time
import pytest
from typing import Dict, Any


class TestCAGAPI:
    """Test suite for the CAG API endpoints"""
    
    def test_health_check(self, api_url: str):
        """Test if API health endpoint is working"""
        try:
            response = requests.get(f"{api_url}/health")
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            assert "timestamp" in data
            assert "checks" in data
            print("✅ Health check passed")
        except Exception as e:
            pytest.fail(f"Health check failed: {str(e)}")
    
    def test_root_endpoint(self, api_url: str):
        """Test the root endpoint"""
        try:
            response = requests.get(f"{api_url}/")
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            assert "service" in data
            print("✅ Root endpoint passed")
        except Exception as e:
            pytest.fail(f"Root endpoint failed: {str(e)}")
    
    def test_sync_query(self, api_url: str, timeout: int):
        """Test synchronous query endpoint"""
        print("\n🔍 Testing synchronous query...")
        try:
            start = time.time()
            response = requests.post(
                f"{api_url}/api/query",
                json={"query": "What beers cost less than £6?"},
                timeout=timeout
            )
            elapsed = time.time() - start
            
            if response.status_code == 200:
                result = response.json()
                assert "query" in result
                assert "response" in result
                assert "session_id" in result
                assert "timestamp" in result
                assert "processing_time" in result
                print(f"✅ Sync query completed in {elapsed:.2f} seconds")
                print(f"Response preview: {result['response'][:200]}...")
            else:
                pytest.fail(f"Sync query failed: {response.status_code} - {response.text}")
        except requests.exceptions.Timeout:
            pytest.fail(f"Sync query timed out after {timeout} seconds")
        except Exception as e:
            pytest.fail(f"Sync query error: {str(e)}")
    
    def test_async_query(self, api_url: str, timeout: int):
        """Test asynchronous query endpoint"""
        print("\n🔍 Testing asynchronous query...")
        try:
            # Submit job
            response = requests.post(
                f"{api_url}/api/query/async",
                json={"query": "What pizzas are under £12?"}
            )
            
            if response.status_code != 200:
                pytest.fail(f"Failed to submit async job: {response.status_code}")
            
            job_data = response.json()
            assert "job_id" in job_data
            assert "status" in job_data
            job_id = job_data["job_id"]
            print(f"📋 Job ID: {job_id}")
            
            # Poll for results
            start = time.time()
            while True:
                status_response = requests.get(f"{api_url}/api/jobs/{job_id}")
                assert status_response.status_code == 200
                job_status = status_response.json()
                
                elapsed = time.time() - start
                print(f"\r⏳ Status: {job_status['status']} ({elapsed:.1f}s)", end="", flush=True)
                
                if job_status['status'] == 'completed':
                    assert "result" in job_status
                    result = job_status["result"]
                    assert "query" in result
                    assert "response" in result
                    print(f"\n✅ Async query completed in {elapsed:.2f} seconds")
                    print(f"Response preview: {result['response'][:200]}...")
                    break
                elif job_status['status'] == 'failed':
                    error_msg = job_status.get('error', 'Unknown error')
                    pytest.fail(f"Async query failed: {error_msg}")
                
                if elapsed > timeout:
                    pytest.fail(f"Async query timed out after {timeout} seconds")
                
                time.sleep(1)
                
        except Exception as e:
            pytest.fail(f"Async query error: {str(e)}")
    
    def test_invalid_query(self, api_url: str):
        """Test API behavior with invalid queries"""
        # Test empty query
        response = requests.post(
            f"{api_url}/api/query",
            json={"query": ""}
        )
        assert response.status_code == 422  # Validation error
        
        # Test missing query
        response = requests.post(
            f"{api_url}/api/query",
            json={}
        )
        assert response.status_code == 422  # Validation error
        
        print("✅ Invalid query tests passed")
    
    def test_nonexistent_job(self, api_url: str):
        """Test behavior when requesting non-existent job"""
        response = requests.get(f"{api_url}/api/jobs/nonexistent-job-id")
        assert response.status_code == 404
        print("✅ Non-existent job test passed")


def test_api_integration():
    """Integration test that runs all API tests"""
    api_url = "http://localhost:8000"
    timeout = 300
    
    # Check if API is running
    try:
        response = requests.get(f"{api_url}/health")
        if response.status_code != 200:
            pytest.skip("API is not running")
    except:
        pytest.skip("API is not accessible")
    
    # Run tests
    test_suite = TestCAGAPI()
    test_suite.test_health_check(api_url)
    test_suite.test_root_endpoint(api_url)
    test_suite.test_sync_query(api_url, timeout)
    test_suite.test_async_query(api_url, timeout)
    test_suite.test_invalid_query(api_url)
    test_suite.test_nonexistent_job(api_url)
    
    print("\n🎉 All API integration tests passed!")


if __name__ == "__main__":
    # Run integration test when script is executed directly
    test_api_integration() 