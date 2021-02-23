import praw
from MongoHandler import MongoHandler
from prawcore.exceptions import Forbidden
from prawcore.exceptions import NotFound


'''
    Leverage the PRAW library to get a list of 100 of the most recent commenters from all. 
    Make sure they're all unique and if there aren't grab more comments till I have 100
    unique users. Use that list of users to generate the database. 
'''
class RedditScraper:

    def __init__(self, user_agent, client_id, client_secret, username=None, password=None):
        self.users_set = set()
        self.SUBREDDIT_KEYS = ["all", "gaming", "amitheasshole", "relationships", "pics", "guns", "foodporn", "formula1", "denver"]

        self.user_agent = user_agent
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password

        self.reddit = None
        self.mongo_handler = MongoHandler()
        self.mongo_handler.create_database()

    def create_reddit_object(self):
        self.reddit = praw.Reddit(
            user_agent=self.user_agent,
            client_id=self.client_id,
            client_secret=self.client_secret,
            username=self.username,
            password=self.password
        )

    def get_comments_and_users(self):
        for sub in self.SUBREDDIT_KEYS:
            count = 0
            subreddit = self.reddit.subreddit(sub)
            hot_data = subreddit.hot(limit = 100)

            for submission in hot_data:
                submission.comments.replace_more(limit=0)
                for top_level_comment in submission.comments:
                    self.users_set.add(top_level_comment.author)
                    count += 1
                    if count >= 100:
                        break
                if count >= 100:
                    break

            print("Subreddit: " + sub + " - " + str(len(self.users_set)))

    def get_users_set(self):
        return self.users_set

    def get_user_subreddits(self):
        for redditor in self.get_users_set():
            if redditor is None:
                continue
            else:
                try:
                    comments_list = list(redditor.comments.new(limit=100))
                    self.mongo_handler.insert_documents(redditor.name, comments_list)
                    print("Redditor: " + redditor.name + " has been inserted into the database")
                except Forbidden or NotFound:
                    print("Slight error while getting Redditor " + redditor.name + "'s comment information")

    def insert_specific_user(self, username):
        redditor = self.reddit.redditor(username)
        comments_list = list(redditor.comments.new(limit=100))
        self.mongo_handler.insert_documents(redditor.name, comments_list)

    def collate_subreddits(self):
        self.mongo_handler.get_all_subreddits()