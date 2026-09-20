# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** [Tên nhóm]
**Thành viên:** Võ Phú Hãn (2A202602628), Vũ Duy Điệp (2A202602703), Võ Minh Quân (2A202602429)
**Ngày:** 2026-09-19

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Quy định đào tạo và dịch vụ học vụ đại học

**Tại sao nhóm chọn chủ đề này?**
> Nhóm chọn chủ đề này vì phù hợp trực tiếp với biến thể K4-L3A và có câu hỏi thực tế cho sinh viên, giảng viên và cán bộ. ViRHE4QA có context, câu hỏi và gold answer tiếng Việt, phù hợp để thử retrieval và metadata filtering.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Quy chế đào tạo chính quy | https://github.com/DoPhamPhucTinh/R2GQA | 2026-09-19 / not-stated | 165112 | `{"audience":"student","department":"Phòng Đào tạo","category":"Quy chế đào tạo"}` |
| 2 | Quy định tổ chức thi | https://github.com/DoPhamPhucTinh/R2GQA | 2026-09-19 / not-stated | 172845 | `{"audience":"student","department":"Phòng Khảo thí","category":"Kiểm tra và thi cử"}` |
| 3 | Quy định khóa luận tốt nghiệp | https://github.com/DoPhamPhucTinh/R2GQA | 2026-09-19 / not-stated | 81053 | `{"audience":"student","department":"Phòng Đào tạo","category":"Đánh giá tốt nghiệp"}` |
| 4 | Quy chế văn bằng, chứng chỉ | https://github.com/DoPhamPhucTinh/R2GQA | 2026-09-19 / not-stated | 127573 | `{"audience":"all","department":"Phòng Đào tạo","category":"Hồ sơ học vụ"}` |
| 5 | Quy định dạy học trực tuyến | https://github.com/DoPhamPhucTinh/R2GQA | 2026-09-19 / not-stated | 90254 | `{"audience":"all","department":"Phòng Đào tạo","category":"Dạy và học"}` |
| 6 | Quy định tiêu chuẩn giảng viên | https://github.com/DoPhamPhucTinh/R2GQA | 2026-09-19 / not-stated | 86554 | `{"audience":"faculty","department":"Phòng Công tác giảng viên","category":"Dạy và học"}` |
| 7 | Quy định công tác giáo trình | https://github.com/DoPhamPhucTinh/R2GQA | 2026-09-19 / not-stated | 114266 | `{"audience":"faculty","department":"Phòng Công tác giảng viên","category":"Dạy và học"}` |
| 8 | Quy trình phân công cán bộ coi thi | https://github.com/DoPhamPhucTinh/R2GQA | 2026-09-19 / not-stated | 54176 | `{"audience":"staff","department":"Phòng Khảo thí","category":"Kiểm tra và thi cử"}` |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `audience` | string | `student`, `faculty`, `staff`, `all` | Lọc theo đối tượng áp dụng |
| `department` | string | `Phòng Đào tạo`, `Phòng Khảo thí` | Lọc theo đơn vị phụ trách |
| `category` | string | `Dạy và học`, `Kiểm tra và thi cử` | Lọc theo loại quy định |
| `language` | string | `vi` | Xác định ngôn ngữ corpus |
| `source_url` | string | GitHub R2GQA | Truy vết nguồn |
| `retrieved_at` | date | `2026-09-19` | Thời điểm lấy dữ liệu |
| `document_version` | string | `not-stated` | Không bịa version khi nguồn không nêu |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| Quy chế đào tạo chính quy | FixedSizeChunker (`fixed_size`) | 331 | 498.83 | Có thể cắt giữa điều khoản |
| Quy chế đào tạo chính quy | SentenceChunker (`by_sentences`) | 116 | 301.48 | Có, ở mức khá — không cắt giữa câu; heading/Điều có thể tách khỏi nội dung. |
| Quy chế đào tạo chính quy | RecursiveChunker (`recursive`) | 543 | 302.51 | Giữ cấu trúc tốt hơn fixed-size |
| Quy định tổ chức thi | FixedSizeChunker (`fixed_size`) | 346 | 499.55 | Có nguy cơ cắt giữa quy trình |
| Quy định tổ chức thi | SentenceChunker (`by_sentences`) | 218 | 238.42 | Có, ở mức khá — giữ câu nguyên vẹn; ngữ cảnh giữa các câu có thể bị tách. |
| Quy định tổ chức thi | RecursiveChunker (`recursive`) | 568 | 302.73 | Cân bằng hơn giữa độ dài và cấu trúc |
| Quy định khóa luận tốt nghiệp | FixedSizeChunker (`fixed_size`) | 163 | 497.26 | Chunk lớn, dễ chứa nhiều ý |
| Quy định khóa luận tốt nghiệp | SentenceChunker (`by_sentences`) | 100 | 245.02 | Có, ở mức khá — giữ trọn câu; một Điều dài có thể bị tách thành nhiều chunk. |
| Quy định khóa luận tốt nghiệp | RecursiveChunker (`recursive`) | 254 | 317.56 | Giữ đoạn/điều tốt hơn baseline |

