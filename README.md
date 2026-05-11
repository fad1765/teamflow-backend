# TeamFlow Backend

TeamFlow Backend 是專案管理系統的後端 API，負責專案管理、任務協作、使用者驗證與資料儲存。

---

## 📌 專案簡介

本專案使用 **FastAPI + PostgreSQL** 建立 RESTful API，支援多專案與團隊協作，並具備完整 CI/CD 自動部署流程。

---

## 核心功能

### 使用者系統

- 註冊 / 登入（JWT）
- 取得當前使用者

### 專案管理

- 建立專案（個人 / 團隊）
- 專案列表（僅本人參與）
- 專案描述（description）
- 專案刪除
- 成員數統計

### 專案成員
- ProjectMember 關聯
- role（owner / member）
- 成員權限控管

### 邀請系統
- 發送邀請（Email）
- 查詢我的邀請
- 接受邀請 → 自動加入專案
- 拒絕邀請
- 回傳：
  - project_name
  - inviter_name
  - inviter_email

### 任務管理
- 任務 CRUD
- Kanban 拖拉排序（position）
- 任務指派（assignee）
- 截止時間（deadline）
- 預估天數（estimated_days）
- 完成時間自動記錄

---

## 技術架構

- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic
- python-jose（JWT）
- passlib + bcrypt
- Uvicorn
- Docker
- GitHub Actions（CI/CD）

---

## 專案結構

backend/
├── app/
│ ├── models/ # 資料表模型
│ ├── routers/ # API 路由
│ ├── schemas/ # 請求/回應格式
│ ├── utils/ # JWT / DB / 依賴
│ ├── database.py
│ └── main.py
├── requirements.txt
└── README.md

---

## API 路由

### Auth
- POST `/auth/register`
- POST `/auth/login`
- GET `/auth/me`

### Users
- GET `/users`

### Projects
- GET `/projects`
- POST `/projects`
- GET `/projects/{id}`
- DELETE `/projects/{id}`

### Invitations
- GET `/invitations/my`
- POST `/invitations/{id}/accept`
- POST `/invitations/{id}/decline`

### Tasks
- GET `/tasks`
- POST `/tasks`
- PUT `/tasks/{task_id}`
- PUT `/tasks/reorder`
- DELETE `/tasks/{task_id}`

---

## 資料表

### users
- id / name / email
- password_hash
- color

### projects
- name / description / type / owner_id

### project_members
- project_id / user_id / role

### project_invitations
- project_id / email / invited_by / status

### tasks
- title / description / status / category / position
- assignee_id / deadline / estimated_days / completed_at

---

## 本機開發


python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload


Swagger：

http://127.0.0.1:8000/docs


---

## Docker

### 啟動

docker compose up --build

### 常用指令

docker compose exec db psql -U postgres -d teamflow_db
docker compose restart backend
docker compose down

---

## CI/CD 與部署架構

### 🔷 CI（Continuous Integration）

使用 **GitHub Actions** 自動執行：

- Python 語法檢查（compileall）
- FastAPI 啟動驗證
- Docker Image 建置

---

### 🔷 CD（Continuous Deployment）


PR merge → master
↓
GitHub Actions（build & push Docker）
↓
Railway 偵測更新
↓
自動部署 backend

---

### 🔷  Docker + GHCR

ghcr.io/fad1765/teamflow-backend:latest

GHCR（GitHub Container Registry）為 Docker Image 儲存服務

---

### 🔷 Backend 部署（Railway）

- FastAPI 部署於 Railway
- PostgreSQL 使用 Railway DB
- 環境變數由 Railway 管理

---

### 🔷 系統架構


[ Client ]
↓
[ Vercel Frontend ]
↓ API
[ Railway Backend ]
↓
[ Railway PostgreSQL ]


---

## 環境變數

DATABASE_URL=xxx
SECRET_KEY=xxx
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440


---

## CORS 設定


allow_origins = [
"http://localhost:5173",
"https://teamflow-frontend.vercel.app
"
]

---

## 未來擴充

- Timeline（專案時程）
- Dashboard（PM 視角）
- 測試（pytest）
- 多環境部署