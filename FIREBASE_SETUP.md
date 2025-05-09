# Firebase 設置指南

## 概述

本應用程序使用 Firebase Firestore 作為數據庫。要正確運行應用程序，您需要設置 Firebase 憑證。

## 設置步驟

### 1. 獲取 Firebase 憑證

1. 登錄到 [Firebase 控制台](https://console.firebase.google.com/)
2. 選擇或創建一個新項目
3. 在項目設置中，選擇「服務帳戶」選項卡
4. 點擊「生成新的私鑰」按鈕
5. 下載生成的 JSON 文件

### 2. 設置憑證

您有以下幾種方式設置 Firebase 憑證：

#### 方法 1: 使用環境變數（推薦用於生產環境）

在 Windows 上：
```
set GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\your\firebase-credentials.json
```

在 Linux/Mac 上：
```
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/firebase-credentials.json
```

#### 方法 2: 將憑證文件放在項目目錄中（開發環境）

將下載的 JSON 文件重命名為以下任一名稱，並放在項目根目錄：
- `firebase-credentials.json`
- `firebase-key.json`

或者放在 `instance` 目錄中：
- `instance/firebase-credentials.json`
- `instance/firebase-key.json`

應用程序將自動檢測這些位置的憑證文件。

### 3. 憑證文件格式

您的憑證文件應該類似於 `firebase-credentials-example.json`，但包含您的實際項目信息。請確保不要將實際憑證文件提交到版本控制系統。

## 故障排除

如果您遇到 Firebase 連接問題：

1. 確認憑證文件格式正確
2. 檢查應用程序日誌中的錯誤消息
3. 確保您的 Firebase 項目已啟用 Firestore 數據庫
4. 確認您的 IP 地址未被 Firebase 安全規則阻止

## 重啟應用程序

設置憑證後，重啟應用程序以應用更改：

```
python main.py
```

或者：

```
python app.py
```