from config.config import HubPull, Backtester
from backtesting.strategy_generator import StrategyGenerator
from backtesting.token_prices import TokenPrices
from backtesting.compliance_manager import ComplianceManager
from rag.mongodb_handler import MongoDBHandler


class PortfolioManager:
    """
    Manages trading strategy generation, portfolio metrics updates, and compliance checks.

    Attributes
    ----------
    db_handler : MongoDBHandler
        Handles MongoDB interactions for data persistence.
    agent_info : HubPull
        Provides configuration details for the knowledge base and other settings.
    token_prices : TokenPrices
        Provides methods to fetch and analyze token prices.
    compliance_manager : ComplianceManager
        Ensures compliance with risk management and other investment policies.
    strategy_starter : StrategyGenerator
        Generates trading strategies and manages portfolio metrics.
    """

    def __init__(self, hub_pull=HubPull):
        """
        Initialize the PortfolioManager with required components.

        Parameters
        ----------
        collection_name : str
            Name of the MongoDB collection to interact with.
        """
        # self.agent_info = HubPull()
        self.agent_info = hub_pull
        strategy_generator = Backtester()
        self.token_prices = TokenPrices()
        self.compliance_manager = ComplianceManager()
        self.strategy_starter = StrategyGenerator(collection_name=self.agent_info.KNOWLEDGE_BASE_COLLECTION_NAME, hub_pull=hub_pull, strategy_generator=strategy_generator)

    def create_opportunity(self) -> None:
        """
        Creates trading opportunities using the strategy generator.

        Returns
        -------
        None
        """
        self.strategy_starter.create_opportunity()
        # TODO finish create_clmm_opportunity
        # self.strategy_starter.create_clmm_opportunity()

    def update_portfolio_metrics(self) -> None:
        """
        Updates portfolio metrics with the latest data.

        Returns
        -------
        None
        """
        self.strategy_starter.update_portfolio_metrics()

