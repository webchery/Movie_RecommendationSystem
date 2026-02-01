from flask import Flask, jsonify, request, session
from flask_cors import CORS
from models import db, Movie, Client, Admin, Footprint, Rating
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func
from datetime import datetime
from openai import OpenAI
import joblib,os

app = Flask(__name__)
# 允许跨域请求，并允许携带 Cookie (Session)
CORS(app, supports_credentials=True)
app.secret_key = 'cinema_secret_v10'
# 数据库连接配置
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/moviedb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


# ==========================================
# 1. AI 智能对话模块 (调用通义千问 API)
# ==========================================

@app.route('/api/ai/chat', methods=['POST'])
def ai_chat():
    """调用阿里云百炼 API 实现 AI 电影咨询"""
    try:
        user_msg = request.json.get('message')
        # 初始化 OpenAI 客户端
        client = OpenAI(
            api_key="YOUR_API-KEY",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        # 调用模型生成对话
        completion = client.chat.completions.create(
            model="qwen-plus",
            messages=[
                {"role": "system", "content": "你是一个电影专家，请简洁地回答用户关于电影的问题。"},
                {"role": "user", "content": user_msg},
            ]
        )
        # 提取并返回 AI 的文本回复
        ai_reply = completion.choices[0].message.content
        return jsonify({"reply": ai_reply})

    except Exception as e:
        print(f"AI Error: {e}")
        return jsonify({"reply": "抱歉，我现在的思维有点混乱，请稍后再试。"}), 500


# ==========================================
# 2. 用户身份认证模块 (Client 用户)
# ==========================================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """用户注册：同时存入加密哈希和明文密码"""
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"msg": "账号密码不能为空"}), 400

    if Client.query.filter_by(username=username).first():
        return jsonify({"msg": "用户名已存在"}), 400

    # 创建新客户：password用于验证，password_plain用于管理员查看
    new_c = Client(
        username=username,
        password=generate_password_hash(password),
        password_plain=password
    )
    db.session.add(new_c)
    db.session.commit()
    return jsonify({"msg": "注册成功，请登录"})


