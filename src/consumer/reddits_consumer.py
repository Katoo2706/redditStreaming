from reddit import RedditCrawler


print(RedditCrawler().get_subreddit("test", type='new', limit=10))
