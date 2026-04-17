# Day 12 — AI Agent in Production
## Lab của Lê Minh Tuấn (2A202600379)

> [!CAUTION]
> **CẢNH BÁO BẢO MẬT — ĐỌC TRƯỚC KHI DÙNG**
>
> Repository này chứa code mẫu và **KHÔNG** đi kèm file `.env` hoặc API Keys thực tế.
> Nếu bạn clone repo này, bạn **PHẢI**:
> 1. Tự tạo file `.env` theo hướng dẫn bên dưới.
> 2. **KHÔNG BAO GIỜ** commit file `.env` lên Git.
> 3. **KHÔNG BAO GIỜ** dùng lại API Key của người khác.
> 4. API Key trong file `.env.example` chỉ là ví dụ, **ĐÃ BỊ VÔ HIỆU HÓA**.

---

## 🗺️ Tổng quan dự án

Lab này triển khai AI Agent theo từng bước, từ môi trường phát triển cơ bản đến hệ thống Production có khả năng chịu tải cao.

```
Lecture-Day-12/
├── 01-localhost-vs-production/   # So sánh code dev vs production
├── 02-docker/                    # Docker Compose stack đầy đủ
├── 03-cloud-deployment/railway/  # Deploy lên Railway (Cloud)
├── 04-api-gateway/               # Bảo mật với JWT & Rate Limiting
├── 05-scaling-reliability/       # Scale với Redis + Nginx
└── 06-lab-complete/              # Final Project (Production-ready)
```

---

## ⚙️ Yêu cầu hệ thống

