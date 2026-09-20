# Benchmark queries — ViRHE4QA

Bộ 5 câu hỏi đánh giá thống nhất của nhóm. Cột `Document` là tài liệu chứa điều khoản/đoạn được dùng làm nguồn chuẩn; `metadata_filter` được áp dụng nguyên trạng khi truy xuất.

| # | Audience | Query | Gold answer | Document | Metadata filter |
|---:|---|---|---|---|---|
| 1 | `student` | Quy trình hoãn thi giữa kỳ cần thực hiện như thế nào? | Nộp đơn kèm minh chứng cho Phòng Đào tạo Đại học trong vòng 03 ngày kể từ ngày thi. | `quy-che-dao-tao-chinh-quy` | `{"audience":"student"}` |
| 2 | `student` | Bộ phận nào của Trường sẽ xem xét các trường hợp có lí do chính đáng để vắng thi giữa kỳ? | P.ĐTĐH | `quy-dinh-to-chuc-thi` | `{}` |
| 3 | `student` | Thời hạn lưu trữ đề thi các môn học hệ đại học chính quy của Trường là bao lâu? | 9 năm | `quy-dinh-khoa-luan-tot-nghiep` | `{}` |
| 4 | `staff` | Sinh viên thuộc chương trình tài năng có các hình thức nào? | chính thức và dự bị | `quy-trinh-phan-cong-can-bo-coi-thi` | `{}` |
| 5 | `student` | KLTN là viết tắt của cụm từ nào? | Khóa luận tốt nghiệp | `quy-dinh-khoa-luan-tot-nghiep` | `{}` |

> **Lưu ý metadata filter:** Câu 1 dùng `{"audience":"student"}` để kiểm thử filter: đoạn nguồn S1 áp dụng cho sinh viên nộp đơn trong 03 ngày. Trong corpus thử nghiệm có một đoạn tổng hợp F1 cho giảng viên; nó không phải quy định chính thức.
