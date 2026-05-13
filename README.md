# TeamFlow Backend

FastAPI 後端，負責專案管理、任務協作與使用者驗證。

---

## 專案特色

- 使用 FastAPI 建立高效能 RESTful API
- JWT Authentication
- Kanban + Timeline 支援
- Docker + CI/CD
- 支援多專案與團隊協作場景

---

## 核心功能

### 使用者
- 註冊 / 登入
- JWT 驗證

### 專案
- 建立 / 查詢 / 刪除
- 成員管理

### 任務
- CRUD
- 拖拉排序（position）
- Deadline / Estimated Days

### Timeline
- start_date / deadline

### 留言
- CRUD
- Like

---

## 技術

- FastAPI / SQLAlchemy
- PostgreSQL
- JWT / bcrypt
- Docker / GitHub Actions / GHCR / Render

---

## 本機開發

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## 環境變數

```env
DATABASE_URL=your_database_url
SECRET_KEY=your_secret_key
```

## API

```bash
/auth
/projects
/tasks
/comments
```

## 部署

- Render（Backend）
- GHCR（Docker Image）
- GitHub Actions（CI/CD）

## 架構

```text
Client
  ↓
Vercel Frontend
  ↓
Render Backend
  ↓
PostgreSQL
```

## 專案亮點

- 設計 Project / Member / Invitation 關聯模型支援團隊協作
- JWT 安全驗證
- Kanban 排序機制（position-based）
- Timeline 資料支援
- Docker + CI/CD 自動化部署

## 未來規劃

- WebSocket 即時同步
- 通知系統
- 測試（pytest）