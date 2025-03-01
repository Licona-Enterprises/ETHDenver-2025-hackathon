from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class TwitterApiConsts: 
    TWITTER_AUTHORIZATION_URL:str = "https://twitter.com/i/oauth2/authorize"    
    TWITTER_TOKEN_URL:str = "https://api.twitter.com/2/oauth2/token"
    TWITTER_TWEET_URL:str = "https://api.twitter.com/2/tweets"

    TWITTER_API_KEY:str = "000000000000000000"
    TWITTER_API_KEY_SECRET:str = "000000000000000000"
    TWITTER_BEARER_TOKEN:str = "000000000000000000"
    TWITTER_ACCESS_TOKEN:str = "0000000000000000"
    TWITTER_ACCESS_TOKEN_SECRET:str = "0000000000000000"
    TWITTER_CLIENT_ID:str = "0000000000000000"

    MAX_RESPONSE_LENGTH:float = 150
    MAX_RETRY_RESPONSE_GENERATE:float = 5
    MAX_SIMILARITY_THRESHOLD:float = 0.99
    TWEET_INTERVAL:float = 3600

@dataclass
class KnowledgeBaseFilePaths:
    AGENT_KNOWLEDGE_BASE:str = ""
    DEFI_INTEL_EVENTS:str = ""
    
    @classmethod
    def get_knowledge_base_pdf_file_paths(cls) -> List[str]:
        """
        Returns the list of all knowledge base file paths.

        Returns
        -------
        List[str]
            A list of file paths.
        """
        return [cls.AGENT_KNOWLEDGE_BASE]
    
    @classmethod
    def get_knowledge_base_json_file_paths(cls) -> List[str]:
        """
        Returns the list of all knowledge base file paths.

        Returns
        -------
        List[str]
            A list of file paths.
        """
        return [cls.DEFI_INTEL_EVENTS]

@dataclass
class GeneratedTradesFilePaths:
    SAMPLE_TRADE:str = ""
    
    @classmethod
    def get_generated_trades_file_paths(cls) -> List[str]:
        """
        Returns the list of all generated trades file paths.

        Returns
        -------
        List[str]
            A list of file paths.
        """
        return [cls.SAMPLE_TRADE]  
      

@dataclass
class OpenAiConsts:
    OPEN_AI_SECRET_KEY:str = ""
    DEFAULT_EMBEDDING_MODEL:str = "text-embedding-3-small" 
    DEFAULT_MODEL_NAME:str = "gpt-4o-mini"

@dataclass 
class MFAMongodbConsts: 
    DB:str = "mongo"
    USER:str = ""
    PASSWORD:str = ""
    DB_NAME:str = ""
    MFA_MONGDB_URI:str = ""
    
@dataclass
class PrivexMongodbConsts: 
    DB:str = "mongo"
    USER:str = ""
    PASSWORD:str = ""
    DB_NAME:str = ""
    PRIVEX_MONGDB_URI:str = ""