**Lần chạy SentenceChunker của thành viên 2 trên 3 tài liệu:**

- Cấu hình: `SentenceChunker(max_sentences_per_chunk=3)`; `chunk_size` không áp dụng cho chiến lược này.
- Tổng số chunk: **484**.
- Độ dài trung bình: **258,72**.
- Nhận xét: chunk kết thúc tại ranh giới câu, giữ ý trọn vẹn tốt hơn cách cắt theo số ký tự.

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — Võ Phú Hãn (2A202602628)**
- **Loại chiến lược:** FixedSizeChunker với overlap
- **Mô tả & lý do chọn cho chủ đề này:** Chia văn bản theo kích thước cố định, có thể cấu hình overlap để giữ ngữ cảnh tại ranh giới chunk. Đây là baseline đơn giản, dễ tái lập để so sánh với hai chiến lược còn lại.
- **Cấu hình:** `FixedSizeChunker(chunk_size=500, overlap=50)`.
- **Code snippet (nếu custom):**
```python
# Dán mã nguồn (implementation) vào đây
```

**Thành viên 2 — Vũ Duy Điệp (2A202602703)**
- **Loại chiến lược:** SentenceChunker (`max_sentences_per_chunk=3`)
- **Mô tả & lý do chọn:** Trên ba tài liệu nhóm chọn — Quy chế đào tạo chính quy, Quy định tổ chức thi và Quy định khóa luận tốt nghiệp — chiến lược này tạo 484 chunk, độ dài trung bình 258,72 ký tự. Mỗi chunk ghép tối đa ba câu và không cắt giữa câu, phù hợp với văn bản quy chế vì điều kiện, chủ thể và thời hạn thường trải qua nhiều câu liên tiếp. Đánh đổi là ba câu cạnh nhau vẫn có thể thuộc hai ý khác nhau; kết quả benchmark được dùng để kiểm tra đánh đổi này.
- **Code snippet (nếu custom):**
```python
SentenceChunker(max_sentences_per_chunk=3)
```

