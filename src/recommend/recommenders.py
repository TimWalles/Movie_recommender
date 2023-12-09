from src.utils.recommender_utils import RecommenderUtils


class Recommender(RecommenderUtils):
    def __init__(self, rating_data, rating_scale, links_data, item_model_path, user_model_path) -> None:
        self.links_data = links_data
        self.ratings = rating_data
        self.full_rating_data = RecommenderUtils.load_full_dataset(rating_data, rating_scale)
        self.item_algo = RecommenderUtils.load_surprise_model(item_model_path)
        self.user_algo = RecommenderUtils.load_surprise_model(user_model_path)

    def get_popular_movies(self, n_recommendations: int, **kwargs) -> list[int]:
        # Calculate average rating and number of ratings per movie and storing it in a dataframe
        movie_stats = self.ratings.groupby('movieId')['rating'].agg(['mean', 'count']).reset_index()

        C = movie_stats["mean"].mean()  # Mean rating across all movies
        m = 50  # Minimum number of ratings required (threshold) to be counted in the top (IMDb keeps 25000 currently for movies to be considered in top 250)

        # The IMDb popularity recommender formula
        weighted_rating = (movie_stats["mean"] * movie_stats["count"] + C * m) / (movie_stats["count"] + m)

        # adding 'weighted ratings' of each movie to the dataframe
        movie_stats["weighted_rating"] = weighted_rating

        # getting a list of top n movies based on the formula above
        top_pop_movie_ids = movie_stats.nlargest(n_recommendations * 2, columns="weighted_rating")["movieId"].tolist()
        return self.links_data.loc[self.links_data['movieId'].isin(top_pop_movie_ids), 'tmdbId'].values

    def get_similar_movies_recommended(self, n_recommendations: int, **kwargs):
        # Generate item-based recommendations for the given user
        user_unseen_movies = [mov_id for mov_id in self.full_rating_data.all_items() if mov_id not in self.full_rating_data.ur[kwargs['movie_id']]]
        item_predictions = [self.item_algo.predict(kwargs['movie_id'], mov_id) for mov_id in user_unseen_movies]
        return RecommenderUtils.get_recommended_movie_ids(item_predictions, n_recommendations, self.links_data)

    def get_user_recommended_movies(self, n_recommendations: int, **kwargs):
        # Generate predictions for the given user
        user_movies = self.ratings['movieId'].unique()
        user_unseen_movies = [
            movie_id for movie_id in user_movies if movie_id not in self.ratings[self.ratings['userId'] == kwargs['user_id']]['movieId'].unique()
        ]
        user_predictions = [self.user_algo.predict(kwargs['user_id'], movie_id) for movie_id in user_unseen_movies]
        return RecommenderUtils.get_recommended_movie_ids(user_predictions, n_recommendations, self.links_data)
