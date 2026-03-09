# evals/deepeval/test_cag_queries.py
"""
DeepEval tests for Bella Terra CAG System.
"""
from typing import TYPE_CHECKING
import httpx
import pytest
from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerRelevancyMetric
from deepeval import assert_test

if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest

# API Configuration
API_BASE_URL = "http://localhost:8000"
API_ENDPOINT = f"{API_BASE_URL}/api/query"


def call_cag_api(query: str) -> str:
    """
    Call the CAG API and return the response text.
    
    Args:
        query: The query string to send to the API
        
    Returns:
        The response text from the API
        
    Raises:
        httpx.HTTPError: If the API call fails
    """
    with httpx.Client(timeout=300.0) as client:
        response = client.post(
            API_ENDPOINT,
            json={"query": query},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()["response"]


def contains_all(text: str, values: list[str]) -> bool:
    """
    Check if all specified values are present in the text.
    
    Args:
        text: The text to search in
        values: List of values that must all be present
        
    Returns:
        True if all values are found, False otherwise
    """
    return all(value in text for value in values)


def contains(text: str, value: str) -> bool:
    """
    Check if a value is present in the text.
    
    Args:
        text: The text to search in
        value: The value to search for
        
    Returns:
        True if value is found, False otherwise
    """
    return value in text


class TestCAGQueries:
    """Test cases for CAG system queries."""
    
    def test_beers_under_6_pounds(self) -> None:
        query = "What beers cost less than £6?"
        expected_beers = [
            "Peroni Nastro Azzurro",
            "Menabrea Blonde",
            "York Brewery \"Yorkshire Bitter\"",
            "Saltaire Brewery \"Saltaire Blonde\"",
            "Black Sheep Brewery \"Best Bitter\"",
            "Budvar Original Lager"
        ]
        rubric = (
            "The response should list specific beers with prices under £6, including the price for each beer, with no extra elaboration"
        )
        
        # Call API
        actual_output = call_cag_api(query)
        
        # Test contains-all assertion
        assert contains_all(
            actual_output, expected_beers
        ), f"Expected all beers to be present: {expected_beers}"
        
        # Test LLM rubric using AnswerRelevancyMetric
        test_case = LLMTestCase(
            input=query,
            actual_output=actual_output,
            expected_output=rubric
        )
        
        # Use AnswerRelevancyMetric with a custom prompt that includes the rubric
        metric = AnswerRelevancyMetric(
            threshold=0.7,
            include_reason=True
        )
        
        # Note: AnswerRelevancyMetric evaluates relevancy, not exact rubric compliance
        # For exact rubric matching, you may need a custom metric
        assert_test(test_case, [metric], run_async=False)
    
    def test_pizzas_under_12_pounds(self) -> None:
        query = "What pizzas do you have under £12?"
        expected_pizza = "Margherita"
        rubric = (
            "The response should list the specific pizza with a price under £12, including the price the pizza and no extra elaboration"
        )
        
        # Call API
        actual_output = call_cag_api(query)
        
        # Test contains assertion
        assert contains(
            actual_output, expected_pizza
        ), f"Expected '{expected_pizza}' to be present in response"
        
        # Test LLM rubric
        test_case = LLMTestCase(
            input=query,
            actual_output=actual_output,
            expected_output=rubric
        )
        
        metric = AnswerRelevancyMetric(
            threshold=0.7,
            include_reason=True
        )
        
        assert_test(test_case, [metric], run_async=False)
    
    def test_vegetarian_options(self) -> None:
        query = "Show me vegetarian options"
        expected_items = [
            "Fusilli al Pesto",
            "Penne alla Vodka",
            "Smoked Mackerel Pâté",
            "Fish of the Day"
        ]
        rubric = (
            "The response should list the vegetarian options available, including the price for each item and no extra elaboration"
        )
        
        # Call API
        actual_output = call_cag_api(query)
        
        # Test contains-all assertion
        assert contains_all(
            actual_output, expected_items
        ), f"Expected all items to be present: {expected_items}"
        
        # Test LLM rubric
        test_case = LLMTestCase(
            input=query,
            actual_output=actual_output,
            expected_output=rubric
        )
        
        metric = AnswerRelevancyMetric(
            threshold=0.7,
            include_reason=True
        )
        
        assert_test(test_case, [metric], run_async=False)