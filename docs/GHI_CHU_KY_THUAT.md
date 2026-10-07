# Chai 500 ml hot-fill — ghi chú kỹ thuật (CONCEPT — CHƯA DUYỆT SẢN XUẤT)

Mẫu tham chiếu: M38 – 500 ml (Mẫu F), chai thường 36 g. Đây là mô hình **hình học** để xem và chỉnh sửa, không phải thiết kế đã kiểm chứng chịu nhiệt hay chân không.

## 1. Nguồn dữ liệu

Mọi tham số nằm trong `config/bottle_500_params.toml`, mỗi giá trị có nhãn:

| Nhãn | Ý nghĩa |
|---|---|
| `image` | Đọc từ ảnh: thân 61×61, cao 188, miệng 38, dung tích danh định 500 ml |
| `assumption` | Giả định để dựng hình: bo góc, chiều cao từng đoạn, rãnh, đáy |
| `factory` | Giá trị giữ chỗ, nhà máy phải xác nhận: finish/cổ, độ dày thành, mức chiết rót, toàn bộ quy trình |

Trọng lượng 36 g chỉ để tham chiếu, không dùng trong mô hình và không suy ra khối lượng chai hot-fill.

## 2. Hình dáng và các đánh đổi

- **Thân**: 61×61, bo góc R11 (giả định). Mặt nhãn phẳng rộng 61 − 2×11 = **39 mm**. Bo nhỏ hơn thì mặt phẳng rộng hơn nhưng góc kém cứng.
- **Vùng nhãn** (tô cam trong preview): 4 mặt phẳng, mỗi mặt 39 × 93 mm = 3.627 mm² (tổng 14.508 mm²). Không có gân ngang; chừa mép 3 mm so với rãnh. Chưa tính phần nhãn quấn qua góc bo.
- **Vai**: giao tuyến mặt phẳng × mặt tròn xoay, cho hình vòm gần với ảnh. Nhìn trước, vai thu từ 61 mm về cổ trong khoảng ~11 mm cao (z≈147→158).
- **Cổ**: hình trụ Ø38 + vòng đỡ placeholder. Không dựng ren, không suy chuẩn finish từ "38 mm". Ảnh không nói 38 mm là OD ren hay OD miệng.
- **Hai rãnh nông** (sâu 1,2 mm, rộng 5 mm) quanh chu vi, một trên và một dưới vùng nhãn: cứng hóa chung mà không cắt vào nhãn.
- **Đáy**: gót bo R6, vòng đỡ ngoài, màng trung tâm lõm dạng vòm R26 sâu 10 mm.

## 3. Kết cấu, chân không và quy trình — ba việc khác nhau

1. **Tăng độ cứng** (có trong CAD): bo góc, vai vòm, rãnh chu vi, gót bo. Chống biến dạng chung, **không** hấp thụ chân không.
2. **Hấp thụ chân không khi nguội** (chưa thiết kế): hướng ưu tiên ít ảnh hưởng nhãn nhất là màng chuyển động ở **đáy**, vì không đụng 4 mặt nhãn. Trong CAD chỉ có màng lõm tĩnh. Sơ đồ nguyên lý (trang 2 bản vẽ) ghi rõ "chưa kiểm chứng". Một đáy lõm thông thường không được coi là đã xử lý chân không.
3. **Phôi, thổi chịu nhiệt, cổ/nắp**: quyết định chai có chịu nhiệt hay không; không suy ra được từ CAD.

**Rủi ro chính:** mặt phẳng 39 mm không gân là kiểu dễ bị lõm vào khi có chân không. Nếu đáy hấp thụ chưa đủ, phải đánh đổi một trong: (a) mặt nhãn hơi cong lồi; (b) lõm nông trên mặt hoặc ở góc, làm giảm diện tích nhãn phẳng; (c) tăng khối lượng/độ dày phôi. Chưa có dữ liệu để chọn. Chưa sao chép cấu trúc độc quyền nào.

## 4. Dung tích (tính từ khoang trong, không từ solid ngoài)

Khoang trong dựng với thành đều 0,45 mm (giả định `factory`, **không** đại diện phân bố độ dày sau thổi).

| Đại lượng | Giá trị |
|---|---|
| Dung tích đầy miệng (hình học) | 540,9 ml |
| Thể tích khoang đến mức giả định thấp hơn đỉnh miệng 12 mm (z=176) | 531,8 ml |
| Mức z để khoang chứa 500 ml | 148,3 mm (trong vai), khoảng trống ≈ 7,6% thể tích đầy miệng |

Điểm cần xem xét: với các cao độ giả định, mức 500 ml nằm **trong vai**, thấp hơn nhiều so với vị trí chiết rót thường ở cổ. Hoặc mẫu gốc có dung tích đầy miệng thấp hơn, hoặc các cao độ/độ lõm đáy giả định cần chỉnh. Mức chiết rót thật do nhà máy/khách hàng xác định. Đây là số hình học, không phải dung tích chiết rót đã duyệt.

## 5. Kiểm tra đã thực hiện (chỉ kiểm tra hình học)

- Chạy mã thực tế bằng CadQuery 2.8.0 trong `.venv`.
- Solid ngoài, solid rỗng và khoang trong đều `isValid()`, mỗi cái 1 solid (đã sửa lỗi vòng đỡ chia đôi khoang).
- Bounding box ngoài 61 × 61 × 188 mm khớp tham chiếu.
- Xuất STEP, nhập lại thành công, solid hợp lệ.
- Render 6 hướng + vùng nhãn + mặt cắt; so sánh bằng mắt các preview với hình chiếu HLR trong bản vẽ (cùng kích thước, cùng vị trí rãnh/vai).

Chưa kiểm tra và không thể kết luận từ CAD: chịu nhiệt, chịu chân không, độ bền rơi, phân bố độ dày, khả năng thổi, khối lượng chai, tương thích nắp.

## 6. Dữ liệu cần nhà máy bổ sung

Chuẩn finish/cổ và nắp có vòng niêm phong; thông số phôi (khối lượng, vật liệu, độ dày); nhiệt độ và thời gian chiết rót; quy trình thổi chịu nhiệt (nhiệt khuôn, thời gian, độ kết tinh); lượng chân không cần hấp thụ; mức chiết rót/khoảng trống mong muốn; khuôn và giới hạn undercut cho rãnh/đáy; yêu cầu vùng nhãn (kích thước, quấn góc hay không).

## 7. Chạy lại

```
.venv/bin/python build.py all        # hoặc: model | previews | drawing
```

Sửa `config/bottle_500_params.toml` rồi chạy lại; kết quả ở `out/`. Preview dùng bộ render phần mềm trong `cad/render.py` (không cần GPU), bản vẽ dùng `cad/drawing.py`.
