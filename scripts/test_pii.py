import json
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app

def test_pii():
    client = TestClient(app)
    fake_pii_message = (
        "Xin chào, email của tôi là nguyenvana@example.com, "
        "số điện thoại 0987654321. "
        "Số CCCD của tôi là 030012345678. "
        "Thẻ tín dụng 4123-4567-8901-2345."
    )
    
    log_file = Path("data/logs.jsonl")
    lines_before = len(log_file.read_text(encoding="utf-8").splitlines()) if log_file.exists() else 0
    
    print("=== INPUT TEST CHỨA PII GIẢ ===")
    print(fake_pii_message)
    print("\n=== ĐANG GỬI REQUEST ĐẾN API ===")
    
    response = client.post("/chat", json={
        "user_id": "test_user_pii",
        "session_id": "session_test",
        "feature": "qa",
        "message": fake_pii_message
    })
    
    print(f"Status: {response.status_code}")
    
    print("\n=== LOG ĐẦU RA (data/logs.jsonl) ===")
    if log_file.exists():
        lines_after = log_file.read_text(encoding="utf-8").splitlines()
        for line in lines_after[lines_before:]:
            try:
                parsed = json.loads(line)
                print(json.dumps(parsed, indent=2, ensure_ascii=False))
            except Exception:
                print(line)

if __name__ == "__main__":
    test_pii()
