# Day 12 Lab - Mission Answers
#  Delivery Checklist — Day 12 Lab Submission

> **Student Name:** Lê Minh Tuấn

> **Student ID:** 2A202600379  

> **Date:** 18/4/2026

---
## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found
1. **Hardcoded Secrets**: API keys và Database URLs được ghi trực tiếp trong mã nguồn (`app.py`), dẫn đến nguy cơ lộ bí mật nếu code được chia sẻ hoặc push lên GitHub.
2. **Thiếu Quản lý Cấu hình Tập trung**: Các biến cấu hình như `DEBUG` và `MAX_TOKENS` nằm rải rác trong file chính, thay vì được quản lý tập trung và đọc từ biến môi trường.
3. **Sử dụng print() thay vì Proper Logging**: Dùng `print()` không cung cấp timestamp hay log levels, và đặc biệt nguy hiểm khi log cả secret key ra màn hình console.
4. **Thiếu Health Check Endpoint**: Không có endpoint `/health`, khiến các nền tảng tự động hóa (Cloud orchestrators) không thể kiểm soát trạng thái của Agent để tự khởi động lại khi gặp lỗi.
5. **Cấu hình Hạ tầng Cố định**: Hardcode `host="localhost"` và `port=8000` khiến ứng dụng không thể chạy trên các môi trường đám mây (Cloud) nơi Port thường được cấp phát động.

## Part 2: Docker

### Exercise 2.1: Dockerfile questions
1. **Base image là gì?**: `python:3.11` (Bản Develop) và `python:3.11-slim` (Bản Production).
2. **Working directory là gì?**: `/app`.
3. **Tại sao COPY requirements.txt trước?**: Để tận dụng cơ chế **Layer Caching** của Docker. Nếu file requirements không đổi, Docker sẽ không cần chạy lại lệnh `pip install` ở các lần build sau, giúp tiết kiệm thời gian.
4. **CMD vs ENTRYPOINT khác nhau thế nào?**: `ENTRYPOINT` quy định lệnh thực thi chính không thể bị ghi đè dễ dàng, trong khi `CMD` cung cấp các tham số mặc định và có thể bị ghi đè bởi người dùng khi chạy `docker run`.

### Exercise 2.3: Image size comparison (Kết quả thực tế)
- **Develop (python:3.11 full)**: **1.66 GB** ← base image đầy đủ, có pip, gcc, v.v.
- **Production (Multi-stage + python:3.11-slim)**: Nhỏ hơn đáng kể (~160-200 MB)
- **Kết luận**: Multi-stage build giảm ~80% dung lượng, image sạch hơn, an toàn hơn (không có build tools).

### Exercise 2.4: Docker Compose stack (Kết quả thực tế)
- **Dịch vụ đã chạy thành công**:
  - `production-agent-1` → **healthy** (port 8000, không expose ra ngoài)
  - `production-redis-1` → **healthy** (cache & rate limiting)
  - `production-nginx-1` → **running** (port 80 & 443, reverse proxy)
  - `production-qdrant-1` → running (vector DB, health check cần `curl` không có sẵn)
- **Test qua Nginx thành công**:
  ```
  curl http://localhost/health
  → {"status":"ok","uptime_seconds":55.6,"version":"2.0.0"}
  ```
- **Cách communicate**: Qua Docker internal network (`production_internal`), các service gọi nhau qua tên service (e.g. `redis:6379`, `agent:8000`). Nginx là "cổng" duy nhất expose ra ngoài.

### Architecture Diagram

```mermaid
graph TD
    Internet([🌐 Internet]) --> Nginx

    Nginx["🔀 Nginx\nPort 80/443\nReverse Proxy"] --> Agent

    subgraph internal["Docker Internal Network: production_internal"]
        Agent["🤖 Agent FastAPI\nPort 8000\nproduction-agent"] --> Redis
        Agent --> Qdrant
        Redis["⚡ Redis\nPort 6379\nCache & Rate Limit"]
        Qdrant["🗄️ Qdrant\nPort 6333\nVector Database"]
    end
```

### Exercise 1.3: Comparison table

