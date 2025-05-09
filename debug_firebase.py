import os
import sys
import logging

# 設置日誌記錄
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# 顯示當前工作目錄
cwd = os.getcwd()
logging.info(f"當前工作目錄: {cwd}")

# 顯示環境變量
env_var = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
logging.info(f"環境變量 GOOGLE_APPLICATION_CREDENTIALS: {env_var}")

# 設置環境變量（如果尚未設置）
if not env_var:
    firebase_key_path = os.path.join(os.path.dirname(__file__), "firebase-key.json")
    if os.path.exists(firebase_key_path):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = firebase_key_path
        logging.info(f"已設置環境變量 GOOGLE_APPLICATION_CREDENTIALS: {firebase_key_path}")
    else:
        logging.error(f"找不到憑證文件: {firebase_key_path}")
        sys.exit(1)

try:
    logging.info("嘗試導入 firebase_admin 模組...")
    import firebase_admin
    from firebase_admin import credentials, firestore
    logging.info("成功導入 firebase_admin 模組")
    
    # 檢查是否已初始化
    if firebase_admin._apps:
        logging.info("Firebase 已經初始化")
        db = firestore.client()
        logging.info("成功獲取 Firestore 客戶端")
    else:
        # 嘗試使用憑證初始化
        logging.info("嘗試使用憑證初始化 Firebase...")
        cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        logging.info(f"使用憑證路徑: {cred_path}")
        
        try:
            cred = credentials.Certificate(cred_path)
            logging.info("成功讀取憑證")
            firebase_admin.initialize_app(cred)
            logging.info("成功初始化 Firebase")
            db = firestore.client()
            logging.info("成功獲取 Firestore 客戶端")
        except Exception as e:
            logging.error(f"使用憑證初始化失敗: {e}")
            logging.info("嘗試無憑證初始化...")
            try:
                firebase_admin.initialize_app()
                logging.info("成功無憑證初始化 Firebase")
                db = firestore.client()
                logging.info("成功獲取 Firestore 客戶端")
            except Exception as e2:
                logging.error(f"無憑證初始化也失敗: {e2}")
                sys.exit(1)
    
    # 測試獲取數據
    logging.info("嘗試獲取數據...")
    tournaments_ref = db.collection('tournaments')
    tournaments = tournaments_ref.get()
    logging.info(f"成功獲取 {len(list(tournaments))} 個比賽數據")
    
    # 測試獲取玩家數據
    logging.info("嘗試獲取玩家數據...")
    players_ref = db.collection('players')
    players = players_ref.get()
    logging.info(f"成功獲取 {len(list(players))} 個玩家數據")
    
    # 顯示所有集合
    logging.info("嘗試列出所有集合...")
    collections = db.collections()
    for collection in collections:
        logging.info(f"集合: {collection.id}")
    
    logging.info("Firebase 測試完成，一切正常！")
    sys.exit(0)
except Exception as e:
    logging.error(f"發生錯誤: {e}")
    import traceback
    logging.error(traceback.format_exc())
    sys.exit(1)