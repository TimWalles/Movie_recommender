import pathlib

import numpy as np
import pandas as pd
from PIL import Image
from st_click_detector import click_detector

import streamlit as st
from src.recommend.recommenders import Recommender
from src.service.tmdb_api import TheMovieDB
from src.streamlit.component_builder import StreamLitComponentBuilder

st.set_page_config(layout='wide')


# region data caching
# load rating data
@st.cache_data
def load_rating(file_path: pathlib.Path):
    return pd.read_csv(file_path)


# load links data
@st.cache_data
def load_links(file_path: pathlib.Path):
    return pd.read_csv(file_path)


# initialize api for getting movie posters
@st.cache_resource
def load_api():
    return TheMovieDB()


# initialize the various recommenders
@st.cache_resource
def load_recommender(
    rating_df: pd.DataFrame,
    rating_scale: tuple,
    links_df: pd.DataFrame,
    user_model_path: pathlib.Path,
    item_model_path: pathlib.Path,
):
    return Recommender(
        rating_data=rating_df,
        rating_scale=rating_scale,
        links_data=links_df,
        user_model_path=user_model_path,
        item_model_path=item_model_path,
    )


# initialize builder to make trackable movie poster grids
@st.cache_resource
def load_comp():
    return StreamLitComponentBuilder()


# movie poster grid builder
@st.cache_data  # note _recommender, the leading "_" instructs streamlit not to cache this parameter
def get_recommended_movie_poster(_recommender, n_recommendations: int, **kwargs):
    movie_ids = _recommender(n_recommendations=n_recommendations, **kwargs)
    return st_comp_builder.build_image_columns(movie_ids, n_recommendations)


# endregion


# region initialize streamlit caches
rating_df = load_rating(pathlib.Path('.', 'data', 'ratings.csv'))
links_df = load_links(pathlib.Path('.', 'data', 'links.csv'))
api = load_api()
st_comp_builder = load_comp()
recommender = load_recommender(
    rating_df=rating_df[['userId', 'movieId', 'rating']],
    rating_scale=(0.5, 5),
    links_df=links_df,
    user_model_path=pathlib.Path('.', 'models', 'sim_user_recommender_svd'),
    item_model_path=pathlib.Path('.', 'models', 'KNNBaseline_itembased_model'),
)
# endregion

### streamlit app ###
# region App header
banner_img = Image.open(pathlib.Path('.', 'images', 'wbsflix_banner.jpg'))
st.image(np.asarray(banner_img))
st.title('Welcome to :red[WBSFLIX] :sunglasses:')
# endregion

# region App side-bar
selected_user_id = st.sidebar.selectbox('select user id', rating_df['userId'].unique(), index=0, placeholder='Select user...')
logo_img = Image.open(pathlib.Path('.', 'images', 'tmdb_logo.png'))
st.sidebar.image(np.asarray(logo_img))
st.sidebar.write('This product uses the TMDB API but is not endorsed or certified by TMDB.')
# endregion

# region Movie posters
# region top10 popular movies
st.markdown('## Top 10 :red[popular] movies :film_frames:')
popular_movie_posters = get_recommended_movie_poster(_recommender=recommender.get_popular_movies, n_recommendations=10)
popular_movie_id_clicked = click_detector(popular_movie_posters)
if st.session_state.get('popular_movie_id_clicked') != popular_movie_id_clicked:
    st.session_state['popular_movie_id_clicked'] = st.session_state['similar_movie_id'] = popular_movie_id_clicked
# endregion


# region top10 popular movies for user
st.markdown('## Top 10 :red[recommended] for you! :popcorn:')
user_movie_posters = get_recommended_movie_poster(
    _recommender=recommender.get_user_recommended_movies,
    n_recommendations=10,
    user_id=selected_user_id,
)
user_movie_id_clicked = click_detector(user_movie_posters)
if st.session_state.get('user_movie_id_clicked') != user_movie_id_clicked:
    st.session_state['user_movie_id_clicked'] = st.session_state['similar_movie_id'] = user_movie_id_clicked
# endregion

# region similar movies
st.markdown('## similar :blue[popular] movies')
if st.session_state.get('similar_movie_id'):
    similar_movie_posters = get_recommended_movie_poster(
        _recommender=recommender.get_similar_movies_recommended,
        n_recommendations=10,
        movie_id=int(st.session_state['similar_movie_id']),
    )
    similar_movie_id_clicked = click_detector(similar_movie_posters)
# endregion


# endregion
