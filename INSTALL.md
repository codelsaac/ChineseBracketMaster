# 安裝說明

本文件提供中國象棋比賽管理系統的詳細安裝指南。

## 必要套件

請確保您的系統已安裝以下套件：

- Python 3.9+
- PostgreSQL 資料庫
- pip (用於安裝 Python 套件)
- Node.js (用於前端套件管理)
- npm (可透過 Node.js 安裝)

## 安裝步骨

### 1. 安裝 Python 包

```bash
pip install flask==2.2.3
pip install flask-sqlalchemy==3.0.3
pip install flask-login==0.6.2
pip install flask-wtf==1.1.1
pip install sqlalchemy==2.0.7
pip install psycopg2-binary==2.9.5
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

### 3. 創建資料庫

在 PostgreSQL 中創建新的資料庫：

```bash
# 使用 PostgreSQL 命令列工具
psql -U postgres
```

在 PostgreSQL shell 中：

```sql
CREATE DATABASE chess_tournament;
CREATE USER chess_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE chess_tournament TO chess_user;
```

### 4. 設定環境變數

在啟動應用程式前設定資料庫 URL 設定：

在 Linux/Mac 上：

```bash
export DATABASE_URL=postgresql://chess_user:your_password@localhost/chess_tournament
export SESSION_SECRET=your_secret_key_here
```

在 Windows 上：

```cmd
set DATABASE_URL=postgresql://chess_user:your_password@localhost/chess_tournament
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

2. 在生產環境中，建議使用適當的 Web 伺服器（如 Nginx 或 Apache）來提供静態檔案並代理對 Gunicorn 的諏問。

3. 請確保將所有檔案和資料區定期備份。
