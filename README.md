# TeamFlow Backend

TeamFlow Backend 是 TeamFlow 團隊專案管理系統的後端 API 服務，負責使用者驗證、任務管理、Kanban 看板排序儲存，以及截止時間與任務狀態追蹤。

---

## 專案簡介

此專案使用 **FastAPI + PostgreSQL** 建立 RESTful API，提供前端任務管理功能。

系統核心目標：

* 提供類似 Jira / Trello 的任務管理後端
* 支援 Kanban 拖拉排序
* 提供完整任務生命週期管理

---

## 核心功能

* 使用者註冊 / 登入（JWT）
* 取得當前登入者資訊
* 任務 CRUD
* 任務拖拉排序（Kanban）
* 任務指派（Assignee）
* 截止時間（Deadline）
* 預估天數（Estimate）
* 任務完成時間追蹤

---

## 技術架構

* FastAPI
* SQLAlchemy
* PostgreSQL
* Pydantic
* python-jose（JWT）
* passlib + bcrypt（密碼加密）
* Uvicorn

---

## 專案結構

```
backend/
├── app/
│   ├── models/        # 資料表模型
│   ├── routers/       # API 路由
│   ├── schemas/       # 請求/回應格式
│   ├── utils/         # JWT / DB / 依賴
│   ├── database.py    # DB 連線
│   └── main.py        # 入口
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 設計亮點

### 🔹 Kanban 排序（position）

每個任務透過 `position` 控制排序，確保拖拉後順序一致。

---

### 🔹 批次排序 API

前端拖拉後一次送到：

```
PUT /tasks/reorder
```

👉 避免多次 API 呼叫（效能更好）

---

### 🔹 任務完成時間自動記錄

* 移到 done → 自動填 `completed_at`
* 移出 done → 自動清除

---

### 🔹 JWT 驗證

所有受保護 API 使用 Bearer Token 驗證

---

## 🔌 API 路由

### Auth

* POST `/auth/register`
* POST `/auth/login`
* GET `/auth/me`

### Users

* GET `/users`

### Tasks

* GET `/tasks`
* POST `/tasks`
* PUT `/tasks/{task_id}`
* PUT `/tasks/reorder`
* DELETE `/tasks/{task_id}`

---

## 🗄 資料表

### users

* id / name / email
* password_hash
* color

### tasks

* title / description
* status / category
* position
* assignee_id
* deadline
* estimated_days
* completed_at

---

## ⚙️ 安裝與執行

### 1️建立虛擬環境

```
python -m venv venv
```

### 2️啟動環境

```
venv\Scripts\activate
```

### 3️安裝套件

```
pip install -r requirements.txt
```

### 4️啟動後端

```
uvicorn app.main:app --reload
```

### 5️Swagger 文件

```
http://127.0.0.1:8000/docs
```

---

## 環境變數

```
SECRET_KEY=your_secret
DATABASE_URL=your_db_url
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

---

## 未來擴充

* Project 模組
* Dashboard
* 任務留言
* Docker
* CI/CD
* 雲端部署
