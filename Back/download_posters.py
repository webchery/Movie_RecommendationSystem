import os
import pandas as pd
import requests

# 1. 确保文件夹存在
save_path = r'F:\Projects\ZhangKKKKS\Front\public\images'
if not os.path.exists(save_path):
    os.makedirs(save_path)

# 2. 从 babu-thomas 仓库获取海报链接列表 (CSV格式)
# 这是一个公开维护的列表，直接对应 MovieLens 100k ID
csv_url = "https://raw.githubusercontent.com/babu-thomas/movielens-posters/master/movie_poster.csv"

print("正在获取海报链接清单...")
try:
    df = pd.read_csv(csv_url, names=['id', 'url'])

    print(f"找到 {len(df)} 条记录，开始下载...")

    for index, row in df.iterrows():
        movie_id = row['id']
        img_url = row['url']

        # 排除掉没有链接的情况
        if pd.isna(img_url) or str(img_url).strip() == "":
            continue

        target_file = os.path.join(save_path, f"{movie_id}.jpg")

        if os.path.exists(target_file):
            continue

        try:
            # 下载图片
            r = requests.get(img_url, timeout=10)
            if r.status_code == 200:
                with open(target_file, 'wb') as f:
                    f.write(r.content)
                print(f"✅ 成功下载电影 ID: {movie_id}")
            else:
                print(f"❌ 链接失效 ID: {movie_id}")
        except:
            print(f"⚠️ 网络波动，跳过 ID: {movie_id}")

    print("下载任务已完成！")

except Exception as e:
    print(f"错误: 无法连接到海报数据库清单 ({e})")