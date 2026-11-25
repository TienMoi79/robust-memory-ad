# Quy trình đo bộ nhớ và độ trễ — Lê Quyết Tiến

Trạng thái ngày **25/11/2026**: bộ đo CPU đã tự kiểm; **chưa có số đo PatchCore hoặc L4**.
Theo Huy qua Tiến, máy đo chính thức là **NVIDIA L4 trên Google Colab**.
Hữu Huỳnh Phúc đang làm baseline; phần tích hợp chờ bàn giao, theo thống nhất với Tiến.

[Mở notebook trong Colab](https://colab.research.google.com/github/TienMoi79/robust-memory-ad/blob/profiling/pilot/notebooks/profiling_colab.ipynb) · [Draft PR để Huy xem](https://github.com/huyryan220806/robust-memory-ad/pull/1).

## 1. Máy và điều kiện đo

| Mục | Quy ước / tình trạng |
|---|---|
| Máy chính thức | Google Colab, NVIDIA L4; notebook phải kiểm GPU thực nhận, không tự thay bằng GPU khác |
| RAM, VRAM, CPU, OS, driver, thư viện | Lấy từ phiên Colab thực chạy; chưa điền bằng thông số quảng cáo |
| Máy thử dụng cụ | Windows 11 Home Single Language 10.0.26200, i5-12450H, RAM 16.866.680.832 byte; RTX 4050 Laptop 6.141 MiB, driver 610.78 |
| Môi trường thử | Python 3.12.5, PyTorch 2.12.1+cpu, psutil 7.2.2; không chạy CUDA |
| Batch size | Đề xuất 1 để đo một ảnh; harness bắt buộc 1 |
| Dtype, độ phân giải, decoder, normalization | Chờ cấu hình chính xác từ Phúc |
| Truy vấn | Chờ loại index, CPU/GPU, số láng giềng, số luồng và tham số từ Phúc |
| Nhóm sản phẩm, split, nhóm ánh sáng, thứ tự ảnh | Chờ nhóm chốt; phải giống nhau giữa các cấu hình so sánh |
| Ngân sách | Random và greedy phải cùng số patch thực; ghi cả seed, tỷ lệ và số patch |

`environment.json` lưu thư viện thực tế, CPU/OS/RAM, `nvidia-smi`, commit bộ đo và hash nguồn bộ đo.
`config.json` lưu cấu hình đo, commit baseline, adapter và thứ tự ảnh; `images.json` lưu hash ảnh.
Không xem một phiên Colab mới là cùng môi trường chỉ vì đều có nhãn L4.

## 2. Ranh giới thời gian — còn chờ Huy xác nhận

Đề xuất: ảnh **đã giải mã trong RAM** → tiền xử lý → tạo batch 1 → chuyển thiết bị → backbone → truy vấn bank/index → tạo điểm và map sẵn cho bên gọi.

- Loại đọc đĩa, giải mã ảnh, nạp mô hình/bank, tạo index và ghi CSV khỏi thời gian từng ảnh.
- Việc trả kết quả về CPU **chưa chốt**. Nếu pipeline đã trả điểm/map CPU thì phải ghi đó là phần của phép đo; không tự cắt ra.
- Nạp mô hình và bank một lần, đặt `eval()` và chế độ inference/no-grad. Không cache kết quả suy luận.
- Trước đồng hồ và sau phép tính cuối: đồng bộ GPU, kể cả công việc FAISS/stream ngoài framework nếu có.
- Dùng `time.perf_counter_ns()`, xuất **ms**. Đầu ra phải được tính đầy đủ; không trả generator/lazy result.

Điểm cần Phúc xác nhận trong mã upstream: `PatchCore.load_from_path`, đường suy luận `predict`/`_predict`, preprocessing và FAISS. Đây chỉ là các điểm tham khảo; **adapter phải theo đúng commit Phúc bàn giao**.
Nguồn: [PatchCore](https://github.com/amazon-science/patchcore-inspection/blob/main/src/patchcore/patchcore.py), [FAISS wrapper](https://github.com/amazon-science/patchcore-inspection/blob/main/src/patchcore/common.py).

## 3. Thử bộ đo ngay

Từ thư mục gốc repo:

```bash
python -m pip install -r requirements-profiling.txt
python -m unittest discover -s tests -v
python -m scripts.profile --smoke --output outputs/smoke-cpu-UNIQUE_ID
```

`--smoke` dùng phép cộng giả lập CPU, **không có ảnh, bank hoặc mô hình anomaly detection**.
Kết quả minh họa nằm trong `docs/evidence/smoke-cpu-20261125/`; không dùng các ms này trong bảng so sánh mô hình.
Dãy kiểm `8,9,10,11,12` cho p50 = **10 ms**, p95 = **11,8 ms** theo nội suy tuyến tính.

## 4. Tích hợp khi Phúc giao baseline

1. Nhận commit nguồn và môi trường đã khóa, cấu hình full/random/greedy, bank/index và trọng số; danh sách ảnh có thứ tự và `predictions.csv` (`run_id,image_id,image_score,map_path`). Không train lại hay chọn bank mới trong vòng đo.
2. Điền `examples/adapter_template.py` theo pipeline thật. `load` kiểm HEAD baseline, nạp model/bank và đặt seed/dtype/eval; `decode` trả ảnh RAM; `predict` chứa đúng phạm vi đo; `image_score` lấy raw score. `synchronize` xử lý công việc ngoài PyTorch nếu cần.
3. Sao chép `examples/pilot-l4.template.json` thành cấu hình riêng. Điền đường dẫn **tương đối với file config**, mọi trường `REPLACE`, số patch, budget và điểm tham chiếu. Đặt `baseline_commit_verified=true` chỉ sau khi adapter thực sự kiểm checkout. Không chạy file template nguyên trạng.
4. Kiểm tolerance với Phúc (mặc định kỹ thuật `atol=rtol=1e-5` là đề xuất, chưa được nhóm chốt). Bộ đo so điểm của từng ảnh tham chiếu trước khi warm-up; sai thì dừng và lưu `validation.json`/`status.json`.
5. Mở `notebooks/profiling_colab.ipynb` trong Colab. Chọn runtime GPU L4, kiểm `nvidia-smi` và PyTorch CUDA. Cài baseline bằng đúng hướng dẫn Phúc; **không tự nâng torch/FAISS bằng phiên bản tùy ý**.
6. Chạy từ gốc repo:

```bash
python -m scripts.profile --config configs/pilot/YOUR_CONFIG.json --adapter examples.adapter_template:create_adapter --output outputs/YOUR_MEASUREMENT_ID
```

Harness không tích hợp được baseline cho đến khi adapter được điền. Không có fallback CPU cho cấu hình L4. Nếu không thuê/nhận được L4, ghi bị chặn và hỏi Huy nơi chạy, không thay thiết bị âm thầm.

## 5. Pilot: 10 warm-up + 50 mẫu đo ban đầu

Đây là điểm bắt đầu, chưa phải bảo đảm ổn định. Warm-up và đo chạy cùng đường tiền xử lý. Ảnh được xoay vòng theo danh sách cố định; 50 lượt có thể lặp lại ảnh, không mặc nhiên là 50 ảnh khác nhau. Dùng cùng danh sách và thứ tự giữa full/random/greedy.

`warmup.csv` giữ thời gian làm nóng, `timings.csv` chỉ giữ mẫu sau warm-up. Xem dãy gốc và `stability.json` (p95 hai nửa); nếu biến động, lặp **đúng cấu hình** với `measurement_id` mới, ghi lý do trong nhật ký và cân nhắc tăng số lượt. Không xóa outlier, không sửa log cũ. Kiểm tiến trình khác, nạp bank trong loop, cấp phát đầu, đọc tệp và đồng bộ theo từng giả thuyết có thể tái hiện.

Phân vị: sắp xếp các mẫu và nội suy ở vị trí `(n-1)*q`, giống `numpy.quantile(method="linear")`.
Tự kiểm `n=iterations`, p50 ≤ p95, ms không âm/hữu hạn, không gộp warm-up vào mẫu đo. Chỉ so p95 cùng thiết bị, thư viện, nhóm ảnh, dtype, batch và ranh giới đo.

Mẫu CSV **chỉ minh họa định dạng**:

```csv
run_id,measurement_id,image_group,device,image_id,iteration,latency_ms
pilot01-greedy-s0,pilot01-greedy-s0-l4-session01,product_split_light,cuda:0,img001,0,10.0
```

## 6. Bank/index và bộ nhớ đỉnh

Trong config, liệt kê mỗi tệp kèm vai trò: `bank_index`, `backbone`, `metadata`, `intermediate`. `artifacts.json` ghi byte thực và SHA-256 từng tệp; tổng bank/index chỉ cộng `bank_index`, **1 MB = 1.000.000 byte**. Tệp params/metadata và trọng số báo riêng. Nếu index đã chứa vector, raw bank trùng nội dung chỉ là `intermediate` khi không cần để triển khai. Nếu thực sự cần cả hai, ghi lý do và tính cả hai; không tự suy luận từ phần mở rộng tệp.

RAM: psutil lấy RSS tiến trình trước vòng đo và mỗi 5 ms, lưu `rss_samples.csv`. `memory.json` ghi peak quan sát tuyệt đối và tăng thêm so baseline. **Peak lấy mẫu có thể bỏ sót đỉnh ngắn**, gồm cả chi phí ghi log/đo của tiến trình; không gọi là peak chính xác. Không bao quát tiến trình con.

VRAM: reset bộ đếm PyTorch **sau warm-up, ngay trước vòng đo**, ghi baseline allocated/reserved và max allocated/reserved. Bộ đếm bao gồm phần model/bank do PyTorch giữ, **không bao gồm FAISS/CUDA ngoài allocator PyTorch**. Không xem phần chênh lệch là tổng footprint mô hình. Nếu truy vấn GPU dùng FAISS, cần thống nhất thêm công cụ cấp tiến trình và cách lấy peak; hiện báo `gpu_process_peak=not measured`.

## 7. Chi phí chọn coreset

Dùng `measure_selection` trong `scripts/profile.py` sau khi đã có ma trận train features. Chuẩn bị feature/seed trước đồng hồ; đồng bộ hai phía. Callback chỉ làm chọn coreset và trả chỉ số hoặc bank theo ranh giới đã ghi. Ghi `run_id`, `measurement_id`, seed, budget, số patch đầu vào và nội dung đo (projection, chọn patch, gather, chuyển thiết bị có nằm trong phép đo không). Không gọi `fit` toàn bộ rồi gọi đó là thời gian chọn. Nếu Phúc chỉ giao bank mà không có feature/lệnh chọn/log gốc, mục này **chưa đo được**.

## 8. Bàn giao và ghép chất lượng

`run_id` là mã **cấu hình + seed** do baseline dùng; giữ nguyên để ghép chất lượng. `measurement_id` phân biệt các lần đo lặp và thiết bị, không đổi run ID chỉ vì chạy lại đồng hồ. Mỗi thư mục có config, environment, artifacts, hashes ảnh, validation, warmup, timings, RSS samples, memory, stability, efficiency và status. `status=failed` không phải lượt hợp lệ dù đã có một phần CSV.

`efficiency.csv` có run ID, measurement ID, nhóm ảnh, device, commit, seed, budget, số patch, byte/MB bank, số warm-up, số mẫu, p50/p95 và đường dẫn log tương đối trong thư mục của lượt đo. Tên GPU/VRAM nằm trong `environment.json`, cùng cấu hình `device=cuda:0`. Giữ nguyên thư mục khi chuyển log.

Khi Đỗ Hoàng Phúc giao `quality.csv`, thống nhất `image_group` và ngưỡng/split. Script ghép yêu cầu đúng một hàng chất lượng cho mỗi khóa `run_id,image_group` (thêm `device` nếu có trong quality); lọc rõ ngưỡng trước khi ghép. Không tự tính AUROC, độ nhạy hay báo động giả thay người phụ trách.

```bash
python -m scripts.join_quality --efficiency outputs/RUN1/efficiency.csv outputs/RUN2/efficiency.csv --quality quality.csv --output quality-efficiency.csv
```

Script dừng khi thiếu hoặc trùng khóa để tránh nhân số hàng hay mất nhóm. Nhiều measurement ID/thiết bị vẫn được giữ riêng. Không ghép chất lượng thật với `smoke-only`.

Đầu ra cho Huy: lệnh chạy, commit bộ đo và baseline, notebook/môi trường, run ID, measurement ID, toàn bộ log thô và bảng hiệu năng. Không commit MVTec, feature cache, bank lớn hoặc trọng số; chờ nhóm chọn nơi lưu chung.
