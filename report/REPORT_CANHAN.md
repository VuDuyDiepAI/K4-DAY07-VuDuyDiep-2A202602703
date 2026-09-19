# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Vũ Duy Điệp
**Nhóm:** [Tên nhóm]
**Ngày:** [Ngày nộp]

> Báo cáo này trình bày phần lập trình và thử nghiệm cá nhân. Chiến lược nhóm của tôi là SentenceChunker; thử nghiệm cá nhân trong báo cáo này dùng RecursiveChunker kết hợp LocalEmbedder để so sánh với MockEmbedder.

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine

**Độ tương tự cosine cao nghĩa là gì?**

Hai embedding có hướng gần nhau trong không gian vector, vì vậy hai đoạn văn có xu hướng tương tự về nội dung hoặc ngữ nghĩa. Điểm cao không có nghĩa là hai câu phải giống từng từ hoặc có cùng độ dài.

**Ví dụ có độ tương tự cao:**

- Câu A: Làm thế nào để gia hạn thời gian mượn sách ở thư viện?
- Câu B: Tôi cần kéo dài hạn mượn tài liệu, phải thực hiện ở đâu?
- Lý do: Hai câu diễn đạt khác nhau nhưng cùng ý định hỏi quy trình gia hạn mượn tài liệu.

**Ví dụ có độ tương tự thấp:**

- Câu A: Quy trình đăng ký học phần diễn ra như thế nào?
- Câu B: Thư viện mở cửa vào những khung giờ nào?
- Lý do: Một câu hỏi nghiệp vụ đăng ký học, câu còn lại hỏi vận hành thư viện.

**Vì sao cosine similarity phù hợp hơn Euclidean distance cho text embeddings?**

Cosine so sánh hướng của vector nên ít bị ảnh hưởng bởi độ lớn vector, vốn có thể thay đổi theo độ dài văn bản. Khi embedding đã chuẩn hóa, dot product chính là cosine similarity.

### Bài toán chunking

**Tài liệu 10.000 ký tự, `chunk_size=500`, `overlap=50`:**

`ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = 23` chunks.

**Nếu `overlap=100`:**

`ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = 25` chunks. Overlap lớn hơn làm tăng số chunk nhưng giúp giữ thông tin tại ranh giới giữa hai chunk.

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

### Chunking

**`SentenceChunker.chunk`**

Tôi dùng regex `(?<=[.!?])\s+` để tách tại khoảng trắng sau dấu kết câu, nhờ đó vẫn giữ dấu câu trong sentence. Các câu được gom theo `max_sentences_per_chunk`; text rỗng trả về danh sách rỗng. Hạn chế của cách này là chưa phân biệt tốt chữ viết tắt như `v.v.` hoặc dấu chấm của số thập phân.

**`RecursiveChunker.chunk` / `_split`**

Chunker thử lần lượt các separator `\n\n`, `\n`, `. `, khoảng trắng và cuối cùng cắt cứng theo ký tự. Nếu đoạn không dài hơn `chunk_size` thì đó là base case; nếu quá dài, thuật toán đệ quy chuyển sang separator có ưu tiên thấp hơn. Separator được gắn lại khi ghép đoạn để hạn chế mất cấu trúc văn bản.

### EmbeddingStore

**`add_documents` và `search`**

Mỗi `Document` được lưu thành record gồm id, content, metadata và embedding; metadata luôn có `doc_id` để truy vết tài liệu gốc. Query được nhúng rồi xếp hạng bằng dot product. Với embedding chuẩn hóa của MockEmbedder hoặc LocalEmbedder, dot product tương ứng cosine similarity.

**`search_with_filter` và `delete_document`**

`search_with_filter` lọc metadata trước khi xếp hạng để các kết quả sai audience không chiếm top-k. `delete_document` xóa toàn bộ chunk có cùng `metadata['doc_id']` và trả về `False` nếu tài liệu không tồn tại.

### KnowledgeBaseAgent

`answer` lấy top-k chunk, đánh số rồi ghép vào `Context` của prompt. Prompt yêu cầu Agent chỉ dùng ngữ cảnh được truy xuất và nêu rõ khi thiếu thông tin. Hàm cũng nhận `metadata_filter` để câu trả lời có thể dùng cùng điều kiện lọc với truy xuất.

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Kết quả kiểm thử đã chạy:

```text
pytest tests/ -v

=============================== 42 passed in 0.24s ================================
```

**Số bài test vượt qua:** **42 / 42**.

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