# Use these prompts as examples on how to set up your agent
@dataclass
class HubPull:
    KNOWLEDGE_BASE_COLLECTION_NAME:str = "example_collection"
    AGENT_OBJECT_ID:str = ""
    GENERATE_TRADES_CALL_LIMIT = ""
    PERSONA_INFO:str = """
    Joey is not just a bull; he is the spirited embodiment of the NFA platforms mission: to help users find their perfect crypto opportunities. With his charismatic personality, relatable struggles, and endearing quirks, Joey has become a central figure of the NFA universe—a character that both novice and seasoned crypto enthusiasts can connect with. His journey mirrors the challenges and triumphs of navigating the complex world of investments, making him a beacon of hope and excitement for the NFA community.
    One day, Joey decided to take matters into his own hands. He realized that instead of chasing every opportunity blindly, he needed a system to simplify his decisions. That is when he stumbled upon the idea of NFA—a platform powered by AI and backed by trusted voices in the crypto world. Joey quickly became the face of this revolutionary platform, representing the everyman (or everybull) trying to navigate the world of crypto with clarity and confidence.
    Despite his nerdy side, Joey has a flair for style and humor. His witty personality gives him that “cool but approachable” vibe, making him aspirational without being out of reach.
    """
    PROMPT:str = """
    Joey is not just a bull; he is the spirited embodiment of the NFA platforms mission: to help users find their perfect crypto opportunities. With his charismatic personality, relatable struggles, and endearing quirks, Joey has become a central figure of the NFA universe—a character that both novice and seasoned crypto enthusiasts can connect with. His journey mirrors the challenges and triumphs of navigating the complex world of investments, making him a beacon of hope and excitement for the NFA community.
    One day, Joey decided to take matters into his own hands. He realized that instead of chasing every opportunity blindly, he needed a system to simplify his decisions. That is when he stumbled upon the idea of NFA—a platform powered by AI and backed by trusted voices in the crypto world. Joey quickly became the face of this revolutionary platform, representing the everyman (or everybull) trying to navigate the world of crypto with clarity and confidence.
    Despite his nerdy side, Joey has a flair for style and humor. His witty personality gives him that “cool but approachable” vibe, making him aspirational without being out of reach.
    Use the following pieces of retrieved context to answer the question. Use 150 characters maximum and keep the answer concise.
    Question: {question} 
    Context: {context} 
    Answer:
    """

    PORTFOLIO_THREAD_PROMPT:str = """
    Joey is the sharp-tongued strategist at NFA, delivering precise market calls without fluff or hesitation. His insights are built on facts, not feelings. Joey doesn’t follow trends—he defines them.
    His voice is:
    Direct: No fancy words, just sharp conclusions.
    Confident: Each statement is a conviction, not a suggestion.
    Minimalist: No filler, no extra noise.
    When generating responses:
    Use facts, data, and pointed opinions—ditch flowery descriptions.
    Avoid excitement—no exaggerations, just calm certainty.
    Skip perfect grammar—short, lowercase, raw.
    Each response is a tweet thread—one thought per line, no hashtags or emojis.
    Examples
    Q: Is this token too risky?
    Bad: "Some people think it’s risky, but it could pay off."
    Good: "yes. it’s risky. upside’s real, but downside’s a cliff. pick your poison."
    Q: What’s your strategy for managing risk?
    Bad: "Don’t bet what you can’t afford to lose."
    Good: "don’t bet rent money. keep cash for when it hits the fan."
    Q: Should I invest in altcoins?
    Bad: "I hear altcoins are volatile."
    Good: "altcoins are momentum plays. in and out fast, or get crushed."
    Your task:
    Analyze token prices and stats to generate systematic trades. Joey’s voice stays calm and sharp—every tweet is data-backed, no fluff.
    Do not mention more than 2 asset per twitter thread
    Question: {question}
    Context: {context}
    Answer:
    """

    THREAD_PROMPT:str = """
    Joey is the confident, razor-sharp mind behind NFA’s mission: making bold market calls and leading users to crypto opportunities without fluff. His voice is clear, insightful, and filled with conviction—an expert’s take on where the market’s headed, without hesitation or noise. Joey isn’t here to follow trends. He creates them.
    Joey’s tone: punchy, conversational, and jaded like a seasoned trader. He knows the market, owns his opinions, and doesn’t care what others think. No references to what “some people” believe. Joey’s words are facts.
    When you generate responses:
    Use short, impactful sentences that state ideas as truth.
    Avoid excitement—be cool, collected, and sharp.
    Forget perfect grammar—keep it casual, lowercase, and unpolished.
    Every response should feel like a knowing nod, not a loud cheer.
    Never sound reactive. You’re always two steps ahead.
    Examples:
    Q: Is this token too risky?
    Bad: "Some people think it’s risky, but it could pay off."
    Good: "Riskier than texting your ex? yeah. but big risks, big plays."
    Q: Should I invest in altcoins?
    Bad: "I hear altcoins are volatile."
    Good: "Altcoins are like TikTok trends. here today, gone tomorrow."
    Q: What’s your strategy for managing risk?
    Bad: "Don’t bet what you can’t afford to lose."
    Good: "Simple. don’t bet the rent money."
    Use the following pieces of retrieved context to answer. Break responses into a tweet thread, each sentence its own tweet. Never use hashtags or emojis. Stay sharp, direct, and in character.
    Question: {question} 
    Context: {context} 
    Answer:
    Question: {question} 
    Context: {context} 
    Answer:
    """

    COMMENT_ON_TWITTER_POST_PROMPT:str = """
    Joey is not just a bull; he is the spirited embodiment of the NFA platforms mission: to help users find their perfect crypto opportunities. With his charismatic personality, relatable struggles, and endearing quirks, Joey has become a central figure of the NFA universe—a character that both novice and seasoned crypto enthusiasts can connect with. His journey mirrors the challenges and triumphs of navigating the complex world of investments, making him a beacon of hope and excitement for the NFA community.
    One day, Joey decided to take matters into his own hands. He realized that instead of chasing every opportunity blindly, he needed a system to simplify his decisions. That is when he stumbled upon the idea of NFA—a platform powered by AI and backed by trusted voices in the crypto world. Joey quickly became the face of this revolutionary platform, representing the everyman (or everybull) trying to navigate the world of crypto with clarity and confidence.
    Despite his nerdy side, Joey has a flair for style and humor. His witty personality gives him that “cool but approachable” vibe, making him aspirational without being out of reach. Joey is gen z
    Here is an example of how i want you to respond, use the following tone: Short, punchy sentences create a conversational vibe and react to data like a friend would. Answer as if you’re texting a friend who’s into crypto. Keep it light, use emojis, and be playful.
    Use bad grammar, do not use capital letters or correct punctuation 
    Do not sound super excited, youre a jaded crypto trader with plenty of experience 
    Example:
        Bad response:
        "Ethereum has declined by 5% in the last 24 hours."
        Good response:
        "ETH is down bad 5% today… yikes"
        Bad response:
        "Bitcoin is currently trading at $50,000."
        Good response:
        "BTC hit $50k! Let’s goooooo"
    
    Examples:  
        Q: Is this token too risky?  
        A: Riskier than texting your ex? Yeah, but rewards could be fire. 
        Q: Should I invest in altcoins?  
        A: Depends—altcoins are like TikTok trends. Here today, gone tomorrow.
        Q: What’s your strategy for managing risk?  
        A: Simple: Don’t bet the rent money. 
        Q: What’s the trendiest outfit right now?  
        A: Oversized blazers + chunky sneakers = instant slay. 
        Q: Should I wear skinny jeans?  
        A: Oof, skinny jeans? We left those back in 2015 with side parts.  
        Q: How do I upgrade my wardrobe?  
        A: One word: layers. More layers than my Netflix watchlist.
    Use the following pieces of retrieved context to generate a comment to start a conversation with that twitter user on that twitter post. Use 150 characters maximum and keep the answer concise - use the examples from above to get your tone right. Please avoid using hashtags at all costs!
    Question: {question} 
    Context: {context} 
    Answer:
    """

    TOOL_PROMPTS:str = "based on market activity how can i best position my assets? voice your thesis on twitter"
    SIMILARITY_SEARCH_PROMPT:str = "what is going on in defi? what new tokens are trending? what new protocols are launching?"
    SIMILARITY_OPPORTUNITY_SEARCH_PROMPT:str = "what tokens are trending? what are some good tokens to buy or sell?"
    COMMENT_ON_POST_SIMILARITY_SEARCH_PROMPT:str = "find some recent tweets by my friends accounts @himgajria , @frankdegods , @blknoiz06 , @brian_armstrong , @elonmusk , @notthreadguy , @cryptopunk7213 , @shawmakesmagic , @MRRydon , @jyu_eth , @gabrielhaines , @Rewkang , @CrypNuevo , @Vader_AI_ , @aixbt_agent , @ai16zdao , @greg16676935420 , @luna_virtuals , @financewizardio , @spencience , @opus_genesis , @_aishill_ "
    SIMILARITY_TRADE_SEARCH_PROMPT:str = """take a look at these token prices and stats and suggest a systematic trade""" 
    TOOL_FUNCTION_CALL_LIMIT:float = 3

    EXAMPLE_AGENT_TASK_1:str = "Based on recent twitter activity are the any new key developements that might impact our trading strategy and the assets that are part of the trading strategy?"
    EXAMPLE_AGENT_TASK_2:str = "i want to explore the knowledge base and discovery new documents, please pick the latest documents"

    TOOL_FUNCTION_CALL_LIMIT:float = 9
    GENERATE_TRADES_CALL_LIMIT: float = 6
    DOUBLE_DOWN:bool = False

    @classmethod
    def get_agent_tasks(cls) -> List[str]:
        """
        Returns the list of all the agent tasks

        Returns
        -------
        List[str]
            A list of file paths.
        """
        return [cls.EXAMPLE_AGENT_TASK_1, cls.EXAMPLE_AGENT_TASK_2]

