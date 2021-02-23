import pymongo

class MongoHandler:

    def __init__(self):
        #Constant fields and variables
        self.localhost = "127.0.0.1"
        self.database_name = "RedditRecommenderDatabase"
        self.collection_name = "user_subscriptions"
        self.port = 27017

        self.my_client = pymongo.MongoClient("mongodb://"+self.localhost+":"+str(self.port)+"/")
        self.database = None
        self.collection = None

    def create_database(self):
        dblist = self.my_client.list_database_names()
        if self.database_name not in dblist:
            self.database = self.my_client[self.database_name]
            self.create_collections()
        else:
            self.database = self.my_client[self.database_name]
            self.collection = self.database[self.collection_name]

    def create_collections(self):
        self.collection = self.database[self.collection_name]

    def insert_documents(self, username=None, c_list=None):
        self.collection = self.database[self.collection_name]
        if c_list is not None:
            subreddit_subscriptions = set()
            for comment in c_list:
                subreddit_subscriptions.add(comment.subreddit.display_name.lower())

            user_document = { "username":username, "subreddit_list":list(subreddit_subscriptions)}

            x = self.collection.insert_one(user_document)
        else:
            x = self.collection.insert_one({"none":None})

    def get_redditor_with_subscriptions(self, username):
        user = self.collection.find_one({'username': username})
        return user

    def get_all_subreddits(self):
        subreddits = set()
        cursor = self.collection.find({}, {"_id": 0, "username": 0})
        for document in cursor:
            for subreddit in document["subreddit_list"]:
                subreddits.add(subreddit)

        return subreddits

    def get_all_users(self):
        users = []
        cursor = self.collection.find({}, {"_id": 0, "subreddit_list": 0})
        for document in cursor:
            users.append(document["username"])

        return users

    def get_users_in_array(self, user_arr):
        return self.collection.find({'username': {"$in": user_arr}})

    def database_exists(self):
        dblist = self.my_client.list_database_names()
        if self.database_name in dblist:
            return True