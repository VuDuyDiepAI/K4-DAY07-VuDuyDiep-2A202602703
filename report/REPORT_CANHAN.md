# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Vũ Duy Điệp<br>
**Nhóm:** [Tên nhóm]<br>
**Ngày:** [Ngày nộp]

> Báo cáo dùng bộ dữ liệu `data/university` gồm 8 tài liệu quy định. Phần benchmark dùng chung 5 câu hỏi tại `data/university/BENCHMARK.md`. Phần thử nghiệm cá nhân sử dụng `RecursiveChunker`; phần đóng góp trong báo cáo nhóm của tôi là `SentenceChunker`.

## 1. Khởi động (Warm-up) — Cá nhân

### Độ tương tự cosine

Độ tương tự cosine cao nghĩa là hai embedding có hướng gần nhau trong không gian vector; với embedding văn bản, điều này thường biểu thị hai câu có nội dung hoặc ý nghĩa gần nhau. Điểm cao không bắt buộc hai câu giống từ ngữ hay có cùng độ dài.

Ví dụ có độ tương tự cao:

- Câu A: “Làm thế nào để đăng ký thêm một học phần?”
- Câu B: “Tôi muốn bổ sung môn học vào kế hoạch học kỳ.”

Hai câu cùng diễn đạt nhu cầu đăng ký/bổ sung học phần. Ví dụ có độ tương tự thấp là “Quy trình đăng ký học phần diễn ra như thế nào?” và “Thư viện mở cửa vào những khung giờ nào?”, vì chúng thuộc hai nghiệp vụ khác nhau.

Cosine similarity phù hợp hơn Euclidean distance vì nó so sánh hướng vector, ít bị ảnh hưởng bởi độ lớn vector. Với embedding đã chuẩn hóa, dot product tương đương cosine similarity.

### Bài toán chunking

Với tài liệu 10.000 ký tự, `chunk_size=500`, `overlap=50`:

```text
ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = 23 chunks
```

Nếu `overlap=100`:

```text
ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = 25 chunks
```

Overlap lớn hơn tạo thêm chunk nhưng giúp giữ thông tin ở ranh giới giữa hai chunk.

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân

### Chunking

`SentenceChunker.chunk` tách văn bản tại khoảng trắng sau dấu kết câu bằng regex `(?<=[.!?])\s+`, rồi gom tối đa `max_sentences_per_chunk` câu. Cách này giữ nguyên câu nhưng có hạn chế với chữ viết tắt như `v.v.`.

Trong benchmark cá nhân, tôi dùng `RecursiveChunker(chunk_size=500)`. Chunker ưu tiên tách theo `\n\n`, `\n`, `. `, khoảng trắng, rồi mới cắt cứng khi cần. Vì vậy một chunk có xu hướng giữ được đoạn/ý hoàn chỉnh hơn cắt theo số ký tự ngay từ đầu.

### EmbeddingStore và metadata

`add_documents` lưu `id`, `content`, `metadata` và embedding của từng `Document`; metadata luôn giữ `doc_id` để truy vết nguồn. `search` nhúng câu hỏi rồi xếp hạng bằng dot product/cosine similarity. `search_with_filter` lọc metadata trước khi xếp hạng, nên có thể loại tài liệu sai đối tượng. Câu 1 của benchmark dùng thật filter `{"audience":"student"}`.

`delete_document` xóa tất cả chunk có cùng `metadata['doc_id']`; nếu không tìm thấy tài liệu thì trả về `False`.

### KnowledgeBaseAgent

`answer` lấy các chunk top-k, đánh số và đưa vào phần `Context` của prompt. Prompt yêu cầu chỉ trả lời dựa trên ngữ cảnh đã truy xuất và nêu rõ khi ngữ cảnh không đủ. Hàm nhận `metadata_filter` để filter được áp dụng thống nhất từ truy xuất đến trả lời.

## 3. Hoàn thiện code (Core Implementation) — Cá nhân

Kết quả kiểm thử đã chạy:

```text
pytest tests/ -v

=============================== 42 passed in 0.24s ================================
```

**Số bài test vượt qua: 42 / 42.**

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân

