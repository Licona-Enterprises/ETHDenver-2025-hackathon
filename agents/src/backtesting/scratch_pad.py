import re
import polars as pl
from pydantic import BaseModel, Field

# Sample JSON-like tweet data
tweet_thread = [
    {
        "timestamp": "2025-01-01 12:06:23",
        "response": [
            "1/8 🚀 Hey crypto enthusiasts! It’s Joey here, ready to dive into some trending tokens that might just be the golden tickets you've been searching for! Let's break it down!",
            "2/8 First up, we have $REX. This token has been on the radar for those who love a good buy during dips. If you spot it dropping from a strong launch, it might be your chance to scoop it up at a bargain. Remember, buying low can lead to some sweet gains!",
            "3/8 Next, let’s chat about $EMP. With a market cap of only $80 million, there's chatter about it gearing up for a significant rise. Some even anticipate it reaching '4 digits'! If you’re looking for growth potential, this one could be worth a closer look.",
            "4/8 Last but not least, keep an eye on $SDM. A recent partnership is sparking buzz, and it’s currently seen as heavily discounted. If you believe in its potential, now could be the time to jump in before it catches fire!",
            "5/8 Just remember, while these tokens have promise, the crypto market can be as wild as a bull in a china shop! Do your homework and tread carefully.",
            "6/8 Always keep your risk tolerance in mind. It’s easy to get excited, but balancing your portfolio is key.",
            "7/8 So, are you ready to ride the waves of these tokens? Keep your eyes peeled and your wallets ready!",
            "8/8 Until next time, stay curious and keep exploring the crypto frontier! 🐂💰"
        ]
    }
]

class ResponseFormatter(BaseModel):
    """Always use this tool to structure your response to the user."""
    token_symbol: str = Field(description="The symbol of the token")
    direction: str = Field(description="Are we buying, selling, or holding this token?")


# Define a regex pattern for token symbols
token_pattern = r"\$(\w+)"

# Extract token mentions and timestamps into a list of dictionaries
data = []
for thread in tweet_thread:
    timestamp = thread["timestamp"]
    for tweet in thread["response"]:
        matches = re.findall(token_pattern, tweet)
        # Filter out numeric matches
        token_symbols = [token for token in matches if not token.isdigit()]
        for token in token_symbols:
            data.append({"timestamp": timestamp, "token_symbol": token, "entry_price": 100})

# TODO store these reccomendations as structured outout 
# https://python.langchain.com/docs/concepts/structured_outputs/

# Create a Polars DataFrame
df = pl.DataFrame(data)

# Display the resulting DataFrame
print(df)
