import pandas as pd
from surprise import Dataset, Reader, Trainset, dump


class RecommenderUtils:
    @classmethod
    def load_surprise_model(cls, model_path: str):
        _, loaded_model = dump.load(model_path)
        return loaded_model

    @classmethod
    def get_est(cls, prediction):
        return prediction.est

    @classmethod
    def load_full_dataset(cls, df: pd.DataFrame, rating_scale: tuple) -> Trainset:
        reader = Reader(rating_scale=rating_scale)
        data = Dataset.load_from_df(df, reader)
        return data.build_full_trainset()

    @classmethod
    def get_recommended_movie_ids(cls, recommendations: list, n_recommendations: int, links_data: pd.DataFrame) -> list[int]:
        top_movies = sorted(recommendations, key=RecommenderUtils.get_est, reverse=True)[: n_recommendations * 2]
        top_movie_ids = [movie_info.iid for movie_info in top_movies]
        return links_data.loc[links_data['movieId'].isin(top_movie_ids), 'tmdbId'].values
        # return [links_data.loc[links_data['movieId'] == movie_id, 'tmdbId'] for movie_id in top_movie_ids]
