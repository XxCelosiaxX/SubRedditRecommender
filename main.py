from RedditScraper import RedditScraper
from RecommenderEngine import RecommenderEngine



def main():
    user_agent = "RedditRecommender1000 Bot - Created By InnovAsians and XxCelosiaxX"
    client_id = "7JTsizc90yilcw"
    client_secret = "CVOdCezPKgAUcm4PbPGcqmRjBdDpIw"

    rs = RedditScraper(user_agent, client_id, client_secret)
    rs.create_reddit_object()
    re = RecommenderEngine(rs.mongo_handler, rs)

    while(True):
        print("Options Menu:")
        print("1: Reload Data Into MongoDB")
        print("2: Get a recommendation for a user")
        x = input("Enter your choice: ")
        if x is "1":
            rs.get_comments_and_users()
            rs.get_user_subreddits()
            re = RecommenderEngine(rs.mongo_handler, rs)
        elif x is "2":
            if rs.mongo_handler.database_exists():
                username = input("Enter a username: ")
                print(re.get_recommended_subreddits(username))
            else:
                print("Please load in the data first before trying to get recommendations...")

if __name__ == "__main__":
    main()
