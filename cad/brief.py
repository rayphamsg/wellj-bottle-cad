"""Sinh bản thảo brief gửi nhà máy + danh sách thông số cần xác nhận từ cùng nguồn số liệu với bản vẽ.

Chỉ tạo file nháp trong docs/brief_nha_may/. Không gửi đi đâu.
"""
import csv
from pathlib import Path

from .brief_drawing import wrap_geometry

DOCS = Path(__file__).resolve().parent.parent / "docs" / "brief_nha_may"


def n(x, nd=0):
    """Số kiểu Việt Nam: dấu . ngăn nghìn, dấu , thập phân."""
    s = f"{x:,.{nd}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def param_rows(p, res, g):
    cad = "CAD hiện tại"
    rows = [
        # (mã, nhóm, thông số, giá trị/nguồn trong CAD, ghi chú)
        ("A1", "Cổ / nắp", "Chuẩn finish/cổ (loại, mã, ren, OD ren, ID miệng)",
         f"Placeholder hình trụ Ø{p['neck.finish_od']:g} (ảnh ghi 'miệng 38 mm'; chưa rõ OD ren hay OD miệng); ID giả định {p['neck.finish_id']:g}. Không dựng ren.",
         "Nhà máy cung cấp chuẩn/bản vẽ finish. Không suy chuẩn từ '38 mm'."),
        ("A2", "Cổ / nắp", "Chiều cao finish, vị trí và kích thước vòng đỡ (support ledge)",
         f"Placeholder: vòng Ø{p['neck.support_ring_od']:g} tại z={p['neck.support_ring_z']:g}, dày {p['neck.support_ring_h']:g}; cổ cao {p['body.height_total'] - p['zones.shoulder_top_z']:g}.",
         ""),
        ("A3", "Cổ / nắp", "Nắp có vòng niêm phong phù hợp (loại, chất liệu, liner, mô-men đóng/mở)", "Chưa có", "Ảnh mẫu có nắp đen/trắng có vòng niêm phong."),
        ("A4", "Cổ / nắp", "Cổ có kết tinh (neck crystallization) hay không", "Chưa có", ""),
        ("B1", "Phôi", "Mã phôi, khối lượng (g), vật liệu/IV, độ dày thành phôi", "Chưa có", "Không suy từ chai thường 36 g."),
        ("B2", "Phôi", "Khối lượng chai hot-fill đề xuất (g)", "Chưa có", "36 g chỉ là chai thường tham chiếu."),
        ("C1", "Quy trình", "Thiết bị thổi và khuôn hiện có (heat-set? đáy chuyển động được không?)", "Chưa có", "Quyết định câu hỏi 1."),
        ("C2", "Quy trình", "Quy trình thổi chịu nhiệt: nhiệt khuôn, thời gian giữ, độ kết tinh mục tiêu", "Chưa có", ""),
        ("C3", "Quy trình", "Nhiệt độ chiết rót (°C) và thời gian giữ nóng (s)", "Chưa có", "Chủ dự án/nhà máy chốt; CAD không suy ra được."),
        ("C4", "Quy trình", "Cách làm nguội (nhúng/phun/đường hầm), thời gian, nhiệt độ cuối", "Chưa có", ""),
        ("C5", "Quy trình", "Sản phẩm chiết rót (loại, độ nhớt, có CO₂/bọt không)", "Chủ dự án bổ sung", ""),
        ("D1", "Dung tích", "Định nghĩa '500 ml' (ở nhiệt độ nào; đầy miệng hay chiết rót)", f"Ảnh: dung tích danh định {p['capacity.target_fill_ml']:g} ml", ""),
        ("D2", "Dung tích", "Dung tích đầy miệng đề xuất (ml)",
         f"{n(res['cavity_brimful_ml'],1)} ml — hình học khoang trong với thành đều {n(p['wall.t_model'],2)} mm GIẢ ĐỊNH", "Chỉ để so sánh; không dùng làm xác nhận."),
        ("D3", "Dung tích", "Khoảng trống đầu chai đề xuất (ml, %, mm) và mức chiết rót (mm dưới đỉnh miệng)",
         f"500 ml ở z={n(res['fill_level_z_for_target_mm'],1)} mm (trong vai), khoảng trống ≈ {n(res['headspace_pct_at_target'],1)}% — hình học",
         "Với giả định hiện tại mức 500 ml nằm trong vai; cần nhà máy cho giá trị thực."),
        ("D4", "Dung tích", "Thể tích co cần hấp thụ khi nguội (ml) ở điều kiện C3–C4", "Chưa có", ""),
        ("E1", "Chân không / đáy", "Có xử lý chân không chủ yếu ở đáy được không (Có / Không / Một phần)", "Đáy CAD: màng lõm TĨNH, không phải cơ cấu hoạt động", "Câu hỏi 1."),
        ("E2", "Chân không / đáy", "Loại cơ cấu đáy, hành trình (mm), thể tích hấp thụ (ml)",
         f"Màng R{p['base.diaphragm_r']:g} sâu {p['base.diaphragm_depth']:g}. Minh họa: dịch 3 mm ≈ 3,8 ml (chỉ tính hình học, CHƯA kiểm chứng)", "Không dùng con số minh họa làm năng lực thật."),
        ("E3", "Chân không / đáy", "Thay đổi cần ở đáy so với CAD (bán kính, độ sâu, gân, vòng đỡ, độ dày)", "—", "Đánh dấu lên bản vẽ trang 2."),
        ("E4", "Chân không / đáy", "Chân không dư sau khi nguội (kPa hoặc mmHg) và ngưỡng chấp nhận", "Chưa có", ""),
        ("E5", "Kết cấu thêm", "Kết cấu tối thiểu phải thêm nếu đáy không đủ: vị trí, loại, kích thước, chức năng (dùng vùng ②–⑥)", "Chưa có", "Câu hỏi 2; đánh dấu trực tiếp lên bản vẽ."),
        ("E6", "Kết cấu thêm", "Bán kính bo góc tối thiểu/tối ưu", f"R{p['body.corner_r']:g} (giả định)", "Ảnh hưởng nhãn quấn."),
        ("E7", "Kết cấu thêm", "Biên dạng vai: giữ vòm hiện tại hay cần đổi", f"Vòm mặt phẳng, z {p['zones.shoulder_start_z']:g}–{p['zones.shoulder_top_z']:g} (giả định)", "Đổi vai ảnh hưởng nhận diện."),
        ("E8", "Kết cấu thêm", "Rãnh chu vi trên/dưới nhãn: có dùng được với khuôn không (undercut, độ sâu)",
         f"2 rãnh sâu {p['features.band_depth']:g}, rộng {p['features.band_width']:g}, tại z={p['features.lower_band_z']:g} và {p['features.upper_band_z']:g} (giả định)", ""),
        ("E9", "Kết cấu thêm", "Độ dày thành mục tiêu theo vùng: đáy, gót, thân (mặt/góc), vai, cổ", f"Thành đều {n(p['wall.t_model'],2)} mm CHỈ để dựng khoang (giả định)", "Không đại diện phân bố sau thổi."),
        ("E10", "Khuôn", "Vị trí đường chia khuôn (parting line): có đặt ở góc để giữ 4 mặt nhãn sạch được không", "Chưa có", ""),
        ("F1", "Nhãn", "Diện tích nhãn phẳng còn lại mỗi mặt và tổng 4 mặt (mm²), kích thước",
         f"{n(g['flat_w'])} × {n(g['h'])} = {n(g['flat_face'])} mm²/mặt; {n(g['flat_total'])} mm² tổng 4 mặt", "Mục tiêu: giữ tối đa. Nhà máy cho con số còn lại và % so với CAD."),
        ("F2", "Nhãn", "Vùng nhãn quấn quanh thân còn lại (chu vi × chiều cao, mm²)",
         f"chu vi {n(g['perim'],1)} × {n(g['h'])} ≈ {n(g['wrap_area'])} mm²", "Gồm 4 góc bo."),
        ("F3", "Nhãn", "Chiều cao vùng thân trơn tối đa giữa hai rãnh", f"Vùng nhãn tham chiếu z {g['z_lo']:g}–{g['z_hi']:g} (cao {g['h']:g}); mép chừa {p['zones.label_margin_z']:g}", ""),
        ("F4", "Nhãn", "Độ phẳng cho phép của mặt nhãn sau khi nguội (lõm/phồng, mm)", "Chưa có", "Nhà máy đề xuất ngưỡng đo được."),
        ("G1", "Thử nghiệm", "Thử chiết rót nóng thực tế: số mẫu, điều kiện, nơi thực hiện", "—", "Câu hỏi 5."),
        ("G2", "Thử nghiệm", "Tiêu chí đạt: co thể tích (%), biến dạng mặt nhãn (mm), ổn định đứng/rocker, chân không dư", "Chưa có — nhà máy đề xuất ngưỡng", ""),
        ("G3", "Thử nghiệm", "Tiêu chí đạt: tải dọc, rò rỉ/mô-men nắp, thả rơi, xếp chồng", "Chưa có — nhà máy đề xuất ngưỡng", ""),
        ("G4", "Thử nghiệm", "Phân bố độ dày thành (cắt mẫu) và kiểm tra nhãn thực tế sau nguội/lưu kho", "Chưa có", ""),
        ("H1", "Thương mại", "Chi phí khuôn, MOQ, thời gian mẫu (nếu đã biết)", "—", "Tùy chọn."),
    ]
    return rows


