import os
from dotenv import load_dotenv
import praw
from prawcore import NotFound


class RedditCrawler:
    def __init__(self) -> None:
        """
        Streaming context

        :return: Initial reddit instance
        """
        load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), './../../../.env'))
        CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
        CLIENT_SECRET = os.getenv("REDDIT_SECRET")
        user_agent = 'example_user_agent'

        # Reddit instance, need username & password if crawl user's own data.
        self.reddit = praw.Reddit(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            user_agent=user_agent
        )

        print("Read-only Reddit instance:", self.reddit.read_only)
        print("---------")

    def check_subreddit(self, sub_name: str) -> bool:
        try:
            self.reddit.subreddits.search_by_name(sub_name, exact=True)
        except NotFound:
            return False
        return True

    def get_subreddit(self, sub_name: str, type: str, limit: int):
        f"""
        Get subreddit posts
        :param sub_name: Subreddit name, r/<subreddit>
        :param type: One of [top, hot, hot, controversial, rising, new]
        :param limit: Number of limited posts
        :return: List of posts
        """
        if not self.check_subreddit(sub_name):
            print(f"Subreddit {sub_name} not exist")
            return

        subreddit = self.reddit.subreddit(sub_name)

        # Dictionary mapping type to corresponding method
        type_to_method = {
            'top': subreddit.top,
            'hot': subreddit.hot,
            'controversial': subreddit.controversial,
            'rising': subreddit.rising,
            'new': subreddit.new
        }

        if type not in type_to_method:
            print(f"Invalid type: {type}")
            return
        top_posts = type_to_method[type](limit=limit)
        posts = []
        for post in top_posts:
            posts.append({
                "subreddit": sub_name,
                "id": post.id,
                "titile": post.title,
                "author": post.author.name,
                "url": post.url,
                "score": post.score,
                "num_comments": post.num_comments,
                "created_at": post.created_utc
            })
        return posts