| Công cụ | Phiên bản tối thiểu | Cài đặt |
|---------|---------------------|---------|
| Python | 3.11+ | [python.org](https://python.org) |
| Docker Desktop | 24+ | [docker.com](https://docker.com) |
| Git | 2.40+ | [git-scm.com](https://git-scm.com) |

---

## 🚀 Hướng dẫn chạy từ đầu đến cuối

### Bước 0: Clone và cấu hình môi trường

```bash
git clone https://github.com/YouttyLe-DSAI/Lab12-LeMinhTuan-2A202600379.git
cd Lab12-LeMinhTuan-2A202600379
```

> [!IMPORTANT]
> Sau khi clone, bạn **BẮT BUỘC** phải tạo các file `.env` trước khi chạy bất cứ thứ gì.
> Xem hướng dẫn tạo file `.env` ở phần tiếp theo.

---

### Part 1: Localhost vs Production

```bash
cd 01-localhost-vs-production/production

# Tạo file .env từ template
cp .env.example .env
# Mở .env và điền API keys của BẠN vào

# Cài đặt thư viện
pip install -r requirements.txt

# Chạy server
python app.py
```

**Test:**
```powershell
# Windows PowerShell
curl.exe http://localhost:8000/health
```

---

### Part 2: Docker (Khuyến nghị — Không cần cài Python thủ công)

> [!IMPORTANT]
> Tất cả lệnh `docker build` và `docker compose` phải chạy từ **thư mục gốc** (`Lecture-Day-12/`).
> Lý do: Dockerfile cần truy cập vào thư mục `utils/` nằm ở gốc dự án.

**2a. Build bản Development (Đơn giản):**
```bash
# Phải đứng ở thư mục gốc Lecture-Day-12/
docker build -f 02-docker/develop/Dockerfile -t my-agent:develop .
docker run -p 8000:8000 my-agent:develop
```

**Test bản Develop** (gửi qua URL query, không phải JSON Body):
```powershell
curl.exe -X POST "http://localhost:8000/ask?question=What%20is%20Docker?"
```

**2b. Chạy Production Stack (Nginx + Redis + Qdrant):**
```bash
cd 02-docker/production

# Tạo file .env.local
cp .env.example .env.local
# Điền các giá trị vào .env.local

docker compose up -d --build
```

> [!WARNING]
> Agent không nhận request trực tiếp tại cổng 8000 trong bản Production.
> Tất cả traffic phải đi qua **Nginx ở cổng 80**.

**Test bản Production** (luôn dùng cổng 80):
```powershell
curl.exe http://localhost/health
curl.exe -X POST http://localhost/ask `
  -H "Content-Type: application/json" `
  -d "{\`"question\`": \`"Explain microservices\`"}"
```

---

### Part 3: Cloud Deployment (Railway)

**Live Demo (Không cần API Key):**
```powershell
# Endpoint công khai — dùng thử luôn
curl.exe -X POST https://lecture-day12-production.up.railway.app/ask/public `
  -H "Content-Type: application/json" `
  -d "{\`"question\`": \`"What is Docker?\`"}"

# Health check
curl.exe https://lecture-day12-production.up.railway.app/health
```

**Endpoint có bảo mật (cần API Key):**
```powershell
curl.exe -X POST https://lecture-day12-production.up.railway.app/ask `
  -H "Content-Type: application/json" `
  -H "X-API-Key: <YÊU CẦU API KEY — LIÊN HỆ TÁC GIẢ>" `
  -d "{\`"question\`": \`"What is Docker?\`"}"
```

> [!NOTE]
> Để deploy lên Railway của riêng bạn, xem hướng dẫn trong thư mục `03-cloud-deployment/railway/`.

---

### Part 4: API Security Gateway

```bash
cd 04-api-gateway/production

# Tạo .env.local
cp .env.example .env.local

docker compose up -d --build
```

**Luồng xác thực:**
```powershell
# Bước 1: Đăng nhập lấy JWT Token
curl.exe -X POST http://localhost:8888/auth/token `
  -H "Content-Type: application/json" `
  -d "{\`"username\`": \`"admin\`", \`"password\`": \`"secret\`"}"

# Bước 2: Dùng token để gọi API (thay YOUR_TOKEN bằng token nhận được)
curl.exe -X POST http://localhost:8888/ask `
  -H "Authorization: Bearer YOUR_TOKEN" `
  -H "Content-Type: application/json" `
  -d "{\`"question\`": \`"What is JWT?\`"}"
```

---

### Part 5: Scaling & Reliability

```bash
cd 05-scaling-reliability/production

# Tạo .env.local
cp .env.example .env.local  # hoặc tạo thủ công

# Scale lên 3 instances
docker compose up --scale agent=3 -d
```

**Verify Stateless (Session không mất khi đổi instance):**
```bash
python test_stateless.py
```

---

### Part 6: Final Project (Production Ready)

```bash
cd 06-lab-complete

# Tạo .env.local
cp .env.example .env.local

# Chạy kiểm tra chất lượng
python check_production_ready.py

# Kết quả kỳ vọng: 20/20 checks passed (100%)

# Khởi động hệ thống với 3 instances
docker compose up --build --scale agent=3
```

---

## 🔑 Cấu hình biến môi trường

> [!CAUTION]
> **KHÔNG BAO GIỜ commit `.env` lên Git.** File `.gitignore` đã được cấu hình để bảo vệ bạn.
> Nhưng bạn vẫn cần phải tự kiểm tra.

Tạo file `.env.local` trong từng thư mục `production/` với nội dung sau:

```env
# === BẮT BUỘC ===
AGENT_API_KEY=your-secret-key-here      # Khóa bảo vệ API của bạn
OPENAI_API_KEY=sk-proj-...              # Lấy từ platform.openai.com

# === TÙY CHỌN ===
REDIS_URL=redis://redis:6379/0
LLM_MODEL=gpt-4o-mini
RATE_LIMIT_PER_MINUTE=10
DAILY_BUDGET_USD=2.0
ENVIRONMENT=production
```

---

## 🐳 Các lệnh Docker thường dùng

```bash
# Xem các container đang chạy
docker ps

# Xem log của một service
docker compose logs agent -f

# Dừng toàn bộ stack
docker compose down

# Dừng và xóa toàn bộ volumes (cẩn thận!)
docker compose down -v

# Xem danh sách images
docker images --filter "reference=my-agent*"
```

---

## ⚠️ Các lỗi thường gặp & Cách sửa

| Lỗi | Nguyên nhân | Cách sửa |
|-----|-------------|----------|
| `not found: /utils/mock_llm.py` | Chạy docker build sai thư mục | Chạy từ thư mục gốc `Lecture-Day-12/` |
| `Failed to connect to localhost port 8000` | Agent ẩn sau Nginx | Dùng cổng `80` thay vì `8000` |
| `422 Unprocessable Entity` | Sai định dạng tham số | Xem log để biết server mong đợi gì |
| `env file .env.local not found` | Chưa tạo file .env | `cp .env.example .env.local` |
| `401 Unauthorized` | Thiếu API Key header | Thêm `-H "X-API-Key: your-key"` |
| `grep not found` | Lệnh Linux trên Windows | Dùng `Select-String` hoặc `--filter` |

---

## 📞 Liên hệ

- **Tác giả:** Lê Minh Tuấn
- **Student ID:** 2A202600379
- **GitHub:** [YouttyLe-DSAI](https://github.com/YouttyLe-DSAI)
- **Live Demo:** [lecture-day12-production.up.railway.app](https://lecture-day12-production.up.railway.app)