def write_param_files(p, res, g):
    DOCS.mkdir(parents=True, exist_ok=True)
    rows = param_rows(p, res, g)
    with open(DOCS / "02_thong_so_can_xac_nhan.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["Mã", "Nhóm", "Thông số cần xác nhận", "Giá trị / nguồn trong CAD (tham chiếu, KHÔNG phải thông số sản xuất)",
                    "NHÀ MÁY ĐIỀN: xác nhận / đề xuất", "Ghi chú"])
        for code, grp, name, cadv, note in rows:
            w.writerow([code, grp, name, cadv, "", note])
    md = ["# Danh sách thông số cần nhà máy xác nhận — chai PET 500 ml (CONCEPT — CHƯA DUYỆT SẢN XUẤT)", "",
          "Cột 'CAD' là giá trị giả định hoặc đọc từ ảnh để dựng hình, **không phải** thông số sản xuất. "
          "Cột 'Nhà máy điền' để trống. File CSV cùng tên mở được bằng Excel để điền.", "",
          "| Mã | Nhóm | Thông số cần xác nhận | Giá trị / nguồn trong CAD | Nhà máy điền | Ghi chú |", "|---|---|---|---|---|---|"]
    for code, grp, name, cadv, note in rows:
        md.append(f"| {code} | {grp} | {name} | {cadv} | | {note} |")
    (DOCS / "02_thong_so_can_xac_nhan.md").write_text("\n".join(md) + "\n", encoding="utf-8")