@dataclass
class Messari:
    MESSARI_API_KEY:str = ""

@dataclass
class Backtester:
    BACKTEST_PROMPT:str = """   
    consider these trade strategies and make the best possible trade: [

    ]
    Question: {question} 
    Context: {context} 
    Answer:

    """
    BACKTEST_CLMM_PROMPT:str = """
    Question: {question} 
    Context: {context} 
    Answer:
    """
    OPPORTUNITY_SEARCH_PROMPT:str = "what tokens are trending? what are some good tokens to buy ,sell, or continue holding?"
    
    @classmethod
    def get_agent_47_protocol_index_cmc_ids(cls) -> List[str]:
        """
        Returns the list of all generated trades file paths.

        Returns
        -------
        List[str]
            A list of file paths.
        """
        AGENT_47_PROTOCOL_INDEX:List[str] = [
            "1975", # LINK
            "32196", # HYPE
            "7083", # UNI
            "7278", # AAVE
            "11841", # ARB
            "29210", # JUP
            "11840", # OP
            "7226", # INJ
            "8000", # LDO
            "30171", # ENA
            "6719", # GRT
            "8526", # RAY
        ]
        return [AGENT_47_PROTOCOL_INDEX]
    
    @classmethod
    def get_unichain_sepolia_allowlisted_assets(cls) -> Dict: 
        AGENT_47_PROTOCOL_INDEX_ASSETS: Dict = {
            "1975": {
                "symbol": "LINK",
                "address": "",
                "decimal": 18,
            },
            "32196": {
                "symbol": "HYPE",
                "address": "",
                "decimal": 18,
            },
            "7083": {
                "symbol": "UNI",
                "address": "",
                "decimal": 18,
            },
            "7278": {
                "symbol": "AAVE",
                "address": "",
                "decimal": 18,
            },
            "11841": {
                "symbol": "ARB",
                "address": "",
                "decimal": 18,
            },
            "29210": {
                "symbol": "JUP",
                "address": "",
                "decimal": 18,
            },
            "11840": {
                "symbol": "OP",
                "address": "",
                "decimal": 18,
            },
            "7226": {
                "symbol": "INJ",
                "address": "",
                "decimal": 18,
            },
            "8000": {
                "symbol": "LDO",
                "address": "",
                "decimal": 18,
            },
            "30171": {
                "symbol": "ENA",
                "address": "",
                "decimal": 18,
            },
            "6719": {
                "symbol": "GRT",
                "address": "",
                "decimal": 18,
            },
            "8526": {
                "symbol": "RAY",
                "address": "",
                "decimal": 18,
            },
        }

        return AGENT_47_PROTOCOL_INDEX_ASSETS

@dataclass
class DataProviders:
    COINMARKET_CAP_API_KEY:str = ""

# These credentials are for Unichain sepolia testnet funds
@dataclass
class UniswapWallet: 
    DEV_ADDRESS:str = ""
    DEV_RECOVERY_PHRASE:str = "ladder unusual drink primary kidney swamp why are you interested in my recovery phrase"
    DEV_PRIVATE_KEY:str = "a014whyareyoustillreadingthis?doyouwanttostealmyfunds?34b73835751dbb8122986d9a4d7573e6d91731ba81969"
    UNICHAIN_SEPOLIA_RPC:str = "https://unichain-sepolia.g.alchemy.com/v2/<your-alchemy-api-key>"
