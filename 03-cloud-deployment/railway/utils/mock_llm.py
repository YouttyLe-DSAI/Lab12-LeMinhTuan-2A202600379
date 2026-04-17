import time

def ask(question: str) -> str:
    """Mock LLM response for local testing/demo"""
    # Simulate thinking time
    time.sleep(1)
    
    responses = {
        "hello": "Xin chào! Tôi là AI Agent từ VinUni. Tôi có thể giúp gì cho bạn?",
        "who are you": "Tôi là AI Agent được cấu hình để chạy trên môi trường Production.",
        "default": "Đây là câu trả lời từ AI agent (mock). Trong production, đây sẽ là response từ OpenAI/Anthropic."
    }
    
    q_lower = question.lower()
    for key in responses:
        if key in q_lower:
            return responses[key]
            
    return responses["default"]
