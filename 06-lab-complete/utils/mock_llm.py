import time
import random

_RESPONSES = {
    "docker": "Docker là nền tảng container hóa cho phép đóng gói ứng dụng cùng dependencies vào một container nhất quán. Build once, run anywhere!",
    "kubernetes": "Kubernetes (K8s) là hệ thống orchestration để tự động deploy, scale và quản lý container applications.",
    "redis": "Redis là in-memory data store dùng cho caching, session management, rate limiting và message queuing. Cực kỳ nhanh!",
    "fastapi": "FastAPI là modern Python web framework với auto OpenAPI docs, type hints, và async support. Hiệu năng ngang ngửa NodeJS.",
    "microservices": "Microservices là kiến trúc chia ứng dụng thành các service độc lập, mỗi service có một nhiệm vụ cụ thể và giao tiếp qua API.",
    "nginx": "Nginx là web server và reverse proxy cực kỳ hiệu quả. Thường dùng làm load balancer trước các application server.",
    "default": "Đây là câu trả lời từ Mock LLM. Trong production, thay thế bằng OpenAI/Anthropic API để có câu trả lời thực tế.",
}


def ask(question: str) -> str:
    """Mock LLM - trả về câu trả lời giả lập."""
    time.sleep(0.1)  # Simulate network latency
    q_lower = question.lower()
    for keyword, response in _RESPONSES.items():
        if keyword in q_lower:
            return response
    return _RESPONSES["default"]
