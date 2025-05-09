# Application setup and configuration
import os
import logging
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# --- Firebase Initialization ---
# 嘗試多種方式初始化Firebase

# 1. 首先嘗試從環境變數獲取憑證路徑
cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

# 2. 如果環境變數未設置，嘗試在專案目錄中尋找憑證文件
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
            logging.info(f"Found Firebase credentials at: {cred_path}")
            break

# 3. 嘗試初始化Firebase
db_firestore = None  # 確保變數存在

# 如果找到憑證文件，使用憑證初始化
if cred_path:
    try:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        db_firestore = firestore.client()
        logging.info("Firebase Admin SDK initialized successfully with credentials.")
    except Exception as e:
        logging.error(f"Error initializing Firebase Admin SDK with credentials: {e}")
        # 如果使用憑證失敗，嘗試無憑證初始化
        try:
            if not firebase_admin._apps:
                firebase_admin.initialize_app()
            db_firestore = firestore.client()
            logging.info("Firebase Admin SDK initialized without explicit credentials after credential failure.")
        except Exception as e2:
            logging.error(f"Failed to initialize Firebase without credentials: {e2}")
else:
    # 如果沒有找到憑證，嘗試無憑證初始化（適用於Google Cloud環境）
    logging.warning("No Firebase credentials found. Attempting to initialize without credentials.")
    try:
        if not firebase_admin._apps:
            firebase_admin.initialize_app()
        db_firestore = firestore.client()
        logging.info("Firebase Admin SDK initialized without explicit credentials.")
    except Exception as e:
        logging.error(f"Error initializing Firebase Admin SDK without credentials: {e}")
        logging.error("請設定環境變數 GOOGLE_APPLICATION_CREDENTIALS 指向您的服務帳戶金鑰檔案")
        logging.error("或將憑證文件放在專案根目錄，命名為 firebase-credentials.json 或 firebase-key.json")


# Create the Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")
