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
- 數據庫：Firebase Firestore (雲端NoSQL數據庫)
- 前端：HTML, CSS, JavaScript (使用Material Design風格)
- 依賴庫：firebase-admin (Firebase SDK), confetti-js (慶祝特效), SortableJS (拖拽排序), WeasyPrint (PDF生成)

## 安裝與使用

詳細的本地部署指南、運行說明和使用方法，請參閱 <mcfile name="INSTALL.md" path="c:\Users\user\Documents\program\SBA\ChineseBracketMaster\INSTALL.md"></mcfile> 文件。

## 賽程生成規則

系統根據以下規則生成淘汰賽賽程表：

1. 盡可能將來自同一學校的選手分開
2. 合理分配種子選手
3. 僅在第一輪平衡輪空選手

## 數據結構

系統使用Firebase Firestore存儲數據，主要集合包括：

- **/tournaments/{tournament_id}**：存儲賽事信息
- **/players/{player_id}**：存儲選手信息
- **/matches/{match_id}**：存儲比賽信息

## 項目背景 (原始需求)

**Prompt: Inter-School Chinese Chess Competition System**

**Objective:**
Develop a program to generate the final competition schedule (賽程表) for an inter-school Chinese chess competition using a knockout system.

**Main Target:**
The program should produce a competition chart, ensuring:
Separation of players from the same school, where possible.
Separation of seed players, where possible.
Balanced distribution of 'byes' in the first round only.

**Key Tasks:**

1.  **Input and Data Collection:**
    *   Collect player information: names, school, and seeding status.
    *   Gather competition rules and constraints.
2.  **Data Structure and Storage:**
    *   Select appropriate data structures to store player information.
    *   Store competition rules and constraints.
3.  **Algorithm Design:**
    *   Design algorithms to generate the competition chart.
    *   Ensure algorithms separate players from the same school and seed players.
    *   Implement logic to handle 'byes' for non-power of 2 participants.
4.  **Program Implementation:**
    *   Develop a modular program to produce the competition chart.
    *   Implement error handling and validation for data inputs.
    *   Ensure the program interface is user-friendly.
5.  **Output and Presentation:**
    *   Design the layout of the competition chart.
    *   Generate the competition chart based on input data and constraints.
    *   Ensure the output format is clear and easily readable.
6.  **Testing and Evaluation:**
    *   Create test cases to validate the program's functionality.
    *   Conduct unit tests, system tests, and user acceptance tests.
    *   Collect feedback and record test results.
    *   Make necessary improvements based on testing outcomes.

**Deliverables:**

*   Program code
*   Prototype presentation and documentation
*   Test plan and test results
*   Evaluation report with suggested improvements

