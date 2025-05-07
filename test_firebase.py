import os
import sys

# 设置环境变量
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:\\Users\\user\\Documents\\program\\SBA\\ChineseBracketMaster\\firebase-key.json"

print(f"环境变量GOOGLE_APPLICATION_CREDENTIALS已设置为: {os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')}")

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    print('导入Firebase模块成功')
    
    # 初始化Firebase
    cred = credentials.Certificate(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'))
    print('读取凭证成功')
    
    firebase_admin.initialize_app(cred)
    print('初始化Firebase成功')
    
    db = firestore.client()
    print('Firebase连接成功!')
    
    # 尝试获取数据
    tournaments_ref = db.collection('tournaments')
    tournaments = tournaments_ref.get()
    print(f'获取到 {len(list(tournaments))} 个比赛数据')
    
    sys.exit(0)  # 成功退出
except Exception as e:
    print(f"错误: {e}")
    sys.exit(1)  # 失败退出