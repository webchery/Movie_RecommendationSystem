from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class Client(db.Model):
    __tablename__ = 'client'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)        # 存储加密哈希（用于登录校验）
    password_plain = db.Column(db.String(255), nullable=True)   # 核心修改：存储明文密码（用于管理员看）
    created_at = db.Column(db.DateTime, default=datetime.now)
    preferences = db.Column(db.String(255), nullable=True)
    # 关键：级联删除。删除用户时，该用户的足迹记录会自动被删除，防止外键冲突
    footprints = db.relationship('Footprint', backref='client', cascade="all, delete-orphan")
class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    tags = db.Column(db.String(255))
    director = db.Column(db.String(100))
    actors = db.Column(db.String(500))
    summary = db.Column(db.Text)
    score = db.Column(db.Float, default=0.0)
    click_count = db.Column(db.Integer, default=0)
    release_date = db.Column(db.Date)


    # 联表级联删除。删除电影时自动删除其评分和足迹。
    ratings = db.relationship('Rating', backref='movie', cascade="all, delete-orphan")
    footprints = db.relationship('Footprint', backref='movie', cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id, "title": self.title, "tags": self.tags or "剧情",
            "director": self.director or "未知", "actors": self.actors or "未知",
            "summary": self.summary or "暂无简介", "score": round(self.score or 0, 1),
            "click_count": self.click_count or 0,
            "release_date": self.release_date.isoformat() if self.release_date else "2024-01-01"
        }

class Footprint(db.Model):
    __tablename__ = 'footprint'
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'))
    timestamp = db.Column(db.DateTime, default=datetime.now)
    #movie = db.relationship('Movie')

class Rating(db.Model):
    __tablename__ = 'rating'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'))
    rating = db.Column(db.Float)
    timestamp = db.Column(db.DateTime)