Kết quả dưới đây dùng `LocalEmbedder` với model `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`. Quy ước của lần chạy: score từ `0.20` trở lên là “cao”.

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|---:|---|---|---|---:|---|
| 1 | Làm thế nào để đăng ký thêm một học phần? | Tôi muốn bổ sung môn học vào kế hoạch học kỳ. | cao | 0.5490 | Có |
| 2 | Điều kiện xét tốt nghiệp gồm những gì? | Quy trình phân công cán bộ coi thi ra sao? | thấp | 0.4233 | Không |
| 3 | Cách tính điểm trung bình học kỳ như thế nào? | Công thức tính ĐTBHK là gì? | cao | 0.2182 | Có |
| 4 | Người học sử dụng hệ thống dạy học trực tuyến như thế nào? | Khi nào văn bằng hoặc chứng chỉ bị thu hồi? | thấp | 0.1355 | Có |
| 5 | Giảng viên cần đáp ứng tiêu chuẩn nào để dạy môn học? | Yêu cầu đối với trợ giảng môn học là gì? | cao | 0.7239 | Có |

**Nhận xét:** Cặp 2 bất ngờ nhất vì hai nghiệp vụ khác nhau vẫn có score 0.4233. Ngược lại, cặp 1 và 5 được nhận diện đúng với score khá cao. LocalEmbedder phản ánh ngữ nghĩa tốt hơn MockEmbedder, nhưng ngưỡng 0.20 quá thấp để kết luận hai câu thật sự tương tự; score cần được đọc cùng nội dung câu hỏi.

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

**Cấu hình chạy:** `LocalEmbedder (sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2) + RecursiveChunker(chunk_size=500)` trên 8 tài liệu, tạo 2.763 chunks.

| # | Câu hỏi | Top-1 chunk (tóm tắt) | Score | Liên quan? | Câu trả lời Agent |
|---:|---|---|---:|---|---|
| 1 | Trường hợp nào khiến giảng viên bị đưa ra khỏi quy hoạch giảng dạy của một môn học? | Nội dung chuyển từ đào tạo chính quy sang từ xa. | 0.7258 | Không; đúng tài liệu nguồn nhưng sai nội dung. | Không chứa điều kiện “hai lần liên tiếp”. |
| 2 | Bộ phận nào của Trường sẽ xem xét các trường hợp có lí do chính đáng để vắng thi giữa kỳ? | Sinh viên làm đơn kèm minh chứng; `P.ĐTĐH` xem xét. | 0.7894 | Có | Chứa đúng `P.ĐTĐH`. |
| 3 | Thời hạn lưu trữ đề thi các môn học hệ đại học chính quy của Trường là bao lâu? | Hồ sơ đề thi lưu bản giấy tại Phòng Đào tạo Đại học trong 9 năm. | 0.8240 | Có | Chứa đúng `9 năm`. |
| 4 | Sinh viên thuộc chương trình tài năng có các hình thức nào? | Mô tả học phần tài năng và học phần tiên tiến. | 0.7893 | Không | Không chứa `chính thức và dự bị`. |
| 5 | Trong các thành phần điểm của điểm môn học thì điểm giữa kỳ có tên gọi khác là gì? | Quy định chữ ký trên bảng điểm và nhập điểm khóa luận. | 0.6374 | Không | Không chứa `điểm thi giữa học phần`. |

**Tổng kết:**

- Top-3 có đúng tên tài liệu nguồn: **3 / 5**.
- Chunk liên quan trực tiếp và Agent chứa gold answer: **2 / 5** (câu 2, 3).
- Điểm truy xuất theo rubric 2 điểm/câu: **4 / 10**.

**Điều học được:** So với MockEmbedder, LocalEmbedder cải thiện từ 0/5 lên 2/5 câu trả lời đúng. Tuy nhiên, câu 1 có đúng `doc_id` nhưng chunk sai nội dung, còn câu 4–5 có score cao nhưng không trả lời được gold answer. Vì vậy cần đánh giá nội dung chunk, giữ metadata filter và tiếp tục làm sạch corpus/tách theo điều khoản thay vì chỉ dựa vào score.

## Tự đánh giá (Phần cá nhân)

| Tiêu chí | Điểm tự đánh giá |
|---|---:|
| Khởi động | 5 / 5 |
| Hướng tiếp cận của tôi | 10 / 10 |
| Hoàn thiện code — tests | 30 / 30 |
| Dự đoán độ tương tự | 5 / 5 |
| Kết quả truy xuất của tôi | 4 / 10 |
| **Tổng phần cá nhân** | **54 / 60** |
