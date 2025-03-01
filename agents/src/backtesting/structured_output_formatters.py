from pydantic import BaseModel, Field

class ResponseFormatter(BaseModel):
    """Always use this tool to structure your response to the user."""
    token_symbol: str = Field(description="The symbol of the token")
    direction: str = Field(description="Are we buying, selling, or holding this token?")
    sentiment:str = Field(description="Sentiment around the token")
    crypto_tokens_identified:str = Field(description="Symbols of the tokens identified")
    confidence_level:str = Field(description="Confidence level of opportunity")
    token_performance_context:str = Field(description="Description of why the signal is important")
    expected_duration:str = Field(description="Length of time we should monitor this asset if it is added to the portfolio")
    market_signals:str = Field(description="Type of signal")

