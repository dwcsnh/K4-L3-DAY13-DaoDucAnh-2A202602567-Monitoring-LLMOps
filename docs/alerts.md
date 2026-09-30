# Template Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert 1

- Tên: HighErrorRate
- Severity: Critical
- Duration: 5m
- Kênh thông báo: Slack #alerts
- SLI/SLO liên quan: Error Rate <= 2%
- Điều kiện và thời gian duy trì: error_rate_pct > 2 trong vòng 5 phút
- Ảnh hưởng tới người dùng: Người dùng liên tục nhận được phản hồi lỗi, không thể sử dụng tính năng QA/Summary.
- Ba bước kiểm tra đầu tiên: 1. Kiểm tra logs để xem loại lỗi (error_type); 2. Kiểm tra tải của LLM provider; 3. Kiểm tra kết nối tới Vector DB.
- Mitigation tạm thời: Chuyển sang model dự phòng (fallback) hoặc rollback prompt version.
- Owner: SRE Team

## Alert 2

- Tên: HighLatency
- Severity: Warning
- Duration: 5m
- Kênh thông báo: Slack #alerts
- SLI/SLO liên quan: P95 Latency <= 3000ms
- Điều kiện và thời gian duy trì: p95_latency > 3000 trong 5 phút
- Ảnh hưởng tới người dùng: Người dùng phải đợi rất lâu mới nhận được câu trả lời, gây trải nghiệm kém.
- Ba bước kiểm tra đầu tiên: 1. Xem biểu đồ phân rã latency (TTFT vs Generation); 2. Kiểm tra logs của LLM API; 3. Kiểm tra RAG retrieval time.
- Mitigation tạm thời: Tắt bớt tính năng tốn tài nguyên hoặc scale up/out backend.
- Owner: SRE Team

## Alert 3

- Tên: LowQualityScore
- Severity: Warning
- Duration: 10m
- Kênh thông báo: Slack #alerts
- SLI/SLO liên quan: Quality proxy >= 0.75
- Điều kiện và thời gian duy trì: quality_score_avg < 0.75 trong 10 phút
- Ảnh hưởng tới người dùng: Câu trả lời kém chất lượng, không thỏa mãn nhu cầu.
- Ba bước kiểm tra đầu tiên: 1. Đọc sample logs có chất lượng thấp; 2. Kiểm tra tỉ lệ retrieval success; 3. Xem prompt đang chạy ở version nào.
- Mitigation tạm thời: Rollback về prompt version hoặc LLM model ổn định trước đó.
- Owner: AI Team
