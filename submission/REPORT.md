# Báo cáo cá nhân — K4-L3A Day 13 Monitoring & LLMOps

> Mỗi học viên hoàn thiện một file duy nhất này. Khi dẫn evidence, dùng đường dẫn tương đối, ví dụ `evidence/07-trace-waterfall.png`.

## 1. Thông tin học viên

- **Họ và tên:** Đào Đức Anh
- **MSSV:** 2A202602567
- **Lớp:** K4-L3A
- **Repository URL:** https://github.com/dwcsnh/K4-L3-DAY13-DaoDucAnh-2A202602567-Monitoring-LLMOps.git
- **Commit SHA cuối:**
- **Challenge ID:** day13-k4-l3a-monitoring-llmops-v1
- **Tên project Langfuse cá nhân:** `day13-k4-l3a-2A202602567`

## 2. Evidence index

Điền đúng đường dẫn tới evidence thực tế. Có thể đổi tên hoặc dùng nhiều ảnh nếu cần.

| Evidence | Đường dẫn |
|---|---|
| Pytest cuối | `evidence/01-pytest.png` |
| Log validator | `evidence/02-log-validator.png` |
| Dashboard validator | `evidence/03-dashboard-validator.png` |
| Structured log | `evidence/04-structured-log.png` |
| PII redaction | `evidence/05-pii-redaction.png` |
| Trace list | `evidence/06-trace-list.png` |
| Trace waterfall | `evidence/07-trace-waterfall.png` |
| Trace metadata | `evidence/08-trace-metadata.png` |
| Prompt versions | `evidence/09-prompt-versions.png` |
| Prompt rollback | `evidence/10-prompt-rollback.png` |
| Dashboard runtime | `evidence/11-dashboard-overview.png` |
| Incident metric | `evidence/12-incident-metric.png` |
| Incident log | `evidence/13-incident-log.png` |
| Incident trace | `evidence/14-incident-trace.png` |

## 3. Kết quả kỹ thuật

| Nội dung | Baseline | Kết quả cuối | Nhận xét |
|---|---|---|---|
| `validate_logs.py` | 50/100 | 100/100 | |
| `validate_dashboard.py` | 6/6 | 6/6 | |
| `pytest` | 22 passed | 22 passed | |
| Số traces hợp lệ | | 72 | |
| Số PII leak | | 0 | Đã xử lý bằng middleware/logger scrubbing |
| Latency P95 / TTFT P95 | | 2652 ms / 50 ms | P95 Latency cao do ảnh hưởng từ sự cố `rag_slow` |
| Retrieval success rate | | 100% | |

## 4. Logging và PII

- **Cách tạo/nhận và truyền correlation ID:** Sử dụng `contextvars.ContextVar` để lưu `correlation_id`. Middleware và các hàm xử lý đều access `contextvars.get()` để đảm bảo ID được truyền nhất quán.
- **Các metadata được ghi vào structured log:** `timestamp`, `event`, `severity`, `correlation_id`, `feature`, `latency_ms`, `latency_sec`, `llm_model`, `tokens_input`, `tokens_output`, `cost_usd`, `error`, `user_id`.
- **Cách bảo đảm PII được scrub trước khi ghi:** Hàm `_scrub_pii` trong `app/logger.py` sử dụng regex để tìm và thay thế Email, SĐT, CCCD/CMND, Số thẻ tín dụng bằng `[REDACTED]` trước khi log.
- **Cách kiểm chứng kết quả:** Chạy script `python scripts/validate_logs.py`. Script sẽ đọc file log `data/logs.jsonl` và kiểm tra các yêu cầu: JSON schema, correlation ID, log enrichment và PII scrubbing.

## 5. Tracing và prompt versioning

- **Cách xác nhận traces do chính tôi tạo trong project cá nhân:** Đăng nhập Langfuse project `day13-k4-l3a-<MSSV>` và xem trace.
- **Cấu trúc root/retrieval/generation observations:** Root: agent run, Span: retrieve, Generation: LLM generate.
- **Cách nối trace với log:** Thông qua `correlation_id` chung.
- **Prompt name:** day13-chat
- **Version/label baseline:** v1 / baseline, production
- **Version/label candidate:** v2 / candidate
- **Trace ID của mỗi version:** v1: e3db599399af6e6214c174d3bd1340b1, v2: 9330e84c07100fb0388560a79ce1356c
- **Cách promote và rollback `production`:** Gắn/đổi tag `production` trên Langfuse UI cho version tương ứng.

## 6. Dashboard, SLO và alerts

