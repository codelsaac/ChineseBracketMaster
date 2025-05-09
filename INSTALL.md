# 安裝與使用指南

本文件提供中國象棋比賽管理系統的詳細安裝、部署、運行和使用指南。

## 先決條件

請確保您的系統已安裝以下套件：

- Python 3.9+
- pip (用於安裝 Python 套件)
- Node.js (用於前端套件管理)
- npm (可透過 Node.js 安裝)
- Firebase 帳戶和專案 (用於數據存儲)
- Git (用於克隆代碼庫)

## 安裝步驟

1.  **克隆代碼庫**
    ```bash
    git clone [儲存庫URL] # 請替換為實際的儲存庫 URL
    cd chinese-chess-tournament # 進入項目目錄
    ```

2.  **設置Python虛擬環境** (推薦)
    ```bash
    python -m venv venv
    # 在 Linux/Mac 上激活:
    # source venv/bin/activate
    # 在 Windows 上激活:
    venv\Scripts\activate
    ```

3.  **安裝後端依賴 (Python)**
    ```bash
    # 確保您在 ChineseBracketMaster 目錄中
    # 如果您在 SBA 目錄，請使用以下命令：
    # cd ChineseBracketMaster
    # 或者指定完整路徑：
    # pip install -r ChineseBracketMaster\requirements.txt
    
    pip install -r requirements.txt
    # 這將安裝所有必要的依賴項，包括：
    # flask, flask-babel, flask-login, flask-wtf, email-validator, firebase-admin, 
    # python-dotenv, werkzeug, gunicorn, weasyprint, html2image, google-cloud-firestore
    ```

4.  **安裝前端依賴 (Node.js)**
    ```bash
    # 如果項目根目錄下沒有 package.json 文件，先初始化
    # npm init -y
    npm install confetti-js sortablejs
    ```

5.  **設置 Firebase**
    1.  在 [Firebase 控制台](https://console.firebase.google.com/) 創建一個新項目。
    2.  在「專案設定」>「服務帳戶」中，生成新的私鑰。
    3.  下載生成的 JSON 檔案 (例如 `your-firebase-adminsdk-key.json`)，並將其保存在安全的位置（例如項目根目錄，但**不要**提交到 Git）。
    4.  在 Firebase 控制台中創建 Firestore 數據庫。

6.  **設定環境變數**
    在啟動應用程式前設定 Firebase 憑證路徑和會話密鑰。將下載的 JSON 文件路徑替換掉 `/path/to/your-firebase-adminsdk-key.json` 或 `C:\path\to\your-firebase-adminsdk-key.json`。

    在 Linux/Mac 上：
    ```bash
    export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your-firebase-adminsdk-key.json"
    export SESSION_SECRET="your_secret_key_here" # 替換為一個隨機的安全密鑰
    ```

    在 Windows (CMD) 上：
    ```cmd
    set GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\your-firebase-adminsdk-key.json
    set SESSION_SECRET=your_secret_key_here
    ```
    (注意：`set` 命令只在當前命令提示符窗口有效。你可能需要將其設置為系統環境變數。)

## 運行應用程式

1.  **啟動應用程式**

    開發模式 (帶調試信息):
    ```bash
    python main.py
    ```

    生產環境 (推薦使用 Gunicorn，僅限 Linux/Mac):
    ```bash
    gunicorn --bind 0.0.0.0:5000 main:app
    ```

2.  **訪問應用程式**
    打開瀏覽器並訪問 http://localhost:5000 (或你配置的地址和端口)。

## 使用說明

1.  **創建賽事**：在首頁點擊「新增賽事」按鈕，輸入賽事名稱和日期。
2.  **管理選手**：進入賽事頁面後，點擊「管理選手」。在此頁面可以添加新選手（姓名、學校、是否種子選手）、編輯現有選手信息或刪除選手。
3.  **生成賽程表**：當選手數量達到至少2人時，在「管理選手」頁面點擊「生成賽程表」按鈕。如果賽程已生成，此按鈕會變為「重新生成賽程表」。
4.  **記錄比賽結果**：在賽程表頁面，點擊對戰卡片中獲勝選手的姓名來記錄比賽結果。系統會自動將獲勝者晉級到下一輪。
5.  **導出賽程表**：在賽程表頁面，使用「導出」按鈕旁邊的下拉菜單選擇導出為 PDF 或圖片格式。

## 注意事項

1.  如果在安裝 WeasyPrint 時遇到問題，請查閱其官方的[安裝指南](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html)，因為它可能需要額外的系統相關依賴（如 Pango, Cairo, GDK-PixBuf）。
2.  在生產環境中，建議使用更健壯的 Web 伺服器（如 Nginx 或 Apache）來反向代理對 Gunicorn (或 Flask 開發伺服器) 的請求，並處理靜態文件。
3.  請確保將 Firebase 憑證文件保存在安全的位置，**絕對不要**將其提交到公共代碼庫（例如 Git）。建議將其添加到 `.gitignore` 文件中。
4.  請定期備份您的 Firestore 數據。
5.  如果應用程式啟動時顯示與數據庫連接相關的錯誤（例如 "Database connection not available"），請仔細檢查 `GOOGLE_APPLICATION_CREDENTIALS` 環境變數是否已正確設置，並且指向有效的憑證文件。
