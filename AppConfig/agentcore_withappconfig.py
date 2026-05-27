from strands import Agent, tool
from strands_tools import calculator, current_time
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from appconfig import get_runtime_config
import logging

logger = logging.getLogger(__name__)

logger.info("inside Agent core")

app = BedrockAgentCoreApp()

#model_id = "apac.amazon.nova-lite-v1:0"
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


@app.entrypoint
def invoke(payload, context):
    # ---------------------------------------------------
    # Fetch latest config
    # ---------------------------------------------------

    config = get_runtime_config()
    logger.info("config = %s", config)

    llm_config = config["llm"]
    config['llm']['model_id']

    model_id = llm_config["model_id"]
    logger.info("Model Id: %s",model_id)

    # ---------------------------------------------------
    # Create Agent Dynamically
    # ---------------------------------------------------

    strandsagent = Agent(
        model=model_id,
        tools=[
            calculator,     # from strands-agents-tools
            current_time,   # from strands-agents-tools
            count_keyword,  # our custom exam-themed tool
        ],

        system_prompt=(
            "You are a helpful generative AI assistant. "
            "Use tools when they help produce accurate answers."
        ),
    )
    # Execute and format response
    result = strandsagent(payload.get("prompt", ""))
    return {"response": result, "active_model": model_id}

if __name__ == "__main__":
    app.run()
