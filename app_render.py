# Application setup and configuration for Render deployment
import os
import json
import logging
import sys
import traceback
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask

import sys
sys.modules['app'] = sys.modules[__name__]

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# --- Firebase Initialization for Render ---
db_firestore = None  # 確保變數存在

# 1. 首先嘗試從環境變數獲取憑證JSON內容
cred_json = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_JSON")

if cred_json:
    try:
        logger.info("嘗試使用環境變數中的 JSON 憑證初始化 Firebase")
        # 將環境變數中的JSON字符串轉換為字典
        cred_dict = json.loads(cred_json)
        logger.debug(f"憑證 JSON 解析結果: {json.dumps(cred_dict, indent=2)[:100]}...")  # 只記錄前100個字符避免日誌過長
        
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
        db_firestore = firestore.client()
        logger.info("Firebase Admin SDK initialized successfully with credentials from environment variable.")
        
        # 測試連接
        try:
            collection_ref = db_firestore.collection('test_connection')
            logger.info(f"資料庫連接測試: 存取集合參考成功 - {collection_ref.path}")
        except Exception as e:
            logger.error(f"資料庫連接測試失敗: {e}")
            logger.error(traceback.format_exc())
            
    except json.JSONDecodeError as je:
        logger.error(f"JSON 解析錯誤: {je}")
        logger.error(f"JSON 字符串前100個字符: {cred_json[:100]}...")
        logger.error(traceback.format_exc())
    except Exception as e:
        logger.error(f"Error initializing Firebase Admin SDK with credentials from environment: {e}")
        logger.error(traceback.format_exc())
        # 如果使用環境變數憑證失敗，嘗試無憑證初始化
        try:
            if not firebase_admin._apps:
                firebase_admin.initialize_app()
            db_firestore = firestore.client()
            logger.info("Firebase Admin SDK initialized without explicit credentials after credential failure.")
        except Exception as e2:
            logger.error(f"Failed to initialize Firebase without credentials: {e2}")
            logger.error(traceback.format_exc())
else:
    # 2. 如果環境變數未設置，嘗試在專案目錄中尋找憑證文件
    cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    
    if not cred_path:
        possible_paths = [
            os.path.join(os.path.dirname(__file__), "firebase-credentials.json"),
            os.path.join(os.path.dirname(__file__), "instance", "firebase-credentials.json"),
            os.path.join(os.path.dirname(__file__), "firebase-key.json"),
            os.path.join(os.path.dirname(__file__), "instance", "firebase-key.json")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                cred_path = path
                logger.info(f"Found Firebase credentials at: {cred_path}")
                break
    
    # 如果找到憑證文件，使用憑證初始化
    if cred_path:
        try:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            db_firestore = firestore.client()
            logger.info("Firebase Admin SDK initialized successfully with credentials file.")
        except Exception as e:
            logger.error(f"Error initializing Firebase Admin SDK with credentials file: {e}")
            logger.error(traceback.format_exc())
            # 如果使用憑證失敗，嘗試無憑證初始化
            try:
                if not firebase_admin._apps:
                    firebase_admin.initialize_app()
                db_firestore = firestore.client()
                logger.info("Firebase Admin SDK initialized without explicit credentials after credential failure.")
            except Exception as e2:
                logger.error(f"Failed to initialize Firebase without credentials: {e2}")
                logger.error(traceback.format_exc())
    else:
        # 如果沒有找到憑證，嘗試無憑證初始化（適用於Google Cloud環境）
        logger.warning("No Firebase credentials found. Attempting to initialize without credentials.")
        try:
            if not firebase_admin._apps:
                firebase_admin.initialize_app()
            db_firestore = firestore.client()
            logger.info("Firebase Admin SDK initialized without explicit credentials.")
        except Exception as e:
            logger.error(f"Error initializing Firebase Admin SDK without credentials: {e}")
            logger.error(traceback.format_exc())
            logger.error("請設定環境變數 GOOGLE_APPLICATION_CREDENTIALS_JSON 包含您的服務帳戶金鑰JSON內容")
            logger.error("或設定環境變數 GOOGLE_APPLICATION_CREDENTIALS 指向您的服務帳戶金鑰檔案")
            logger.error("或將憑證文件放在專案根目錄，命名為 firebase-credentials.json 或 firebase-key.json")

# Check if database connection is available
if db_firestore is None:
    logger.critical("資料庫連接不可用。應用程式將無法正常運行。")
else:
    logger.info("資料庫連接成功建立！")

# Create the Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# 環境變數診斷
logger.info(f"環境變數診斷:")
logger.info(f"- GOOGLE_APPLICATION_CREDENTIALS 設置: {'是' if os.environ.get('GOOGLE_APPLICATION_CREDENTIALS') else '否'}")
logger.info(f"- GOOGLE_APPLICATION_CREDENTIALS_JSON 設置: {'是' if os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_JSON') else '否'}")
logger.info(f"- SESSION_SECRET 設置: {'是' if os.environ.get('SESSION_SECRET') else '否'}")
logger.info(f"- 工作目錄: {os.getcwd()}")
logger.info(f"- 目錄內容: {os.listdir('.')[:10]}")  # 只顯示前10個項目

import routes