| Feature | Develop | Production | Why Important? |
|---------|---------|------------|----------------|
| **Config** | Hardcode trong code | Đọc từ Environment Variables (`.env`) | Dễ dàng thay đổi cấu hình mà không cần sửa code, bảo mật secrets. |
| **Health check**| Không có | Có `/health` và `/ready` | Giúp Cloud Platform theo dõi trạng thái và tự động phục hồi app. |
| **Logging** | `print()` thủ công | Structured JSON Logging | Dễ dàng thu thập và phân tích log tự động bởi các công cụ giám sát. |
| **Shutdown** | Đứt gãy (Stop đột ngột) | Graceful Shutdown (Tắt an toàn) | Đảm bảo các request đang xử lý được hoàn thành trước khi ứng dụng tắt. |
| **Binding** | `localhost` | `0.0.0.0` | Cho phép nhận traffic từ bên ngoài (khi chạy trong Docker/Cloud). |

---

## Part 3: Cloud Deployment

### Exercise 3.1: Platform so sánh

| Tiêu chí | **Railway** | **AWS App Runner** |
|----------|-------------|-------------------|
| **Độ khó setup** | Rất thấp (Auto-detect) | Trung bình (Cần config Service/IAM) |
| **Tốc độ build** | Nhanh (~3-5 phút) | Chậm hơn (~5-8 phút) |
| **Khả năng Scale** | Tốt (Vertical & Horizontal) | Rất mạnh (Tự động theo request) |
| **Hệ sinh thái** | Độc lập | Tích hợp sâu AWS (S3, RDS, VPC) |
| **Bảo mật** | Cơ bản | Enterprise-grade (IAM, VPC) |
| **Dùng khi nào?** | MVP, Prototype, cá nhân | Production quy mô lớn, cần bảo mật cao |

### Exercise 3.2: Tại sao serverless không phải lúc nào cũng tốt cho AI Agent?

**Cold Start Problem**: Serverless functions "ngủ" khi không có traffic. Khi request đầu tiên đến, hệ thống cần khởi động lại (cold start), mất 2-10 giây. Điều này không chấp nhận được với AI Agent vì:
- Model loading tốn thời gian
- User experience bị ảnh hưởng
- LLM connections cần warm-up

**Giải pháp**: Dùng dedicated containers (Railway/Cloud Run) với `min_instances=1` để luôn có ít nhất 1 instance sẵn sàng.

### Exercise 3.3: Deployment thực tế (Multi-Cloud)

