# Application setup and configuration
import os
import logging
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask
import sys
from logging.handlers import RotatingFileHandler

# 建立日誌目錄（如果不存在）
logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# 配置根記錄器
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)  # 全局級別設為 DEBUG

# 控制台處理器 - 處理 Windows 控制台編碼問題
try:
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
except UnicodeError:
    # 如果有編碼問題，使用僅限 ASCII 的格式
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    
    class AsciiStreamHandler(logging.StreamHandler):
        def emit(self, record):
            try:
                msg = self.format(record)
                # 轉換為 ASCII，替換無法表示的字符
                msg = msg.encode('ascii', 'replace').decode('ascii')
                stream = self.stream
                stream.write(msg + self.terminator)
                self.flush()
            except Exception:
                self.handleError(record)
    
    ascii_handler = AsciiStreamHandler(sys.stdout)
    ascii_handler.setLevel(logging.INFO)
    ascii_handler.setFormatter(console_formatter)
    root_logger.addHandler(ascii_handler)

# 文件處理器 - 一般日誌
file_handler = RotatingFileHandler(
    os.path.join(logs_dir, 'app.log'), 
    maxBytes=5*1024*1024,  # 5MB
    backupCount=10,
    encoding='utf-8'  # 明確指定UTF-8編碼
)
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

# 文件處理器 - 錯誤日誌
error_handler = RotatingFileHandler(
    os.path.join(logs_dir, 'error.log'), 
    maxBytes=5*1024*1024,  # 5MB
    backupCount=10,
    encoding='utf-8'  # 明確指定UTF-8編碼
)
error_handler.setLevel(logging.ERROR)
error_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s\n%(pathname)s:%(lineno)d\n%(message)s\n')
error_handler.setFormatter(error_formatter)

# 添加處理器到根記錄器
root_logger.addHandler(file_handler)
root_logger.addHandler(error_handler)

logging.info("Application started - log system configured")

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
