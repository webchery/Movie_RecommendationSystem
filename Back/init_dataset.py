import pandas as pd
import random
import os
from datetime import datetime
from app import app, db
from models import Movie, Rating, Client, Admin, Footprint
from werkzeug.security import generate_password_hash
import pymysql

# 🌟 数据库底层配置 (用于执行原生SQL补丁)
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "YOUR_PASSWORD",
    "database": "moviedb",
    "charset": "utf8mb4"
}


def init_all():
    """阶段一：全量数据初始化逻辑"""
    with app.app_context():
        print("1. [系统] 正在重建数据库表结构...")
        db.drop_all()
        db.create_all()

        # 1. 创建管理员和默认测试用户
        print("2. [用户] 正在初始化默认账号 (root/admin123)...")
        # 存入哈希密码用于登录，存入明文密码用于后台审计
        root_pass = "admin123"
        user_pass = "123456"
        root = Admin(username="root", password=generate_password_hash(root_pass))
        guest = Client(
            username="user01",
            password=generate_password_hash(user_pass),
            password_plain=user_pass  # 记录明文
        )
        db.session.add_all([root, guest])

        # 2. 导入电影数据
        path = r'F:\Projects\ZhangKKKKS\data\ml-100k'
        print(f"3. [电影] 正在从 {path} 读取电影元数据...")

        m_cols = ['id', 'title', 'rel_date', 'v_date', 'url'] + [f'g{i}' for i in range(19)]
        genres = ["unknown", "Action", "Adventure", "Animation", "Children's", "Comedy", "Crime", "Documentary",
                  "Drama", "Fantasy", "Film-Noir", "Horror", "Musical", "Mystery", "Romance", "Sci-Fi", "Thriller",
                  "War", "Western"]

        items = pd.read_csv(os.path.join(path, 'u.item'), sep='|', names=m_cols, encoding='latin-1')

        # 英文导演和演员池
        ENG_DIRS = ["Christopher Nolan", "Steven Spielberg", "James Cameron", "David Fincher", "Quentin Tarantino"]
        ENG_ACTS = ["Leonardo DiCaprio", "Tom Hanks", "Scarlett Johansson", "Brad Pitt", "Anne Hathaway"]

        for _, r in items.iterrows():
            # 🌟 确定性随机：根据电影ID固定随机种子
            random.seed(r['id'])
            gs = [genres[i] for i in range(19) if r[f'g{i}'] == 1]
            d, a = random.choice(ENG_DIRS), random.choice(ENG_ACTS)

            # 生成定制中文简介
            clean_name = r['title'].split(' (')[0]
            summary = f"这部名为《{clean_name}》的经典电影，通过精湛的视听语言展现了{gs[0] if gs else '剧情'}题材的独特魅力。导演{d}与主演{a}的倾力合作，使其成为了影史中不可磨灭的篇章。"

            try:
                rd = datetime.strptime(r['rel_date'], '%d-%b-%Y').date()
            except:
                rd = None

            db.session.add(Movie(
                id=r['id'], title=r['title'], director=d, actors=a,
                summary=summary, tags=",".join(gs), release_date=rd
            ))
        db.session.commit()

        # 3. 导入评分数据
        print("4. [评分] 正在同步 100,000 条评分记录 (请耐心等待)...")
        ratings = pd.read_csv(os.path.join(path, 'u.data'), sep='\t', names=['uid', 'mid', 'rating', 'ts'])
        objs = []
        for i, r in ratings.iterrows():
            objs.append(Rating(
                user_id=r['uid'], movie_id=r['mid'],
                rating=r['rating'], timestamp=datetime.fromtimestamp(r['ts'])
            ))
            if len(objs) >= 5000:
                db.session.bulk_save_objects(objs)
                db.session.commit()
                objs = []
        if objs:
            db.session.bulk_save_objects(objs)
            db.session.commit()

        # 4. 更新电影平均分
        print("5. [指标] 正在计算每部电影的平均评分...")
        avgs = ratings.groupby('mid')['rating'].mean()
        for mid, s in avgs.items():
            m = db.session.get(Movie, mid)
            if m: m.score = s
        db.session.commit()


def apply_database_patch():
    """阶段二：数据库结构补丁逻辑 (确保 password_plain 字段存在)"""
    print("6. [补丁] 正在检查 Client 表结构...")
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    try:
        # 尝试增加列 (如果是全新建表其实models里已经有了，这里作为二次保险)
        try:
            cursor.execute("ALTER TABLE client ADD COLUMN password_plain VARCHAR(255) AFTER password")
            conn.commit()
            print("✅ password_plain 字段添加成功！")
        except:
            print("💡 字段已存在，无需添加。")

        # 补全可能缺失的明文数据
        cursor.execute("UPDATE client SET password_plain = '123456' WHERE password_plain IS NULL")
        conn.commit()
        print("✅ 初始用户明文密码补全成功！")
    except Exception as e:
        print(f"❌ 补丁执行异常: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    # 按照顺序执行：重置导入 -> 结构校准
    init_all()
    apply_database_patch()
    print("\n" + "=" * 30)
    print("🎉 电影推荐系统数据初始化全部完成！")
    print("=" * 30)