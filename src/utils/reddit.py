import prawcore.exceptions
import praw


class RedditCrawler:
    def __init__(self, REDDIT_CLIENT_ID, REDDIT_SECRET) -> None:
        """
        Streaming context

        :return: Initial reddit instance
        """
        user_agent = 'example_user_agent'

        # Reddit instance, need username & password if crawl user's own data.
        self.reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_SECRET,
            user_agent=user_agent
        )

        print("Read-only Reddit instance:", self.reddit.read_only)
        print("---------")

    def check_subreddit(self, sub_name: str) -> bool:
        try:
            self.reddit.subreddits.search_by_name(sub_name, exact=True)
        except prawcore.exceptions.NotFound:
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
        posts_list = []
        for post in top_posts:
            posts_list.append({
                "subreddit": sub_name,
                "id": post.id,
                "title": post.title,
                "author": post.author.name,
                "url": post.url,
                "score": post.score,
                "up_votes": post.ups,
                "down_votes": post.downs,
                "num_comments": post.num_comments,
                "created_at": post.created_utc
            })
        return posts_list

    def stream_subreddit_comments(self, sub_name: str):
        """
        Streaming comments context: https://praw.readthedocs.io/en/stable/code_overview/other/subredditstream.html#praw.models.reddit.subreddit.SubredditStream.comments
        Comments are yielded oldest first. Up to 100 historical comments will initially be returned.

        Comment attribute: https://praw.readthedocs.io/en/stable/code_overview/models/comment.html
        :param sub_name:
        :return:
        """
        if not self.check_subreddit(sub_name):
            print(f"Subreddit {sub_name} not exist")
            return

        for comment in self.reddit.subreddit(sub_name).stream.comments():
            try:
                print("---- Start comments")
                print({
                    "subreddit": sub_name,
                    "author": {
                        "id": comment.author.id,
                        "name": comment.author.name,
                        "avatar": comment.author.icon_img
                    },
                    "body": comment.body,
                    "created_utc": comment.created_utc,
                    "submission_id": comment.submission.id
                })
            except prawcore.exceptions.PrawcoreException as e:
                print(e)
                pass

    def stream_subreddit_submission(self, sub_name: str):
        if not self.check_subreddit(sub_name):
            print(f"Subreddit {sub_name} not exist")
            return

        for submission in self.reddit.subreddit(sub_name).stream.submissions():
            try:
                print("---- Start submission")
                print({
                        "id": submission.id,
                        "author": {
                            "id": submission.author.id,
                            "name": submission.author.name,
                            "avatar": submission.author.icon_img
                    },
                        "name": submission.name,
                        "title": submission.title,
                        "url": submission.permalink,
                        "score": submission.score,
                        "num_comments": submission.num_comments
                    })
            except prawcore.exceptions.PrawcoreException as e:
                print(e)
                pass