Kết quả dùng `LocalEmbedder` với `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`. Quy ước của lần chạy: score từ `0.20` trở lên là “cao”.

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|---:|---|---|---|---:|---|
| 1 | Làm thế nào để đăng ký thêm một học phần? | Tôi muốn bổ sung môn học vào kế hoạch học kỳ. | cao | 0.5490 | Có |
| 2 | Điều kiện xét tốt nghiệp gồm những gì? | Quy trình phân công cán bộ coi thi ra sao? | thấp | 0.4233 | Không |
| 3 | Cách tính điểm trung bình học kỳ như thế nào? | Công thức tính ĐTBHK là gì? | cao | 0.2182 | Có |
| 4 | Người học sử dụng hệ thống dạy học trực tuyến như thế nào? | Khi nào văn bằng hoặc chứng chỉ bị thu hồi? | thấp | 0.1355 | Có |
| 5 | Giảng viên cần đáp ứng tiêu chuẩn nào để dạy môn học? | Yêu cầu đối với trợ giảng môn học là gì? | cao | 0.7239 | Có |

Cặp 2 là kết quả bất ngờ nhất: hai nghiệp vụ khác nhau vẫn có score `0.4233`. Điều này cho thấy score cần được đọc cùng nội dung và phân bố điểm, không nên dùng riêng một ngưỡng cố định để kết luận về ngữ nghĩa.

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân

**Cấu hình chạy:** `LocalEmbedder (sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2) + RecursiveChunker(chunk_size=500)` trên 8 tài liệu, tạo **1.583 chunks**.

| # | Câu hỏi | Top-1 chunk truy xuất được (tóm tắt) | Score | Có liên quan? | Câu trả lời Agent (tóm tắt) |
|---:|---|---|---:|---|---|
| 1 | Quy trình hoãn thi giữa kỳ cần thực hiện như thế nào? | Nộp đơn kèm minh chứng cho Phòng Đào tạo Đại học trong 03 ngày kể từ ngày thi. | 0.6980 | Có | Chứa đúng quy trình và đáp án vàng. |
| 2 | Bộ phận nào xem xét trường hợp có lí do chính đáng để vắng thi giữa kỳ? | Trường hợp có lí do chính đáng: sinh viên làm đơn kèm minh chứng; P.ĐTĐH xem xét. | 0.7894 | Có | Chứa đúng `P.ĐTĐH`. |
| 3 | Thời hạn lưu trữ đề thi là bao lâu? | Hồ sơ phân công ra/nhận đề thi được lưu trữ 9 năm. | 0.8240 | Có | Chứa đúng `9 năm`. |
| 4 | Sinh viên chương trình tài năng có các hình thức nào? | Mô tả học phần tài năng và học phần tiên tiến. | 0.7893 | Không | Không chứa “chính thức và dự bị”. |
| 5 | KLTN là viết tắt của cụm từ nào? | Tiêu đề “Điều 8. Phản biện KLTN”. | 0.6939 | Liên quan một phần | Agent dùng ngữ cảnh top-3 và trả lời đúng “Khóa luận tốt nghiệp”. |

**Tổng kết benchmark đã chạy:**

- Top-3 có đúng tài liệu nguồn: **4 / 5**.
- Câu trả lời Agent chứa đáp án vàng: **4 / 5**.
- Đúng cả truy xuất và đáp án: **4 / 5**.
- Điểm truy xuất theo rubric 2 điểm/câu: **8 / 10**.

Câu 1 xác nhận filter `{"audience":"student"}` vẫn trả đúng tài liệu và đúng đoạn nguồn. Câu 4 là lỗi còn lại: top-3 nghiêng về các đoạn nói chung về học phần/chương trình tài năng, nhưng không tới đoạn có hai hình thức “chính thức và dự bị”. Kết quả cho thấy chất lượng mô hình đã đủ tốt với các thông tin cụ thể, nhưng corpus có các đoạn tương tự/lặp giữa tài liệu nên vẫn cần tách theo điều khoản và làm sạch dữ liệu để nâng độ chính xác.

## Tự đánh giá (Phần cá nhân)

| Tiêu chí | Điểm tự đánh giá |
|---|---:|
| Khởi động | 5 / 5 |
| Hướng tiếp cận của tôi | 10 / 10 |
| Hoàn thiện code — tests | 30 / 30 |
| Dự đoán độ tương tự | 5 / 5 |
| Kết quả truy xuất của tôi | 8 / 10 |
| **Tổng phần cá nhân** | **58 / 60** |