def write_message(p, res, g):
    DOCS.mkdir(parents=True, exist_ok=True)
    t = f"""# Bản thảo tin nhắn gửi nhà máy — CHƯA GỬI

> **Nội bộ — xóa phần này trước khi gửi.**
> - Điền: [Tên nhà máy], [Người phụ trách], [Công ty/Người gửi], [Ngày phản hồi mong muốn].
> - File đính kèm đề xuất: `out/ban_ve_gui_nha_may_500ml.pdf`, `out/chai_500ml_concept_outer.step` (chỉ hình học ngoài), `docs/brief_nha_may/02_thong_so_can_xac_nhan.csv`.
> - Không đính kèm `chai_500ml_concept.step` (có thành đều giả định) để tránh bị hiểu là độ dày thiết kế.
> - Quyết định của anh: có nêu mã mẫu tham chiếu "M38 – 500 ml, Mẫu F" hay không (đang để trong ngoặc ở mục 1); có kèm ảnh mẫu gốc hay không.
> - Không gửi trong phiên này; chưa gửi đi đâu.

---

**Tiêu đề:** Đề nghị xác nhận khả năng chuyển chai PET vuông 500 ml sang hot-fill — giữ nhãn thân trơn

Kính gửi [Người phụ trách] — [Tên nhà máy],

Chúng tôi đang phát triển một chai PET vuông 500 ml và muốn hỏi khả năng sản xuất bản hot-fill với thiết bị và quy trình hiện có của quý nhà máy. Hồ sơ đính kèm là **mô hình hình học concept, chưa phải thiết kế hot-fill đã kiểm chứng**; chúng tôi cần ý kiến chuyên môn của quý nhà máy để biết nên giữ, sửa hay bỏ phần nào.

**1. Hình dáng tham chiếu** (mẫu thân vuông 61 × 61 × 188 mm, miệng 38 mm; mã nội bộ M38 – 500 ml, Mẫu F)
Thân 61 × 61, bo góc R{p['body.corner_r']:g} (giả định), vai dạng vòm, bốn mặt nhãn phẳng {n(g['flat_w'])} × {n(g['h'])} mm (≈ {n(g['flat_face'])} mm²/mặt; nhãn quấn gồm góc ≈ {n(g['wrap_area'])} mm²).

**2. Mục tiêu bắt buộc:** giữ **diện tích nhãn trơn tối đa, ưu tiên bốn mặt thân**; hạn chế gân nhìn thấy.

**3. Xin quý nhà máy phản hồi cụ thể**

1. **Xử lý chân không ở đáy.** Với thiết bị, khuôn và quy trình hiện có, có thể xử lý chân không *chủ yếu ở đáy* và giữ thân trơn không? (Có / Không / Một phần.) Nếu có: loại cơ cấu đáy, hành trình, thể tích hấp thụ (ml) và những thay đổi cần ở đáy so với hình trong CAD.
2. **Kết cấu tối thiểu nếu không.** Cần thêm gì và ở đâu? Xin **đánh dấu trực tiếp lên bản vẽ** (vùng ②–⑥ là vị trí ứng viên chúng tôi nêu để hỏi, không phải thiết kế), ghi loại, kích thước và chức năng từng phần, và nói vùng nào nên loại bỏ.
3. **Diện tích nhãn còn lại.** Sau các thay đổi trên, diện tích nhãn **phẳng** mỗi mặt/tổng bốn mặt và vùng nhãn **quấn quanh** thân còn bao nhiêu (mm² và % so với CAD)? Độ phẳng mặt nhãn sau khi nguội nhà máy có thể đảm bảo?
4. **Thông số kỹ thuật.** Chuẩn cổ/nắp phù hợp, phôi (mã, khối lượng, vật liệu), quy trình chiết–làm nguội đề xuất, **dung tích đầy miệng** và **khoảng trống đầu chai** đề xuất, mức chiết rót.
5. **Tiêu chí và thử nghiệm.** Các tiêu chí và thử nghiệm quý nhà máy dùng để xác nhận chai phù hợp (gợi ý trong danh sách đính kèm: thử chiết rót nóng thực tế, co thể tích, biến dạng mặt nhãn và độ ổn định đứng sau nguội/lưu kho, chân không dư, tải dọc, kín/mô-men nắp, rơi/xếp chồng, phân bố độ dày, thử dán nhãn thực tế). Xin đề xuất ngưỡng đạt và cỡ mẫu.

**4. Cần lưu ý khi đọc hồ sơ**
- **Đáy trong CAD là hình học tĩnh** (màng lõm R{p['base.diaphragm_r']:g}, sâu {p['base.diaphragm_depth']:g} mm), chưa phải cơ cấu hấp thụ chân không hoạt động. **Sơ đồ chuyển động và mức giảm thể tích trong bản vẽ chỉ là minh họa, chưa kiểm chứng.**
- Cổ/finish là **placeholder**; chúng tôi không suy chuẩn ren từ "38 mm". Thành đều {n(p['wall.t_model'],2)} mm chỉ để dựng khoang trong, không phải phân bố độ dày sau thổi. Dung tích tính từ hình học ({n(res['cavity_brimful_ml'],1)} ml đầy miệng) chỉ để tham khảo.
- Khối lượng 36 g là của chai thường, **không** dùng làm cơ sở cho chai hot-fill.
- Chúng tôi **chưa** khẳng định concept này đạt hot-fill ở bất kỳ nhiệt độ nào; nhiệt độ/thời gian chiết rót, quy trình thổi chịu nhiệt và lượng chân không cần hấp thụ cần quý nhà máy xác nhận.
- Chúng tôi không yêu cầu sao chép cấu trúc độc quyền của hãng khác. Nếu giải pháp đáy của quý nhà máy thuộc diện sở hữu trí tuệ/giấy phép, xin nêu rõ.

**5. Cách phản hồi.** Xin điền cột "NHÀ MÁY ĐIỀN" trong file CSV và đánh dấu lên bản vẽ PDF (hoặc gửi bản vẽ riêng của quý nhà máy). Nếu có thể, mong nhận phản hồi trước [Ngày]. Nếu cần trao đổi trực tiếp, xin cho chúng tôi biết thời gian phù hợp.

Trân trọng,
[Người gửi]
[Công ty / liên hệ]

**Đính kèm:** (1) `ban_ve_gui_nha_may_500ml.pdf` (2 trang); (2) `chai_500ml_concept_outer.step` — hình học ngoài tham chiếu; (3) `02_thong_so_can_xac_nhan.csv`.
"""
    (DOCS / "01_ban_thao_tin_nhan.md").write_text(t, encoding="utf-8")


def write_all(p, res):
    g = wrap_geometry(p)
    write_message(p, res, g)
    write_param_files(p, res, g)
    return g
