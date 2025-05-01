# 中國象棋比賽管理系統

一個基於網絡的中國象棋比賽管理系統，能夠流暢地組織賽事和管理選手，具有強大的賽程表生成算法和自動化比賽進程功能。

## 功能特色

- **賽事管理**：創建和管理多個賽事
- **參賽者管理**：添加、編輯和刪除參賽者信息
- **智能分組**：按規則分配選手，分離同校選手，合理分配種子選手
- **比賽追蹤**：自動更新和管理比賽進程
- **賽程可視化**：清晰展示賽程表和比賽進程
- **PDF導出**：將賽程表導出為PDF格式
- **拖放管理**：直觀的拖拽界面用於調整選手順序
- **冠軍慶祝**：在決定冠軍時展示彩色紙屑慶祝
- **響應式設計**：適配電腦和平板設備

## 技術架構

- 後端：Python Flask
- 數據庫：PostgreSQL與SQLAlchemy
- 前端：HTML, CSS, JavaScript (使用Material Design風格)
- 依賴庫：confetti-js (慶祝特效), SortableJS (拖拽排序), WeasyPrint (PDF生成)

## 本地部署指南

### 先決條件

- Python 3.9+
- PostgreSQL數據庫
- Node.js（用於管理前端依賴）

### 安裝步驟

1. **克隆代碼庫**

   ```bash
   git clone [儲存庫URL]
   cd chinese-chess-tournament
   ```

2. **設置Python虛擬環境**

   ```bash
   python -m venv venv
   source venv/bin/activate  # 在Windows上使用: venv\Scripts\activate
   ```

3. **安裝後端依賴**

   ```bash
   pip install -r requirements.txt
   ```

4. **安裝前端依賴**

   ```bash
   npm install
   ```

5. **配置數據庫**

   創建PostgreSQL數據庫，然後設置環境變量：

   ```bash
   # Linux/Mac
   export DATABASE_URL=postgresql://username:password@localhost/dbname
   
   # Windows
   set DATABASE_URL=postgresql://username:password@localhost/dbname
   ```

6. **初始化數據庫**

   啟動應用程式，資料表將自動創建：

   ```bash
   python main.py
   ```

### 運行應用程式

```bash
# 開發模式
python main.py

# 或在生產環境下使用Gunicorn
gunicorn --bind 0.0.0.0:5000 main:app
```

應用程式將在 http://localhost:5000 上運行

## 使用說明

1. **創建賽事**：在首頁點擊「新增賽事」按鈕
2. **管理選手**：在賽事頁面點擊「管理選手」，可以添加、編輯或刪除選手
3. **生成賽程表**：當選手數量達到至少2人時，點擊「生成賽程表」按鈕
4. **記錄比賽結果**：在賽程表上點擊獲勝選手姓名來記錄比賽結果
5. **導出賽程表**：使用「導出」按鈕將賽程表導出為PDF

## 賽程生成規則

系統根據以下規則生成淘汰賽賽程表：

1. 盡可能將來自同一學校的選手分開
2. 合理分配種子選手
3. 僅在第一輪平衡輪空選手

## 貢獻指南

如果您希望貢獻代碼，請按以下步驟操作：

1. Fork此儲存庫
2. 創建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打開Pull Request
