import math
import operator

class RecommenderEngine:
    def __init__(self, mongo_handler, reddit_scraper):
        self.mongo_handler = mongo_handler
        self.user_vectors = []
        self.unique_subs = list(self.mongo_handler.get_all_subreddits())
        self.all_users = list(self.mongo_handler.get_all_users())
        self.reddit_scraper = reddit_scraper

    def create_user_vectors(self, username):
        user = self.mongo_handler.get_redditor_with_subscriptions(username)
        vectorized_subreddits_list = [0]*len(self.unique_subs)

        for i in range(len(self.unique_subs)):
            if self.unique_subs[i] in user['subreddit_list']:
                vectorized_subreddits_list[i] = 1

        return vectorized_subreddits_list


    def user_euclidean_distance(self, user_1, user_2):
        user_1_vector = self.create_user_vectors(user_1)
        user_2_vector = self.create_user_vectors(user_2)

        dist = 0
        for i in range(len(user_1_vector)):
            dist += pow(user_1_vector[i] - user_2_vector[i], 2)

        return math.sqrt(dist)

    def get_k_closest_neighbors(self, username, k):
        distances_array = []
        for user in self.all_users:
            dist = self.user_euclidean_distance(username, user)
            distances_array.append((user, dist))

        distances_array.sort(key=operator.itemgetter(1))
        return distances_array[:k]

    def get_recommended_subreddits(self, username):
        neighbor_usernames = []
        subreddit_frequency = {}
        if username not in self.mongo_handler.get_all_users():
            self.reddit_scraper.insert_specific_user(username)

        neighbors = self.get_k_closest_neighbors(username, 50)
        neighbor_cursor = self.mongo_handler.get_users_in_array([neighbor[0] for neighbor in neighbors])
        banned_cursor = self.mongo_handler.get_redditor_with_subscriptions(username)['subreddit_list']

        banned_cursor.append(self.reddit_scraper.SUBREDDIT_KEYS)

        total_subs = [sub for user in neighbor_cursor for sub in user['subreddit_list']]
        subreddit_frequency = {word: total_subs.count(word) for word in set(total_subs) if word not in banned_cursor}

        return sorted(subreddit_frequency, key=subreddit_frequency.get, reverse=True)[:10]