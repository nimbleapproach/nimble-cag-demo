from crewai import Task


def create_augmentation_task(context_augmenter_agent, context_analysis_task) -> Task:
    """Create a task to augment context with additional insights"""
    return Task(
        description="""Based on the context analysis, augment the information by:
        1. Identifying implicit relationships between menu items, prices, and categories
        2. Inferring additional relevant details about ingredients or preparation methods
        3. Suggesting related menu items or pairings that might be helpful
        4. Highlighting any special patterns, pricing tiers, or menu groupings
        5. Making connections between different menu sections (pizza, pasta, wine, etc.)
        Ensure to incorporate precise details from the SQL results where relevant.
        """,
        expected_output="Enhanced context with additional insights about Bella Terra's offerings, including structured data.",
        agent=context_augmenter_agent,
        context=[context_analysis_task]
    ) 