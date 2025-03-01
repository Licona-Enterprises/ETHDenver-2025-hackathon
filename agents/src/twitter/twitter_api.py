import tweepy
from tqdm import trange
import time

from langchain_core.documents import Document

from twitter.tweet_scheduler import TweetScheduler
from config.config import TwitterApiConsts


class TwitterAPI:
    def __init__(self, twitter_api_consts:TwitterApiConsts):
        self.client = tweepy.Client(
            consumer_key=twitter_api_consts.TWITTER_API_KEY,
            consumer_secret=twitter_api_consts.TWITTER_API_KEY_SECRET,
            access_token=twitter_api_consts.TWITTER_ACCESS_TOKEN,
            access_token_secret=twitter_api_consts.TWITTER_ACCESS_TOKEN_SECRET
        )
        self.tweet_scheduler = TweetScheduler([""])

    def post_tweet(self, content: str) -> None:
        """
        Uses tweepy client to create tweet

        Parameters
        ----------
        content : str
            str value of the tweet to post
        """
        try:
            self.client.create_tweet(text=content)
            print("Tweet posted successfully!")
        except Exception as e:
            print(f"Error in post_tweet(): {e}")

    def post_thread(self, contents: list[str]) -> None:
        """
        Posts a Twitter thread, where each tweet is a reply to the previous one.

        Parameters
        ----------
        contents : list[str]
            List of strings, where each string is a tweet in the thread.
        """
        try:
            previous_tweet_id = None   

            # for debug delete later
            print(contents)

            for content in contents:
                if previous_tweet_id is None:
                    response = self.client.create_tweet(text=content)
                    # print("dev disabled live tweeting \n")
                else:
                    self.api_cool_down(previous_tweet_id=previous_tweet_id)
                    response = self.client.create_tweet(
                        text=content, 
                        in_reply_to_tweet_id=previous_tweet_id
                    )
                    # print("dev disabled live tweeting \n")
                                    
                previous_tweet_id = response.data["id"]
                # previous_tweet_id = "123abc"

                self.api_cool_down(previous_tweet_id=previous_tweet_id)

            print("Thread posted successfully!")
        except Exception as e:
            print(f"Error in post_thread(): {e}")

    def get_recent_tweets(self, count: int = 10) -> list[Document]:
        """
        Fetches the most recent tweets from the authenticated user's feed
        and converts them into LangChain Document objects.

        Parameters
        ----------
        count : int, optional
            The number of recent tweets to retrieve (default is 10).

        Returns
        -------
        list[Document]
            A list of LangChain Document objects representing the tweets.

        Raises
        ------
        Exception
            If there is an issue retrieving the tweets.
        """
        try:
            user_id = self.client.get_me().data.id  # Get the authenticated user's ID
            response = self.client.get_users_tweets(
                id=user_id,
                max_results=count,
                tweet_fields=["created_at", "text"]
            )

            if not response.data:
                print("No recent tweets found. \n")
                return []

            documents = [
                Document(
                    page_content=tweet.text,
                    metadata={"created_at": tweet.created_at.isoformat(), "source": "Twitter"}
                )
                for tweet in response.data
            ]
            return documents

        except Exception as e:
            print(f"Error in get_recent_tweets(): {e} \n")
            return []

    def comment_on_tweet(self, content: str, tweet_id: str) -> None:
        """
        Uses tweepy client to comment (reply) on a tweet.

        Parameters
        ----------
        content : str
            Text content of the comment to post.
        tweet_id : str
            ID of the tweet to reply to.
        """
        try:
            self.client.create_tweet(text=content, in_reply_to_tweet_id=tweet_id)
            # print("dev disabled live tweeting \n")
            print(f"Comment posted successfully on tweet ID: {tweet_id}")
            self.api_cool_down(previous_tweet_id=tweet_id)
        except Exception as e:
            print(f"Error in comment_on_tweet(): {e}")

    def api_cool_down(self, previous_tweet_id) -> None:
        """
        Implements a cooldown timer using tqdm for a progress bar.

        The cooldown duration is set to 30 minutes (1800 seconds).
        """
        seconds_to_cool_down: int = 5  # Cooldown duration in seconds
        print(f"Adding tweet to thread {previous_tweet_id}")

        # Use tqdm to create a progress bar
        for remaining in trange(seconds_to_cool_down, desc="Adding tweet to thread", unit="s", ncols=100):
            time.sleep(1)
