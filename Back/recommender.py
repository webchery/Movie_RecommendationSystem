import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from models import Movie, Rating, db


class RecommenderService:
    def __init__(self, db_instance):
        self.db = db_instance

    def get_personalized_rec(self, user_id, limit=12):
        # 如果未登录，返回热映榜
        if not user_id:
            return Movie.query.order_by(Movie.click_count.desc()).limit(limit).all()

        # 简单算法：根据用户最近看过的电影标签推荐
        from models import Footprint
        last_view = Footprint.query.filter_by(user_id=user_id).order_by(Footprint.timestamp.desc()).first()
        if not last_view:
            return Movie.query.order_by(db.func.rand()).limit(limit).all()

        main_tag = last_view.movie.tags.split(',')[0]
        return Movie.query.filter(Movie.tags.like(f'%{main_tag}%'), Movie.id != last_view.movie_id) \
            .order_by(Movie.score.desc()).limit(limit).all()

    def get_related_movies(self, movie_id, limit=6):
        # 基于内容的简单相似度：同导演或同标签
        target = Movie.query.get(movie_id)
        return Movie.query.filter(Movie.tags.like(f'%{target.tags.split(",")[0]}%'), Movie.id != movie_id) \
            .limit(limit).all()