import pandas as pd
import numpy as np
import os
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from datetime import datetime
from app import app, db
from models import Movie, Rating

# 指定保存路径
MODEL_PATH = r'F:\Projects\ZhangKKKKS\Back\trained_models.pkl'


def process_recommender():
    with app.app_context():
        print("1. [数据提取] 正在从数据库加载数据...")
        ratings_df = pd.read_sql("SELECT user_id, movie_id, rating FROM rating", db.engine)
        movies = Movie.query.all()

        if ratings_df.empty:
            print("错误：数据库中没有评分数据！")
            return

        # 2. [数据拆分] 80% 训练模型，20% 留作评估
        train_df, test_df = train_test_split(ratings_df, test_size=0.2, random_state=42)

        # 3. [模型训练] 内容相似度
        print("2. [模型训练] 正在计算电影特征矩阵...")
        movie_data = [{'id': m.id, 'text': f"{m.tags} {m.director} {m.actors} {m.summary}"} for m in movies]
        df_content = pd.DataFrame(movie_data)
        tfidf = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf.fit_transform(df_content['text'])
        content_sim = cosine_similarity(tfidf_matrix)

        # 4. [模型训练] 协同过滤
        user_item_matrix = train_df.pivot_table(index='user_id', columns='movie_id', values='rating').fillna(0)
        item_cf_sim = cosine_similarity(user_item_matrix.T)

        # 5. [核心：模型评估] 针对 20% 测试集计算指标
        print("3. [模型评估] 正在计算 RMSE 和准确率...")
        movie_means = train_df.groupby('movie_id')['rating'].mean()
        global_mean = train_df['rating'].mean()

        y_true = test_df['rating']
        y_pred = test_df['movie_id'].map(movie_means).fillna(global_mean)

        # 计算 RMSE (均方根误差)
        rmse_val = np.sqrt(mean_squared_error(y_true, y_pred))
        # 计算 准确率 (分差小于1.0即为命中)
        precision_val = (np.abs(y_true - y_pred) <= 1.0).sum() / len(test_df)

        # 6. [全量打包]
        print(f"4. [保存] 正在存入文件: {MODEL_PATH}")
        model_pack = {
            'content_sim': content_sim,
            'item_cf_sim': item_cf_sim,
            'movie_ids': df_content['id'].tolist(),
            'indices': pd.Series(df_content.index, index=df_content['id']).to_dict(),
            'item_ids': user_item_matrix.columns.tolist(),
            # 这一块必须存进去，否则前端就是 N/A
            'metrics': {
                'rmse': round(float(rmse_val), 4),
                'precision': f"{round(float(precision_val) * 100, 2)}%",
                'eval_date': datetime.now().strftime('%Y-%m-%d %H:%M')
            }
        }
        joblib.dump(model_pack, MODEL_PATH)
        print(f"🎉 训练完成！RMSE: {model_pack['metrics']['rmse']}, 准确率: {model_pack['metrics']['precision']}")


if __name__ == "__main__":
    process_recommender()