- **Dashboard và sáu panel:** 1. Latency (TTFT P95/P99), 2. Traffic (QPS), 3. Error rate, 4. Cost/Time, 5. Tokens, 6. Quality proxy.
- **SLO và lý do chọn:** 95% request trả lời < 2s (Latency P95 < 2000ms). Tránh UX kém vì chatbot.
- **Cách tính error budget:** Nếu SLA 99%, cho 1 triệu request thì budget = 10,000 lỗi/tháng.
- **Ba alert và runbook tương ứng:**
  - Alert 1: High Error Rate (> 5% in 5m). Mitigation: Rollback prompt/model.
  - Alert 2: High Latency (P95 > 2s in 5m). Mitigation: Check RAG DB load.
  - Alert 3: Cost Spike (Increase 2x in 30m). Mitigation: Block anomalous token patterns.

## 7. Điều tra challenge

- **Challenge ID:** day13-k4-l3a-monitoring-llmops-v1
- **Khoảng thời gian điều tra:** Quanh mốc 2026-09-30 04:05 UTC (Thời điểm xuất hiện log lỗi/chậm).
- **Triệu chứng từ metrics:** Biểu đồ Latency (đặc biệt là P95/P99) tăng vọt vượt ngưỡng 2000ms, khiến người dùng phải đợi rất lâu.
- **Log line và correlation ID liên quan:** Bắt đầu điều tra từ `correlation_id`: `req-9967819b`. Dòng log ghi nhận hệ thống gặp vấn đề về thời gian phản hồi (chứa event `incident_enabled` với payload `rag_slow` hoặc các request theo sau có `latency_ms` > 2500ms).
- **Trace ID và span gây ảnh hưởng:** Tra cứu bằng ID trên, mở Trace trong Langfuse cho thấy Span `retrieve` (thuộc chức năng RAG) bị kéo dài bất thường (> 2.5 giây), trong khi hàm `generate` (LLM) vẫn hoạt động bình thường.
- **Root cause:** Component Vector Store / RAG bị chậm (sự cố `rag_slow`), trở thành nút thắt cổ chai (bottleneck) làm tăng tổng thời gian phản hồi của request.
- **Fix action:** Gọi API disable incident `rag_slow`. Trong thực tế: Kiểm tra kết nối tới Vector DB, tối ưu hóa index, hoặc restart/scale hệ thống lưu trữ vector.
- **Preventive measure:** Áp dụng cơ chế Timeout nghiêm ngặt (vd: 1-1.5s) cho hàm `retrieve()` kèm Fallback response. Thiết lập cảnh báo (Alert) riêng biệt khi P95 của riêng Span `retrieve` tăng cao. Bổ sung Cache cho các truy vấn phổ biến.

## 8. Giải thích và tự đánh giá

- **Một quyết định kỹ thuật quan trọng và lý do:** Chọn `bind_contextvars` ở mức request (trong middleware và main.py) để đảm bảo mọi log thuộc request đều có đủ context (correlation_id, user_id).
- **Một lỗi/blocker đã gặp:** Lỗi tham số `usage` khi dùng API `update_current_generation` của Langfuse SDK.
- **Cách tìm nguyên nhân và xử lý:** Đọc source code SDK và đổi sang dùng `usage_details`, `cost_details`.
- **Cách hiểu luồng Metrics → Logs → Traces:** Metrics phát hiện dị thường tổng quan -> Logs tìm request cụ thể (qua correlation_id) -> Traces xem chi tiết từng bước (span) bên trong request để tìm nguyên nhân gốc.
- **Vai trò của prompt version, token/cost, SLO hoặc rollback trong vận hành LLM:** Đảm bảo LLM an toàn, kiểm soát chi phí, và có khả năng phục hồi nhanh bằng cách rollback khi có bản cập nhật prompt lỗi.
- **Điều quan trọng nhất đã học:** Cơ chế hoạt động của Context Variables (ContextVars) trong Python để lưu vết request đồng thời.
- **Hạn chế hoặc phần chưa hoàn thành, nếu có:** Chưa áp dụng metric exporter thực tế.

## 9. Checklist trước khi nộp

- [ ] Kết quả và evidence thuộc commit SHA cuối.
- [ ] Tất cả ảnh/output mở được bằng đường dẫn tương đối.
- [ ] Incident evidence nối đúng metric → log → trace.
- [ ] Trace/prompt evidence thuộc project Langfuse cá nhân và ảnh không lộ key/secret.
- [ ] Repository chạy lại được theo README.
- [ ] Không có secret, API key, PII thô hoặc evidence của người khác/lớp khác.
- [ ] URL repo và commit SHA cuối đã được nộp trên LMS/Codelabs.
