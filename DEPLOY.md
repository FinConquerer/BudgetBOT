# Triển khai Production (Docker)

Kiến trúc prod: **nginx** phục vụ frontend (build tĩnh) và proxy `/api` sang **backend**
(uvicorn). Database dùng **Postgres sẵn có** (không nằm trong compose). Backend tự chạy
`alembic upgrade head` khi khởi động.

```
Người dùng ──▶ :80 nginx (frontend) ──/api──▶ backend:8000 ──▶ Postgres (host/DB có sẵn)
```

## File liên quan
- `docker-compose.prod.yml` — dịch vụ backend + frontend cho prod.
- `frontend/Dockerfile.prod` + `frontend/nginx.conf` — build tĩnh + nginx.
- `backend/Dockerfile` — image backend (uvicorn + alembic).
- `.env.prod.example` — mẫu biến môi trường (sao chép thành `.env.prod`, **không commit**).

---

## A. Deploy thủ công (chạy trên server)

```bash
# 1) Lần đầu: clone repo về server
git clone https://github.com/FinConquerer/BudgetBOT.git
cd BudgetBOT

# 2) Tạo .env.prod từ mẫu và điền giá trị thật
cp .env.prod.example .env.prod
nano .env.prod          # đặt DATABASE_URL, SECRET_KEY (openssl rand -hex 32), CORS_ORIGINS

# 3) Build & chạy
docker compose -f docker-compose.prod.yml up -d --build

# 4) Kiểm tra
docker compose -f docker-compose.prod.yml ps
curl -s localhost/api/version
```

Truy cập: `http://<server-ip>/` (frontend), API qua `http://<server-ip>/api/...`.

### Cập nhật phiên bản mới
```bash
cd BudgetBOT
git pull origin production
docker compose -f docker-compose.prod.yml up -d --build
docker image prune -f
```

### Lưu ý DATABASE_URL
- Nếu Postgres chạy **ngay trên host**: dùng `host.docker.internal:5432`
  (compose đã bật `extra_hosts: host.docker.internal:host-gateway`).
- Nếu ở nơi khác (RDS, server riêng): điền host/hostname tương ứng.

---

## B. Tự động deploy bằng GitHub Actions

Workflow `.github/workflows/deploy.yml` sẽ SSH vào server và cập nhật mỗi khi push vào
`production` (hoặc chạy tay từ tab Actions).

### Thiết lập một lần
1. Trên server: đảm bảo đã `git clone` repo và tạo `.env.prod` (như phần A).
2. Tạo SSH key riêng cho deploy và thêm public key vào `~/.ssh/authorized_keys` của user deploy.
3. Trong repo GitHub → **Settings → Secrets and variables → Actions**, thêm:
   - `DEPLOY_HOST` — IP/hostname server
   - `DEPLOY_USER` — user SSH (khuyến nghị tạo user `deploy` có quyền chạy docker, **không dùng root**)
   - `DEPLOY_SSH_KEY` — **private key** tương ứng
   - `DEPLOY_PATH` — đường dẫn repo trên server (vd `/home/deploy/BudgetBOT`)
   - `DEPLOY_PORT` — (tuỳ chọn) cổng SSH, mặc định 22
4. Bật deploy: **Settings → Secrets and variables → Actions → Variables** → thêm
   biến `DEPLOY_ENABLED` = `true`. (Chưa có biến này thì job deploy được **skip**,
   không báo đỏ.)

Sau đó: mỗi lần merge vào `production`, CI test + workflow deploy tự chạy.

> Nếu đã từng `gh workflow disable deploy.yml`, bật lại bằng `gh workflow enable deploy.yml`.

---

## Bảo mật cần làm
- Đặt `SECRET_KEY` ngẫu nhiên mạnh trong `.env.prod`.
- Không mở cổng 5432 (Postgres) ra Internet; chỉ cho backend truy cập.
- Ưu tiên đặt nginx/HTTPS (Let's Encrypt) trước cổng 80 khi có domain.
- Dùng user deploy riêng thay vì root cho GitHub Actions.