@app.route('/api/auth/login', methods=['POST'])
def login():
    """统一登录入口：支持普通用户(client)和管理员(admin)角色"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')

    # 根据角色选择查询的表
    if role == 'admin':
        user = Admin.query.filter_by(username=username).first()
        s_key = 'admin_id'
    else:
        user = Client.query.filter_by(username=username).first()
        s_key = 'client_id'

    # 校验密码哈希
    if user and check_password_hash(user.password, password):
        session.clear()  # 登录前清理旧 Session
        session[s_key] = user.id
        return jsonify({"msg": "登录成功", "role": role, "username": user.username})

    return jsonify({"msg": "账号或密码错误"}), 401


@app.route('/api/auth/user_info')
def user_info():
    """检查当前登录状态，返回用户信息"""
    if 'admin_id' in session:
        u = db.session.get(Admin, session['admin_id'])
        return jsonify({"isLogin": True, "role": "admin", "username": u.username})
    if 'client_id' in session:
        u = db.session.get(Client, session['client_id'])
        return jsonify({"isLogin": True, "role": "client", "username": u.username})
    return jsonify({"isLogin": False})

# --- 兴趣偏好保存接口 ---
@app.route('/api/auth/preferences', methods=['POST'])
def save_preferences():
    cid = session.get('client_id')
    if not cid: return jsonify({"msg": "未登录"}), 401
    tags = request.json.get('tags', '')
    client = db.session.get(Client, cid)
    if client:
        client.preferences = tags
        db.session.commit()
    return jsonify({"msg": "偏好设置成功"})

@app.route('/api/auth/logout')
def logout():
    """注销登录，清空 Session"""
    session.clear()
    return jsonify({"msg": "OK"})


# ==========================================
# 3. 电影核心业务模块 (查询、详情、足迹)
# ==========================================

# @app.route('/api/movies/home')
# def home_data():
#     """获取首页推荐：包含随机推荐和热门推荐"""
#     recs = Movie.query.order_by(func.rand()).limit(12).all()
#     hots = Movie.query.order_by(Movie.click_count.desc()).limit(12).all()
#     return jsonify({
#         "recs": [m.to_dict() for m in recs],
#         "hots": [m.to_dict() for m in hots]
#     })

# --- 首页“为你推荐” ---
MODEL_PATH = r'F:\Projects\ZhangKKKKS\Back\trained_models.pkl'
MODEL = joblib.load(MODEL_PATH)
# @app.route('/api/movies/home')
# def home_data():
#     is_logged_in = 'client_id' in session
#
#     if is_logged_in and MODEL:
#         # 逻辑 A：登录用户使用模型文件进行个性化推荐
#         # 获取用户最后一项足迹
#         from models import Footprint
#         last_foot = Footprint.query.filter_by(client_id=session['client_id']).order_by(Footprint.id.desc()).first()
#
#         if last_foot and last_foot.movie_id in MODEL['indices']:
#             idx = MODEL['indices'][last_foot.movie_id]
#             # 从模型相似度矩阵中提取最相似的
#             sim_scores = list(
#                 enumerate(MODEL['item_cf_sim'][idx] if idx < len(MODEL['item_cf_sim']) else MODEL['content_sim'][idx]))
#             sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:13]
#             recs_ids = [MODEL['movie_ids'][i] for i, score in sim_scores]
#             recs_raw = Movie.query.filter(Movie.id.in_(recs_ids)).all()
#         else:
#             recs_raw = Movie.query.order_by(func.rand()).limit(12).all()
#     else:
#         # 逻辑 B：未登录用户使用普通静态信息推荐
#         recs_raw = Movie.query.order_by(func.rand()).limit(12).all()
#
#     return jsonify({"recs": [m.to_dict() for m in recs_raw]})
# --- 混合推荐首页接口 (模型+标签)  ---
@app.route('/api/movies/home')
def home_data():
    cid = session.get('client_id')
    recs_raw = []

    if cid:
        client = db.session.get(Client, cid)
        last_view = Footprint.query.filter_by(client_id=cid).order_by(Footprint.id.desc()).first()

        # 1. 优先逻辑：有历史足迹，基于模型文件进行 Item-CF 推荐
        if last_view and MODEL and last_view.movie_id in MODEL['indices']:
            idx = MODEL['indices'][last_view.movie_id]
            sim_scores = list(enumerate(MODEL['item_cf_sim'][idx]))
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:13]
            recs_ids = [MODEL['movie_ids'][i] for i, _ in sim_scores]
            recs_raw = Movie.query.filter(Movie.id.in_(recs_ids)).all()

        # 2. 次优逻辑：没看过电影但选了标签，根据标签从库中筛选高分电影
        elif client and client.preferences:
            pref_list = client.preferences.split(',')
            recs_raw = Movie.query.filter(
                func.or_(*[Movie.tags.like(f'%{t}%') for t in pref_list])
            ).order_by(Movie.score.desc()).limit(12).all()

    # 3. 游客逻辑：随机推荐
    if not recs_raw:
        recs_raw = Movie.query.order_by(func.rand()).limit(12).all()

    # 强制列表去重并返回
    unique_recs = {m.id: m for m in recs_raw}
    return jsonify({"recs": [m.to_dict() for m in list(unique_recs.values())]})

# @app.route('/api/movies/detail/<int:mid>')
# def movie_detail(mid):
#     """获取电影详情，并记录用户足迹"""
#     m = Movie.query.get_or_404(mid)
#     m.click_count += 1  # 增加点击量
#
#     # 如果用户已登录，则记录到 footprint 表
#     if 'client_id' in session:
#         db.session.add(Footprint(client_id=session['client_id'], movie_id=mid))
#
#     db.session.commit()
#     res = m.to_dict()
#
#     # 相似推荐逻辑：查找具有相同主标签的电影
#     tag = m.tags.split(',')[0] if m.tags else ""
#     rel = Movie.query.filter(Movie.tags.like(f'%{tag}%'), Movie.id != mid).limit(6).all()
#     res['related'] = [r.to_dict() for r in rel]
#     return jsonify(res)
# --- 详情页“猜你喜欢” ---
@app.route('/api/movies/detail/<int:mid>')
def movie_detail(mid):
    m = Movie.query.get_or_404(mid)
    m.click_count += 1

    is_logged_in = 'client_id' in session
    if is_logged_in:
        db.session.add(Footprint(client_id=session['client_id'], movie_id=mid))
    db.session.commit()

    related_movies = []
    # 逻辑：只有登录用户能触发模型计算的“猜你喜欢”
    if is_logged_in and MODEL and mid in MODEL['indices']:
        idx = MODEL['indices'][mid]
        sim_scores = list(enumerate(MODEL['content_sim'][idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:7]
        for i, score in sim_scores:
            rid = MODEL['movie_ids'][i]
            rm = db.session.get(Movie, rid)
            if rm: related_movies.append(rm.to_dict())
    else:
        # 逻辑：未登录用户仅展示同标签的静态信息
        tag = m.tags.split(',')[0] if m.tags else ""
        rel = Movie.query.filter(Movie.tags.like(f'%{tag}%'), Movie.id != mid).limit(6).all()
        related_movies = [r.to_dict() for r in rel]

    res = m.to_dict()
    res['related'] = related_movies
    return jsonify(res)

@app.route('/api/user/footprints')
def get_footprints():
    """获取当前登录用户的最近观看历史记录"""
    cid = session.get('client_id')
    if not cid: return jsonify([])

    # 获取最近12条足迹并去重
    logs = Footprint.query.filter_by(client_id=cid).order_by(Footprint.id.desc()).limit(12).all()
    seen, data = set(), []
    for l in logs:
        if l.movie_id not in seen:
            data.append(l.movie.to_dict())
            seen.add(l.movie_id)
    return jsonify(data)


# ==========================================
# 4. 搜索与榜单模块 (多维度过滤)
# ==========================================

@app.route('/api/movies/search')
def search_movies():
    """多维度搜索：支持片名、导演、演员、标签"""
    keyword = request.args.get('q', '')
    stype = request.args.get('type', 'title')
    if not keyword: return jsonify([])

    query = Movie.query
    if stype == 'director':
        results = query.filter(Movie.director.like(f'%{keyword}%'))
    elif stype == 'actors':
        results = query.filter(Movie.actors.like(f'%{keyword}%'))
    elif stype == 'tags':
        results = query.filter(Movie.tags.like(f'%{keyword}%'))
    else:
        results = query.filter(Movie.title.like(f'%{keyword}%'))

    res = results.order_by(Movie.score.desc()).limit(30).all()
    return jsonify([m.to_dict() for m in res])


@app.route('/api/movies/rankings')
def get_rankings():
    """排行榜接口：支持新片榜(按时间)和热映榜(按热度)"""
    list_type = request.args.get('type', 'hot')
    sort_by = request.args.get('sort', 'clicks')
    min_score = request.args.get('min_score', 0, type=float)

    query = Movie.query.filter(Movie.score >= min_score)

    if list_type == 'new':
        results = query.order_by(Movie.release_date.desc()).limit(30).all()
    else:
        if sort_by == 'score':
            results = query.order_by(Movie.score.desc()).limit(30).all()
        else:
            results = query.order_by(Movie.click_count.desc()).limit(30).all()

    return jsonify([m.to_dict() for m in results])


# ==========================================
# 5. 管理员后台模块 (数据管理与审计)
# ==========================================

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    """管理员专用登录验证"""
    data = request.json
    u = Admin.query.filter_by(username=data['username']).first()
    if u and check_password_hash(u.password, data['password']):
        session.clear()
        session['admin_id'] = u.id
        return jsonify({"msg": "管理员认证成功", "username": u.username})
    return jsonify({"msg": "管理员账号或密码错误"}), 401


# @app.route('/api/admin/stats')
# def get_admin_stats():
#     """后台仪表盘：统计电影、用户及播放总量"""
#     movie_count = Movie.query.count()
#     client_count = Client.query.count()
#     total_clicks = db.session.query(func.sum(Movie.click_count)).scalar() or 0
#     ctr = f"{round((total_clicks / (movie_count * 10)), 2)}%" if movie_count > 0 else "0%"
#     return jsonify({
#         "movie_count": movie_count,
#         "client_count": client_count,
#         "total_clicks": total_clicks,
#         "ctr": ctr,
#         "algo_status": "ItemCF + Content-Based (Active)"
#     })
@app.route('/api/admin/stats')
def get_admin_stats():
    """获取管理后台统计数据，带模型指标"""
    try:
        # 1. 实时统计
        movie_count = Movie.query.count()
        client_count = Client.query.count()
        total_clicks = db.session.query(func.sum(Movie.click_count)).scalar() or 0

        # 2. 读取模型指标 (从全局变量 MODEL 中读取)
        # 确保你在 app.py 顶部已经执行了 MODEL = joblib.load(MODEL_PATH)
        rmse = "N/A"
        precision = "N/A"

        # 重新加载一次模型文件确保数据最新
        if os.path.exists(MODEL_PATH):
            temp_model = joblib.load(MODEL_PATH)
            if 'metrics' in temp_model:
                rmse = temp_model['metrics'].get('rmse', "N/A")
                precision = temp_model['metrics'].get('precision', "N/A")

        return jsonify({
            "movie_count": movie_count,
            "client_count": client_count,
            "total_clicks": int(total_clicks),
            "rmse": rmse,
            "precision": precision
        })
    except Exception as e:
        print(f"Stats Error: {e}")
        return jsonify({"error": "获取统计失败"}), 500

@app.route('/api/admin/movies', methods=['GET', 'POST'])
def admin_manage_movies():
    """管理员管理电影：查看列表或新增电影"""
    if request.method == 'GET':
        movies = Movie.query.order_by(Movie.id.desc()).all()
        return jsonify({"items": [m.to_dict() for m in movies]})

    if request.method == 'POST':
        data = request.json
        new_m = Movie(
            title=data.get('title'),
            director=data.get('director', 'Unknown'),
            actors=data.get('actors', 'Unknown'),
            tags=data.get('tags', 'Drama'),
            summary=data.get('summary', 'No summary.'),
            score=0.0,
            release_date=datetime.now().date()
        )
        db.session.add(new_m)
        db.session.commit()
        return jsonify({"msg": "影片添加成功！"})


@app.route('/api/admin/movies/<int:mid>', methods=['PUT', 'DELETE'])
def admin_movie_ops(mid):
    """管理员操作：修改或删除特定电影 (支持级联删除)"""
    movie = db.session.get(Movie, mid)
    if not movie: return jsonify({"msg": "影片不存在"}), 404

    if request.method == 'PUT':
        data = request.json
        movie.title = data.get('title', movie.title)
        movie.director = data.get('director', movie.director)
        movie.actors = data.get('actors', movie.actors)
        movie.tags = data.get('tags', movie.tags)
        movie.summary = data.get('summary', movie.summary)
        db.session.commit()
        return jsonify({"msg": "修改成功"})

    if request.method == 'DELETE':
        db.session.delete(movie)
        db.session.commit()
        return jsonify({"msg": "删除成功"})


# ---  管理员用户管理接口  ---
@app.route('/api/admin/clients', methods=['GET', 'POST'])
def admin_manage_clients():
    if request.method == 'GET':
        cls = Client.query.all()
        return jsonify([{
            "id": c.id,
            "username": c.username,
            "password": c.password_plain,
            "date": c.created_at.strftime('%Y-%m-%d')
        } for c in cls])

    if request.method == 'POST':
        data = request.json
        username = data.get('username')
        password = data.get('password')

        if Client.query.filter_by(username=username).first():
            return jsonify({"msg": "该用户名已存在"}), 400

        # 管理员开户：同时存入哈希和明文
        new_c = Client(
            username=username,
            password=generate_password_hash(password),
            password_plain=password
        )
        db.session.add(new_c)
        db.session.commit()
        return jsonify({"msg": "新用户创建成功"})


@app.route('/api/admin/clients/<int:cid>', methods=['DELETE'])
def admin_delete_client(cid):
    client = db.session.get(Client, cid)
    if not client:
        return jsonify({"msg": "用户不存在"}), 404

    db.session.delete(client)
    db.session.commit()  # 触发级联删除足迹
    return jsonify({"msg": "用户及其数据已永久删除"})


# ==========================================
# 6. 程序启动入口
# ==========================================

if __name__ == '__main__':
    app.run(debug=True, port=5000)