#### Nền tảng 1: Railway (Dễ tiếp cận)
- **URL Public**: [https://lecture-day12-production.up.railway.app](https://lecture-day12-production.up.railway.app)
- **Health check**: [https://lecture-day12-production.up.railway.app/health](https://lecture-day12-production.up.railway.app/health)
- **Ưu điểm**: Setup cực nhanh, tự động hóa hoàn toàn với GitHub.

#### Nền tảng 2: AWS App Runner (Production-grade)
- **URL Public**: [https://b2xupazkma.ap-southeast-1.awsapprunner.com](https://b2xupazkma.ap-southeast-1.awsapprunner.com)
- **Health check**: [https://b2xupazkma.ap-southeast-1.awsapprunner.com/health](https://b2xupazkma.ap-southeast-1.awsapprunner.com/health)
- **Ưu điểm**: Hạ tầng AWS ổn định, khả năng Auto-scaling mạnh mẽ, hỗ trợ IAM Roles cho bảo mật nâng cao.

#### Phân tích so sánh thực tế:

| Feature | Railway | AWS App Runner |
|---------|---------|----------------|
| **Deployment Time** | ~2 mins | ~5-7 mins |
| **Control** | Trung bình | Cao (Network, VPC, IAM) |
| **Pricing Model** | Tiêu thụ tài nguyên | Cố định (Provisioned) + Tiêu thụ |
| **Workflow** | GitHub -> Nixpacks | GitHub -> AWS Build Service |

### Architecture Diagram (Cloud Deployment)

```mermaid
graph LR
    Dev([💻 Developer]) -- Push --> GitHub[🐙 GitHub Repo]
    
    subgraph Cloud Platform
        GitHub -- Webhook --> BuildEngine["🏗️ Build & Deploy Engine"]
        BuildEngine -- Run --> AgentRuntime["🤖 AI Agent Container"]
        AgentRuntime -- Config --> EnvVar["🔑 Secrets/Env Vars"]
    end
    
    AgentRuntime -- API Call --> OpenAI[🧠 OpenAI API]
    User([🌐 User]) -- HTTPS --> AgentRuntime

---

## Part 4: API Security

### Exercise 4.1: Tại sao nên dùng JWT thay vì API Key cố định?
1. **Stateless**: Server không cần lưu trữ session, giúp hệ thống scale dễ dàng hơn.
2. **Security**: Token có thời hạn (Expiry), nếu bị lộ cũng chỉ có tác dụng trong thời gian ngắn. API Key cố định nếu lộ sẽ gây thiệt hại vĩnh viễn cho đến khi được quay vòng (rotate).
3. **Data-rich**: Token có thể chứa thông tin về `role` (Admin/User), giúp phân quyền ngay lập tức mà không cần truy vấn Database.

### Exercise 4.2: Kết quả thực nghiệm Security Stack (Thao tác trên localhost:8888)
- **JWT Auth**: Đã thực hiện luồng: Đăng nhập (`/auth/token`) -> Nhận `access_token` -> Sử dụng Header `Authorization: Bearer` -> Gọi API `/ask` thành công.
- **Rate Limit**: Đã thử nghiệm spam request liên tục. Kết quả: Sau 10 request, hệ thống trả về mã lỗi **429 Too Many Requests**.
- **Cost Guard**: Token OpenAI được ghi nhận và trừ vào ngân sách giả định. Bạn đã thấy `budget_remaining_usd` giảm đi sau mỗi lần hỏi.

### Sơ đồ kiến trúc Security Gateway

```mermaid
graph TD
    User([🌐 User]) --> Gateway["🛡️ Security Gateway<br/>(FastAPI Middleware)"]
    Gateway -- 1. Verify JWT --> Auth{Valid?}
    Auth -- Yes --> RateLimit["⏱️ Rate Limiter<br/>(Check Quota)"]
    Auth -- No --> 401[❌ 401 Unauthorized]
    RateLimit -- OK --> CostGuard["💰 Cost Guard<br/>(Check Budget)"]
    RateLimit -- Full --> 429[⚠️ 429 Too Many Requests]
    CostGuard -- OK --> Agent["🤖 AI Agent<br/>(Process Request)"]
    CostGuard -- Over --> 402[💸 402 Payment Required]
```

---

## Part 5: Scaling & Reliability

### Exercise 5.1 & 5.2: Phân tích cơ chế tin cậy
- **Health Checks**: Đã triển khai `/health` (Liveness) và `/ready` (Readiness). Điều này giúp Nginx và Docker biết khi nào Agent sẵn sàng nhận việc hoặc cần khởi động lại.
- **Graceful Shutdown**: Hệ thống đã xử lý tín hiệu `SIGTERM`. Khi tắt container, Agent sẽ hoàn thành các request dở dang và đóng kết nối an toàn, không gây lỗi 502 cho người dùng.

### Exercise 5.3 & 5.4: Kết quả Scaling thực tế
- **Stateless Design**: Toàn bộ session history và rate limit đã được đẩy sang **Redis**. 
- **Load Balancing**: Đã scale lên **3 instances**. Qua thử nghiệm, các request được phân phối đều (Round-robin) qua Nginx. Dù request 1 và request 2 rơi vào 2 instance khác nhau, người dùng vẫn thấy lịch sử chat liên tục nhờ bộ nhớ tập trung Redis.

---

## Part 6: Final Project - Production Ready AI Agent

Đây là chặng đường cuối cùng, kết hợp tất cả các kỹ năng đã học:
- **Kết quả kiểm tra tự động (`check_production_ready.py`)**: **20/20 checks passed (100%)**.
- **Điểm số tối đa**: Hệ thống đạt đầy đủ các tiêu chí về Bảo mật (Auth/CostGuard), Hiệu năng (Stateless/Redis), và Hạ tầng (Docker Multi-stage/Nginx).
- **Tình trạng**: **🎉 PRODUCTION READY!** Hệ thống đã sẵn sàng được đưa lên các Cloud platform chuyên nghiệp.

**Hành trình Day 12 kết thúc thành công rực rỡ! 🚀**
