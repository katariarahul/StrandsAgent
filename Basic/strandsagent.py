from strands import Agent, tool
from strands_tools import calculator, current_time


# 1. Define a custom tool
@tool
def count_keyword(text: str, keyword: str) -> int:
    """
    Count how many times a keyword appears in a chunk of text.

    Args:
        text: The text to search.
        keyword: Case-insensitive keyword to count.
    Returns:
        Number of occurrences.
    """
    if not isinstance(text, str) or not isinstance(keyword, str):
        return 0

    if not keyword:
        return 0

    return text.lower().count(keyword.lower())

# Set the model ID, e.g., Amazon Nova Lite.
modelId = "apac.amazon.nova-micro-v1:0" #apac.amazon.nova-lite-v1:0";

# 2. Create the agent using built-in and custom tools
""" the Model ID and Bedrock credentials (including tokens) 
are not explicitly typed out because the strands library 
uses default values and environment variables to handle them automatically.
The Default: By default, the strands-agents SDK is configured to use Amazon Bedrock with the Claude 3 Sonnet model."""
strandsagent = Agent(
    model=modelId,
    tools=[
        calculator,     # from strands-agents-tools
        current_time,   # from strands-agents-tools
        count_keyword,  # our custom exam-themed tool
    ],

    system_prompt=(
        "You are a helpful generative AI assistant."
        "Use tools when they help produce accurate answers."
    ),
)


def callStrandsAgent():
    # 3. Ask the agent a question that uses the tools
    message = """
        You have three tasks:

        1. What time is it right now?
        2. Calculate (3111696 / 74088).
        3. What is the Capital of India?
        4. In the text below, how many times does the word 'prompt' appear?

        Text: 
      """
    result = strandsagent(message)

    return result
