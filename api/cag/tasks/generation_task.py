from crewai import Task


def create_generation_task(query: str, response_generator_agent, context_analysis_task, augmentation_task) -> Task:
    """Create a task to generate the final response"""
    return Task(
        description=f"""Using all the analyzed and augmented context about Bella Terra, 
        generate a comprehensive response to the query: '{query}'
        
        Ensure the response is:
        - Accurate to the source menu data and SQL results
        - Enhanced with the augmented insights about relationships and patterns
        - Well-structured and easy to understand
        - Complete with all relevant details including prices where applicable
        - Helpful for someone trying to understand Bella Terra's offerings
        """,
        expected_output="A comprehensive, friendly response about Bella Terra's menu offerings",
        agent=response_generator_agent,
        context=[context_analysis_task, augmentation_task]
    ) 