# tweet_scheduler.py: Uses schedule or APScheduler to automate periodic tweets.
import time
from typing import List

class TweetScheduler:

    def __init__(self, tweets: List[str]):
        """
        Initializes the TweetScheduler.

        Parameters
        ----------
        tweets : List[str]
            A list of tweets to post.
        """
        self.tweets = tweets
        self.current_index = 0

    def run(self) -> None:
        """
        Continuously posts tweets at 600-second intervals.
        """
        while True:
            if not self.tweets:
                print("No tweets to post.")
                break

            tweet = self.tweets[self.current_index]
            self.post_tweet(tweet)
            self.current_index = (self.current_index + 1) % len(self.tweets)
            time.sleep(600)

    @staticmethod
    def api_cool_down() -> None:
        for remaining in range(600, 0, -1):
            mins, secs = divmod(remaining, 60)
            timer = f"{mins:02}:{secs:02}"  # Format as MM:SS
            print(f"Updating knowledge base in : {timer}", end="\r", flush=True)
            time.sleep(1)
        print(" " * 50, end="\r")  # Clear the line after countdown finishes
