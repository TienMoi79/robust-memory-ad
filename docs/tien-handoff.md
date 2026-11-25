# Việc của Tiến và trạng thái bàn giao

Cập nhật **25/11/2026**, đối chiếu `Tuan2_Le-Quyet-Tien.md` và `Ke-hoach-tong.md` do Tiến cung cấp. Hai file nguồn giữ trong `.local/handoff/` ở bản Desktop, không đưa toàn bộ kế hoạch các thành viên lên repo thay Huy.

## Phạm vi của Tiến

Bạn phụ trách **định nghĩa phép đo, dung lượng bank/index, bộ nhớ đỉnh, độ trễ từng ảnh/p50/p95, chi phí chọn coreset, bảng chất lượng theo ngân sách và phần viết phương pháp đo**. Dùng đúng baseline Phúc giao; ghép số chất lượng do Đỗ Hoàng Phúc phụ trách. Huy quyết định phạm vi, viết bộ chọn mới và ghép đề cương/bản thảo.

Hạn gần nhất **Chủ nhật 29/11/2026**: giao bảng hiệu năng truy được về log, hoặc ghi chính xác mục bị chặn, người cần hỗ trợ và lịch chạy bù. Mục tiêu đề cương 3–5 trang là của nhóm/Huy, không phải Tiến tự làm toàn bộ.

## Trạng thái công việc

| Việc | Trạng thái | Bằng chứng / bước còn lại |
|---|---|---|
| Clone repo trên Desktop, nhánh `profiling/pilot` | Đã làm | Repo nhóm ban đầu chỉ README; không dùng nhầm dự án ProJeat |
| Thiết bị đo | Huy đã chốt L4 trên Colab qua Tiến | RAM/VRAM/driver/thư viện lấy từ runtime thực, chưa có phiên L4 |
| `docs/profiling.md`, đơn vị, mẫu CSV | Đã soạn | Ranh giới và tolerance còn cần xác nhận |
| Đồng hồ, p50/p95, warm-up, log thô | Đã thử CPU | 10 warm-up + 50 mẫu giả lập; **không phải kết quả PatchCore** |
| Notebook Colab L4 | Đã chuẩn bị | Kiểm GPU/CUDA trước khi đo; chưa chạy phiên Colab |
| Full/random/greedy, so điểm trước đo | Chờ Hữu Huỳnh Phúc | Phúc đang làm; Tiến đồng ý tạm chờ |
| Bank/index thật, peak VRAM/RAM thật, p50/p95 thật | Chưa đo | Cần baseline và Colab L4; không điền số giả |
| Chi phí chọn coreset | Có helper, chưa đo thật | Cần ma trận features, lệnh chọn và ranh giới lựa chọn |
| Bảng chất lượng theo ngân sách | Có script ghép, chờ quality.csv | Cần Đỗ Hoàng Phúc giao đúng run ID và nhóm ảnh |
| Pull request | Xem trạng thái PR trên GitHub | Tài khoản Tiến chỉ có READ ở repo nhóm; dùng fork, không merge main |

## Bạn chuyển các câu này cho đúng người

**Hữu Huỳnh Phúc — đợi anh ấy làm xong rồi hỏi:**

> Khi baseline sẵn, gửi Tiến commit/nhánh chính xác, môi trường cài được trên Colab L4, lệnh nạp bank và suy luận một ảnh; full/random/greedy bank hoặc index kèm số patch/seed/budget; danh sách ảnh có thứ tự và predictions.csv có run_id,image_id,image_score,map_path. Nhờ xác nhận preprocessing, dtype, resolution, điểm nạp bank, hàm suy luận, CPU/GPU của FAISS, tolerance điểm và việc output đã về CPU chưa. Để đo coreset cần feature matrix sẵn và lệnh chọn hoặc log thời gian chọn gốc.

**Huy — máy L4 đã chốt, còn các quyết định này:**

> Tiến đề xuất batch 1, tính từ ảnh đã decode trong RAM, gồm preprocess → chuyển thiết bị → backbone → query → score/map sẵn; bỏ đọc đĩa/decode. Có tính chuyển kết quả về CPU không? Nhờ chốt nhóm sản phẩm/split/nhóm ánh sáng, ngân sách patch, nơi lưu bank/log chung. Nếu FAISS chạy GPU, dùng công cụ nào để đo peak VRAM cấp tiến trình? Nếu chưa có L4 trước hạn, ai hỗ trợ phiên chạy và hạn chạy bù?

**Đỗ Hoàng Phúc — có thể thống nhất định dạng trước khi baseline xong:**

> Cho Tiến quy ước image_group và quality.csv dùng cùng run_id với baseline, kèm seed/budget, split/nhóm ánh sáng, ngưỡng và các chỉ số có tử số/mẫu số phù hợp. Nếu một run có nhiều ngưỡng/nhóm, nhờ xác định hàng dùng ghép để không trùng khóa. Tiến sẽ ghép hiệu năng và giữ riêng thiết bị/lượt đo.

Không cần hỏi Nam để mở phần profiling. Không tự đổi dữ liệu hoặc dựng benchmark khác khi baseline chưa sẵn.

## Lịch tiếp theo

| Mốc | Việc của Tiến |
|---|---|
| 25/11/2026 | Chốt giao thức, tự kiểm dụng cụ, gửi PR phần độc lập |
| 26–27/11/2026 | Nhận full/random/greedy từ Phúc; so điểm trước khi đo; random/greedy cùng số patch |
| 28/11/2026 | Đo trên L4 cùng điều kiện, rà p95/outlier và ghép chất lượng nếu đã có |
| 29/11/2026 | Giao Huy bảng + lệnh + log thô; ghi thiếu gì, ai phụ trách, hạn bổ sung |
| 13/12/2026 | Lặp một cấu hình ở hai phiên; cùng nhóm chốt ngân sách và điều kiện chấp nhận so sánh |
| 09/01/2027 | Đo bộ chọn mới: chi phí một lần và mỗi ảnh, ghép lỗi nhỏ/báo động giả |
| 06/02/2027 | Hoàn tất bảng benchmark đã khóa, giải thích trường hợp giảm MB nhưng p95 còn cao |
| 28/02/2027 | Viết thiết bị, phương pháp và đánh đổi; đối chiếu mọi số bảng/hình với log |

## Mẫu nhật ký để gửi Huy

| Ngày | Người | Việc | Kết quả | Còn vướng | Bước tiếp / hạn |
|---|---|---|---|---|---|
| 25/11/2026 | Lê Quyết Tiến | Chuẩn bị profiling pilot | docs/profiling.md, notebook L4, bộ log/p50/p95 và phép thử CPU | Phúc đang làm baseline; còn chốt ranh giới/đầu ra CPU và công cụ peak GPU ngoài PyTorch | Nhận baseline 26–27/11, đo trước 29/11 nếu đầu vào sẵn |

Chỉ thêm dòng này vào kế hoạch tổng trên repo khi Huy đưa file kế hoạch lên và thống nhất vị trí. Không ghi đè kế hoạch chung.
