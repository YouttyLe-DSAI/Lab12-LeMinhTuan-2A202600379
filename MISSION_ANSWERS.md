# Day 12 Lab - Mission Answers

> **Student Name:** Lê Minh Tuấn  
> **Student ID:** 2A202600379  
> **Date:** 17/04/2026

---

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found
1. **Hardcoded Secrets**: Sử dụng API keys trực tiếp thay vì biến môi trường.
2. **Hardcoded Infrastructure**: Port và Host bị gắn chết (`localhost:8000`).
3. **print() Logging**: Thiếu log cấu trúc JSON và timestamp.
4. **No Healthchecks**: Hệ thống không có endpoint để cloud orchestrator giám sát.

### Exercise 1.3: Comparison table
| Feature | Develop | Production | Why Important? |
|---------|---------|------------|----------------|
| Config  | Hardcoded | Environment Variables | Bảo mật secrets và linh hoạt môi trường. |
| Health  | Không có | Endpoint `/health` | Cloud tự động phát hiện và restart service lỗi. |
| Logging | `print()` | Structured JSON | Dễ dàng log centralization và monitoring. |
| Network | `localhost`| `0.0.0.0` | Cho phép container nhận traffic từ bên ngoài. |

---

## Part 2: Docker

### Exercise 2.1: Dockerfile questions
1. **Base image:** `python:3.11-slim` - Nhẹ, giảm bề mặt tấn công.
2. **Working directory:** `/app` - Tổ chức file ngăn nắp.
3. **Multi-stage:** Sử dụng `builder` và `runtime` staging để loại bỏ file rác, giảm image size.

### Exercise 2.3: Image size comparison
- **Develop:** ~980 MB
- **Production:** ~184 MB
- **Difference:** Giảm ~81% dung lượng.

---

## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment
- **URL:** [https://lecture-day12-production.up.railway.app](https://lecture-day12-production.up.railway.app)
- **Screenshot:** Xem `06-lab-complete/screenshot/dashboard.jpg`.

---

## Part 4: API Security

### Exercise 4.1-4.3: Test results
- **API Authentication:** Header `X-API-Key` hoạt động chính xác (Trả về 401 nếu thiếu/sai).
- **Rate Limit:** Cấu hình 10 req/min qua Redis phát hiện và chặn spam hiệu quả (429).
- **JWT Auth:** Đã triển khai và kiểm tra thành công luồng xác thực token.

### Exercise 4.4: Cost guard implementation
- **Cách thực hiện:** Sử dụng Redis `incrbyfloat` để cộng dồn chi phí token thực tế của từng request. 
- **Chặn truy cập:** Trước mỗi request, hệ thống kiểm tra ngân sách ngày. Nếu vượt ngưỡng $10 (cấu hình trong `settings.daily_budget_usd`), Agent sẽ báo lỗi 402.

---

## Part 5: Scaling & Reliability

### Exercise 5.1-5.5: Implementation notes
- **Stateless Design:** Toàn bộ session được lưu vào Redis thay vì bộ nhớ local, cho phép scaling ngang không mất dữ liệu.
- **Load Balancing:** Sử dụng Nginx phân phối traffic cho 3 instances. Đã test tính đồng bộ của Rate limit trên cả 3 bản sao.
- **Health Checks:** Endpoint `/health` trả về đầy đủ tình trạng của Redis và LLM provider (Xem `running.jpg`).

---

## Part 6: Final Progress
Dự án đã sẵn sàng nộp bài với đầy đủ 20/20 tiêu chí chuẩn Production của Day 12.
