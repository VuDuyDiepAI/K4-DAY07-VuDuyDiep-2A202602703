# Benchmark queries — ViRHE4QA

Bộ 5 câu hỏi đánh giá thống nhất của nhóm. Đáp án vàng và tài liệu nguồn được nhóm cung cấp; metadata filter được giữ đúng theo từng câu hỏi.

| # | Audience | Query | Gold answer | Document | Metadata filter |
|---:|---|---|---|---|---|
| 1 | `student` | Trường hợp nào khiến giảng viên bị đưa ra khỏi quy hoạch giảng dạy của một môn học? | GVMH/TGMH có kết quả khảo sát giảng dạy chưa được sinh viên hài lòng và có nhiều nhận xét không tốt (theo quy định hiện hành về khảo sát giảng dạy) trong hai lần liên tiếp thì bị đưa ra khỏi quy hoạch giảng dạy của môn học đó trong một học kỳ | `quy-che-dao-tao-chinh-quy` | `{"audience":"student"}` |
| 2 | `student` | Bộ phận nào của Trường sẽ xem xét các trường hợp có lí do chính đáng để vắng thi giữa kỳ? | P.ĐTĐH | `quy-dinh-to-chuc-thi` | `{}` |
| 3 | `student` | Thời hạn lưu trữ đề thi các môn học hệ đại học chính quy của Trường là bao lâu? | 9 năm | `quy-dinh-khoa-luan-tot-nghiep` | `{}` |
| 4 | `staff` | Sinh viên thuộc chương trình tài năng có các hình thức nào? | chính thức và dự bị | `quy-trinh-phan-cong-can-bo-coi-thi` | `{}` |
| 5 | `student` | Trong các thành phần điểm của điểm môn học thì điểm giữa kỳ có tên gọi khác là gì? | điểm thi giữa học phần | `quy-dinh-khoa-luan-tot-nghiep` | `{}` |