**Thành viên 3 — Võ Minh Quân (2A202602429)**
- **Loại chiến lược:** RecursiveChunker (`chunk_size=500`)
- **Mô tả & lý do chọn:** Tách đệ quy theo separator `['\\n\\n', '\\n', '. ', ' ', '']`, ưu tiên đoạn văn, dòng và câu trước khi fallback về ranh giới ký tự. Cơ chế greedy merge gom các mảnh liền kề sát ngưỡng 500 ký tự, giảm mảnh vụn và giữ ngữ cảnh điều khoản tốt hơn.
- **Bài toán overlap:** Với tài liệu 10.000 ký tự, `chunk_size=500`, `overlap=50`, stride là 450 và cần 23 chunks. Nếu overlap tăng lên 100, stride còn 400 và số chunk tăng lên 25; đổi lại ranh giới điều khoản được giữ ngữ cảnh tốt hơn.
- **Code snippet (nếu custom):**
```python
RecursiveChunker(chunk_size=500)
```

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Võ Phú Hãn (2A202602628) | Fixed-size | 6 / 10 (dự kiến) | Baseline đơn giản, có overlap cấu hình được | Có thể cắt giữa điều khoản |
| Vũ Duy Điệp (2A202602703) | Sentence | 6/ 10 (dự kiến) | Giữ ranh giới câu tự nhiên | Có thể gom nhiều ý vào một chunk |
| Võ Minh Quân (2A202602429) | Recursive | 8 / 10 (dự kiến) | Ưu tiên paragraph/newline/sentence | Phụ thuộc separator và greedy merge |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> Dự kiến RecursiveChunker và SentenceChunker sẽ tốt hơn FixedSizeChunker vì corpus có nhiều điều khoản và đoạn văn dài. RecursiveChunker có lợi thế giữ cấu trúc đoạn, còn SentenceChunker giữ câu tự nhiên; nhóm ưu tiên RecursiveChunker nếu kết quả top-3 tương đương vì chunk bám cấu trúc quy định tốt hơn.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Metadata filter | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-----------------|-------------------------------|--------------------------|
| 1 | Khi sinh viên xin hoãn thi giữa kỳ, hồ sơ cần được xử lý như thế nào? | `{"audience":"student"}` | Sinh viên có lý do chính đáng không thể dự thi giữa kỳ phải nộp đơn kèm minh chứng cho Phòng Đào tạo Đại học trong vòng 03 ngày kể từ ngày thi. | Điều tổng hợp S1 — Quy chế đào tạo chính quy |
| 2 | Bộ phận nào của Trường sẽ xem xét các trường hợp có lí do chính đáng để vắng thi giữa kỳ? | `{}` | P.ĐTĐH | Điều 21 — Quy định tổ chức thi |
| 3 | Thời hạn lưu trữ đề thi các môn học hệ đại học chính quy của Trường là bao lâu? | `{}` | 9 năm | Điều 21 — Quy định khóa luận tốt nghiệp |
| 4 | Sinh viên thuộc chương trình tài năng có các hình thức nào? | `{}` | chính thức và dự bị | Điều 2 — Quy trình phân công cán bộ coi thi |
| 5 | Trong các thành phần điểm của điểm môn học thì điểm giữa kỳ có tên gọi khác là gì? | `{}` | điểm thi giữa học phần | Điều 11 — Quy định khóa luận tốt nghiệp |

> **Note về metadata filter:** Câu 1 được chạy hai lần với cùng một query. Filter `{"audience":"student"}` trả về trách nhiệm của sinh viên trong Điều tổng hợp S1; filter `{"audience":"faculty"}` trả về trách nhiệm của giảng viên trong Điều tổng hợp F1. Hai gold answer đều được trích nguyên văn từ hai file Markdown, nhưng đây là dữ liệu synthetic do nhóm thêm để kiểm thử filter, không phải quy định chính thức của trường.

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | RecursiveChunker | Có, dự kiến cả hai audience | Filter định hướng đúng điều khoản student/faculty |
| 2 | SentenceChunker | Có, dự kiến | Query ngắn, answer nằm trong một câu |
| 3 | RecursiveChunker | Có, dự kiến | Giữ nguyên section lưu trữ |
| 4 | SentenceChunker | Có, dự kiến | Answer ngắn và nằm trọn trong một câu |
| 5 | RecursiveChunker | Có, dự kiến | Giữ cụm thuật ngữ trong cùng section |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Kết quả dự kiến: FixedSizeChunker khoảng **3/5** câu đúng trong top-3, SentenceChunker khoảng **4/5**, RecursiveChunker khoảng **4/5**. Riêng query metadata dự kiến cải thiện rõ khi filter đúng `audience`, vì hai điều khoản synthetic có cùng chủ đề nhưng khác trách nhiệm.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> Case metadata chạy cùng một query với `audience=student` và `audience=faculty`, nên có thể kiểm tra trực tiếp việc filter điều hướng đến trách nhiệm khác nhau.

**Bài học rút ra khi so sánh trong nhóm:**
> SentenceChunker giữ ranh giới câu tự nhiên; RecursiveChunker cân bằng giữa cấu trúc và kích thước; FixedSizeChunker dễ tái lập nhưng có thể cắt giữa điều khoản. Kết quả top-3 cần được đọc cùng cấu hình embedding và phạm vi corpus.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Nếu làm lại, nhóm sẽ lưu chunk/embedding sau lần chạy đầu và benchmark trên subset trước, sau đó mới mở rộng sang toàn bộ corpus. Các đoạn synthetic phải luôn được đánh dấu riêng với nguồn ViRHE4QA.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10/ 10 |
| Thiết kế chiến lược (Strategy Design) | 15/ 15 |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10 (dự kiến) |
| Thuyết trình (Demo) | 5/ 5 |
| **Tổng phần nhóm** | **40 / 40 (dự kiến)** |
