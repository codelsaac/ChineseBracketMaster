# 安裝說明

本文件提供中國象棋比賽管理系統的詳細安裝指南。

## 必要套件

請確保您的系統已安裝以下套件：

- Python 3.9+
- pip (用於安裝 Python 套件)
- Node.js (用於前端套件管理)
- npm (可透過 Node.js 安裝)
- Firebase 帳戶 (用於數據存儲)

## 安裝步驟

### 1. 安裝 Python 包

```bash
pip install flask==2.2.3
pip install firebase-admin==6.2.0
pip install flask-login==0.6.2
pip install flask-wtf==1.1.1
pip install email-validator==2.0.0
pip install gunicorn==23.0.0
pip install weasyprint==59.0
```

### 2. 安裝 Node.js 套件

```bash
npm init -y
npm install confetti-js
npm install sortablejs
```

### 3. 設置 Firebase

1. 在 [Firebase 控制台](https://console.firebase.google.com/) 創建一個新項目
2. 在「專案設定」>「服務帳戶」中，生成新的私鑰
3. 下載生成的 JSON 檔案，並將其保存在安全的位置
4. 在 Firebase 控制台中創建 Firestore 數據庫

### 4. 設定環境變數

在啟動應用程式前設定 Firebase 憑證和會話密鑰：

在 Linux/Mac 上：

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your-firebase-adminsdk-key.json"
export SESSION_SECRET=your_secret_key_here
```

在 Windows 上：

```cmd
set GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\your-firebase-adminsdk-key.json
set SESSION_SECRET=your_secret_key_here
```

### 5. 啟動應用程式

開發環境：

```bash
python main.py
```

生產環境：

```bash
gunicorn --bind 0.0.0.0:5000 main:app
```

訪問 http://localhost:5000 來使用應用程式。

## 注意事項

1. 如果在安裝 WeasyPrint 時遇到問題，請查閱官方的[安裝指南](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html)，因為它可能需要額外的系統相關套件。

2. 在生產環境中，建議使用適當的 Web 伺服器（如 Nginx 或 Apache）來提供静態檔案並代理對 Gunicorn 的請求。

3. 請確保將 Firebase 憑證文件保存在安全的位置，且不要將其提交到公共代碼庫中。

4. 請定期備份您的 Firestore 數據。

5. 如果應用程式啟動時顯示「Database connection not available」錯誤，請檢查 GOOGLE_APPLICATION_CREDENTIALS 環境變數是否正確設置。
