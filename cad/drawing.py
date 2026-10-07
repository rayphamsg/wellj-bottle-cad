"""Bản vẽ PDF sơ bộ (A3 ngang, tỉ lệ 1:1) từ đường nét HLR của mô hình CadQuery."""
import json
import math
from pathlib import Path

import cadquery as cq
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle, Polygon, Arc

from OCP.HLRBRep import HLRBRep_Algo, HLRBRep_HLRToShape
from OCP.HLRAlgo import HLRAlgo_Projector
from OCP.gp import gp_Ax2, gp_Pnt, gp_Dir
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_EDGE

from .params import Params, CLASS_LABEL
from .render import label_zone

STAMP = "CONCEPT — CHƯA DUYỆT SẢN XUẤT"
RED = "#a01818"
ORANGE = "#ee7824"
CLS_COLOR = {"image": "#1b6e2b", "assumption": "#a56a00", "factory": "#b01818"}
A3 = (420, 297)


def hlr_edges(shape, n, vx, samples=48):
    """Đường nét nhìn thấy, trả về danh sách polyline [(x,y),...] trong mặt phẳng nhìn (mm)."""
    algo = HLRBRep_Algo()
    algo.Add(shape.wrapped)
    algo.Projector(HLRAlgo_Projector(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(*n), gp_Dir(*vx))))
    algo.Update()
    algo.Hide()
    res = HLRBRep_HLRToShape(algo)
    lines = []
    for kind, comp in (("sharp", res.VCompound()), ("smooth", res.Rg1LineVCompound()),
                       ("outline", res.OutLineVCompound())):
        if comp.IsNull():
            continue
        ex = TopExp_Explorer(comp, TopAbs_EDGE)
        while ex.More():
            e = cq.Edge(ex.Current())
            pts = [e.positionAt(t / samples) for t in range(samples + 1)]
            lines.append((kind, [(v.x, v.y) for v in pts]))
            ex.Next()
    return lines


def draw_lines(ax, lines, ox, oy, lw=0.45):
    for kind, pts in lines:
        xs = [ox + x for x, _ in pts]
        ys = [oy + y for _, y in pts]
        ax.plot(xs, ys, color="k", lw=lw if kind != "smooth" else lw * 0.6, solid_capstyle="round")


def dim_v(ax, x, y0, y1, text, off=0.0, ext_to=None, side=-1):
    ax.annotate("", (x, y0), (x, y1), arrowprops=dict(arrowstyle="<->", lw=0.5, color="#222", shrinkA=0, shrinkB=0))
    ax.text(x + side * 1.2, (y0 + y1) / 2, text, rotation=90, ha="center" if side < 0 else "center",
            va="center", fontsize=6.5, color="#111",
            bbox=dict(fc="white", ec="none", pad=0.6))
    if ext_to is not None:
        for y in (y0, y1):
            ax.plot([x, ext_to], [y, y], color="#555", lw=0.3)


def dim_h(ax, y, x0, x1, text, ext_from=None):
    ax.annotate("", (x0, y), (x1, y), arrowprops=dict(arrowstyle="<->", lw=0.5, color="#222", shrinkA=0, shrinkB=0))
    ax.text((x0 + x1) / 2, y + 1.6, text, ha="center", va="bottom", fontsize=6.5, color="#111",
            bbox=dict(fc="white", ec="none", pad=0.6))
    if ext_from is not None:
        for x in (x0, x1):
            ax.plot([x, x], [y, ext_from], color="#555", lw=0.3)


def title_block(ax, p, res, page):
    x0, y0, w, h = 270, 12, 140, 56
    ax.add_patch(Rectangle((x0, y0), w, h, fc="white", ec="k", lw=0.8))
    ax.plot([x0, x0 + w], [y0 + 26, y0 + 26], color="k", lw=0.5)
    ax.plot([x0 + 85, x0 + 85], [y0, y0 + 26], color="k", lw=0.5)
    ax.text(x0 + 3, y0 + 51, "Chai PET hot-fill 500 ml — mô hình hình học concept", fontsize=9, weight="bold", va="center")
    ax.text(x0 + 3, y0 + 44, "Mẫu tham chiếu: M38 – 500 ml (Mẫu F). Ảnh: 61×61×188 mm, miệng 38 mm.", fontsize=6.5, va="center")
    ax.text(x0 + 3, y0 + 38, "Neck/finish là placeholder. Không phải bản vẽ sản xuất.", fontsize=6.5, va="center")
    ax.text(x0 + 3, y0 + 32, "Tham số: config/bottle_500_params.toml", fontsize=6, va="center", color="#444")
    ax.text(x0 + 3, y0 + 20, "Đơn vị: mm", fontsize=7, va="center")
    ax.text(x0 + 3, y0 + 13, "Tỉ lệ: 1:1 (in A3 100%)", fontsize=7, va="center")
    ax.text(x0 + 3, y0 + 6, "Rev A · 2026-10-07 · Chưa duyệt", fontsize=7, va="center")
    ax.text(x0 + 88, y0 + 17, STAMP, fontsize=7, weight="bold", color=RED, va="center", ha="left")
    ax.text(x0 + 88, y0 + 7, f"Trang {page}/2", fontsize=7, va="center")


def page1(pdf, p, res, outer, hollow):
    fig = plt.figure(figsize=(A3[0] / 25.4, A3[1] / 25.4))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, A3[0]); ax.set_ylim(0, A3[1]); ax.axis("off")
    ax.add_patch(Rectangle((8, 8), A3[0] - 16, A3[1] - 16, fc="none", ec="k", lw=1.0))
    ax.text(A3[0] / 2, A3[1] - 16, STAMP, ha="center", va="center", fontsize=20, weight="bold", color=RED)

    H = p["body.height_total"]
    W = p["body.width"]
    base_y = 62
    fx, sx = 78, 190                     # tâm hình chiếu trước / mặt cắt
    z_lo, z_hi, half = label_zone(p)

    # --- hình chiếu trước
    draw_lines(ax, hlr_edges(outer.val(), (0, -1, 0), (1, 0, 0)), fx, base_y)
    ax.add_patch(Rectangle((fx - half, base_y + z_lo), 2 * half, z_hi - z_lo, fc=ORANGE, ec=ORANGE, alpha=0.35, lw=0))
    ax.add_patch(Rectangle((fx - half, base_y + z_lo), 2 * half, z_hi - z_lo, fc="none", ec=ORANGE, lw=0.9, ls="--"))
    ax.text(fx, base_y + (z_lo + z_hi) / 2, f"VÙNG NHÃN\n{2*half:.0f} × {z_hi-z_lo:.0f}\n(mỗi mặt, phẳng,\nliên tục)",
            ha="center", va="center", fontsize=7, color="#7a3000", weight="bold")
    ax.text(fx, base_y - 22, "NHÌN TRƯỚC (= nhìn bên)", ha="center", fontsize=8, weight="bold")

    # --- mặt cắt A-A (nửa y>=0, nhìn từ -Y), thành đều giả định
    half_box = cq.Workplane("XY").box(200, 100, 300, centered=(True, False, False)).translate((0, 0, -5))
    cut = hollow.intersect(half_box)
    draw_lines(ax, hlr_edges(cut.val(), (0, -1, 0), (1, 0, 0)), sx, base_y, lw=0.4)
    ax.text(sx, base_y - 22, "MẶT CẮT GIỮA (khoang trong giả định)", ha="center", fontsize=8, weight="bold")
    ax.text(sx, base_y - 27, f"thành đều {p['wall.t_model']} mm là giả định, KHÔNG phải độ dày sau thổi", ha="center", fontsize=6, color=RED)
    zf = res["fill_level_z_for_target_mm"]
    ax.plot([sx - W / 2 - 3, sx + W / 2 + 3], [base_y + zf] * 2, color="#1560b0", lw=0.8, ls=(0, (6, 2)))
    ax.text(sx + W / 2 + 4, base_y + zf, f"mức {p['capacity.target_fill_ml']:.0f} ml (hình học)\nz = {zf:.1f} mm",
            fontsize=6.3, color="#1560b0", va="center")
    ax.text(sx + W / 2 + 4, base_y + H - 4, f"đầy miệng (hình học)\n{res['cavity_brimful_ml']} ml", fontsize=6.3, color="#1560b0", va="center")

    # --- hình chiếu trên / dưới
    tx, ty = 300, 205
    draw_lines(ax, hlr_edges(outer.val(), (0, 0, 1), (1, 0, 0)), tx, ty)
    for sgn in (1, -1):                  # bốn đoạn phẳng nhãn
        ax.plot([tx - half, tx + half], [ty + sgn * W / 2] * 2, color=ORANGE, lw=2.2)
        ax.plot([tx + sgn * W / 2] * 2, [ty - half, ty + half], color=ORANGE, lw=2.2)
    ax.text(tx, ty - W / 2 - 17, "NHÌN TRÊN", ha="center", fontsize=8, weight="bold")
    cr = p["body.corner_r"]
    ax.annotate(f"R{cr:g} (giả định)", (tx - W / 2 + cr * (1 - 0.7071), ty + W / 2 - cr * (1 - 0.7071)),
                (tx - W / 2 - 3, ty + W / 2 + 8), fontsize=6.3, ha="right", arrowprops=dict(arrowstyle="-", lw=0.4))
    dim_h(ax, ty - W / 2 - 7, tx - W / 2, tx + W / 2, f"{W:g}", ext_from=ty - W / 2)
    dim_h(ax, ty + W / 2 + 7, tx - half, tx + half, f"{2*half:g} (mặt phẳng nhãn)", ext_from=ty + W / 2)
    bx, by = 300, 112
    draw_lines(ax, hlr_edges(outer.val(), (0, 0, -1), (1, 0, 0)), bx, by)
    ax.text(bx, by + W / 2 + 5, "NHÌN DƯỚI (đáy)", ha="center", fontsize=8, weight="bold")
    ax.text(bx, by - W / 2 - 6, f"màng trung tâm R{p['base.diaphragm_r']:g}, lõm {p['base.diaphragm_depth']:g}", ha="center", fontsize=6.3)

    # --- kích thước hình chiếu trước
    xl = fx - W / 2 - 8
    marks = [(0, "đáy"), (p["zones.heel_top_z"], "đỉnh gót"), (p["zones.label_top_z"], "đỉnh nhãn"),
             (p["zones.shoulder_start_z"], "vai bắt đầu"), (p["zones.shoulder_top_z"], "chân cổ"), (H, "đỉnh")]
    for (a, na), (b, nb) in zip(marks[:-1], marks[1:]):
        dim_v(ax, xl, base_y + a, base_y + b, f"{b-a:g}", ext_to=fx - W / 2 - 1)
    dim_v(ax, xl - 12, base_y, base_y + H, f"{H:g} (ảnh)", ext_to=xl)
    dim_h(ax, base_y - 8, fx - W / 2, fx + W / 2, f"{W:g} (ảnh)", ext_from=base_y)
    dim_h(ax, base_y + H + 8, fx - p["neck.finish_od"] / 2, fx + p["neck.finish_od"] / 2,
          f"Ø{p['neck.finish_od']:g} (ảnh; cổ PLACEHOLDER)", ext_from=base_y + H)
    # chú thích đặc điểm
    ax.annotate("rãnh cứng hóa trên\n(ngoài vùng nhãn)", (fx + W / 2, base_y + p["features.upper_band_z"]),
                (fx + W / 2 + 14, base_y + p["features.upper_band_z"] + 12), fontsize=6, arrowprops=dict(arrowstyle="-", lw=0.4))
    ax.annotate("rãnh cứng hóa dưới\n(ngoài vùng nhãn)", (fx + W / 2, base_y + p["features.lower_band_z"]),
                (fx + W / 2 + 14, base_y + p["features.lower_band_z"] - 2), fontsize=6, arrowprops=dict(arrowstyle="-", lw=0.4))
    ax.annotate("vai dạng vòm mặt phẳng\n(giao tuyến mặt phẳng × mặt tròn xoay)", (fx + W / 2 - 4, base_y + 146),
                (fx + W / 2 + 14, base_y + 160), fontsize=6, arrowprops=dict(arrowstyle="-", lw=0.4))

    # --- ghi chú (cột phải)
    notes = [
        ("GHI CHÚ", True),
        ("1. Hình học concept để xem/chỉnh. Không chứng minh chịu nhiệt, chân không hay độ bền.", False),
        ("2. Giá trị từ ảnh: 61×61, cao 188, miệng 38. Mọi kích thước khác là GIẢ ĐỊNH (xem trang 2).", False),
        ("3. Cổ/finish: placeholder hình trụ. Không suy chuẩn ren từ 38 mm; không dựng ren.", False),
        (f"4. Dung tích tính từ khoang trong: đầy miệng {res['cavity_brimful_ml']} ml; mức 500 ml ở z={res['fill_level_z_for_target_mm']} mm, khoảng trống ~{res['headspace_pct_at_target']}% thể tích đầy miệng. Giá trị hình học, chưa phải dung tích chiết rót đã duyệt.", False),
        ("5. Vùng nhãn: 4 mặt phẳng, không gân ngang, chừa mép 3 mm so với rãnh.", False),
        ("6. Hấp thụ chân không: chưa thiết kế/kiểm chứng. Xem trang 2.", False),
        ("7. Không suy khối lượng hot-fill từ chai thường 36 g.", False),
        ("8. Cần nhà máy cung cấp: finish & nắp, phôi, độ dày thành, nhiệt độ/thời gian chiết rót, quy trình thổi chịu nhiệt, lượng chân không cần hấp thụ, khuôn.", False),
    ]
    import textwrap
    nx, ny = 338, 262
    yy = ny
    for t, b in notes:
        lines = textwrap.wrap(t.strip(), 54) if not b else [t]
        for k, ln in enumerate(lines):
            ax.text(nx + (3 if (k and not b) else 0), yy, ln, fontsize=6.2 if not b else 8,
                    weight="bold" if b else "normal", va="top")
            yy -= 4.3 if not b else 6
        yy -= 1.2
    title_block(ax, p, res, 1)
    pdf.savefig(fig); plt.close(fig)


def page2(pdf, p, res):
    fig = plt.figure(figsize=(A3[0] / 25.4, A3[1] / 25.4))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, A3[0]); ax.set_ylim(0, A3[1]); ax.axis("off")
    ax.add_patch(Rectangle((8, 8), A3[0] - 16, A3[1] - 16, fc="none", ec="k", lw=1.0))
    ax.text(A3[0] / 2, A3[1] - 16, STAMP, ha="center", va="center", fontsize=20, weight="bold", color=RED)
    ax.text(14, A3[1] - 30, "TRANG 2 — Sơ đồ nguyên lý hấp thụ chân không (CHƯA KIỂM CHỨNG) & phân loại tham số",
            fontsize=10, weight="bold")

    # ---- sơ đồ đáy: hai trạng thái của màng
    rd, d0 = p["base.diaphragm_r"], p["base.diaphragm_depth"]
    d1 = d0 + 3.0

    def dome_pts(r, d, n=60):
        rs = (r * r + d * d) / (2 * d)
        return [(-r + 2 * r * i / n, d - rs + math.sqrt(rs ** 2 - (-r + 2 * r * i / n) ** 2)) for i in range(n + 1)]

    def vol(r, d):
        return math.pi * d * (3 * r * r + d * d) / 6 / 1000.0

    Wd = p["body.width"]
    K = 1.6                                    # phóng đại sơ đồ để đọc rõ
    for k, (cx, d, title) in enumerate([(68, d0, "Trạng thái A — sau chiết rót nóng / đóng nắp\n(vị trí màng như dựng trong CAD)"),
                                         (182, d1, "Trạng thái B — sau khi nguội (minh họa)\nmàng dịch vào trong, khoang nhỏ lại")]):
        y0 = 190
        ax.plot([cx - Wd / 2 * K, cx - rd * K], [y0, y0], color="k", lw=1.2)
        ax.plot([cx + rd * K, cx + Wd / 2 * K], [y0, y0], color="k", lw=1.2)
        pts = dome_pts(rd, d)
        ax.plot([cx + x * K for x, _ in pts], [y0 + y * K for _, y in pts], color="#1560b0", lw=1.6)
        if k == 1:
            pa = dome_pts(rd, d0)
            ax.plot([cx + x * K for x, _ in pa], [y0 + y * K for _, y in pa], color="#1560b0", lw=0.8, ls=(0, (4, 3)))
            ax.text(cx + 8, y0 + (d0 - 1.5) * K, "vị trí A", fontsize=6, color="#1560b0")
        ax.plot([cx - Wd / 2 * K] * 2, [y0, y0 + 48], color="k", lw=1.2)
        ax.plot([cx + Wd / 2 * K] * 2, [y0, y0 + 48], color="k", lw=1.2)
        ax.text(cx, y0 + 60, title, ha="center", va="bottom", fontsize=7, weight="bold")
        ax.text(cx, y0 - 9, f"độ lõm {d:g} mm, Ø{2*rd:g}  (sơ đồ phóng {K:g}×)", ha="center", fontsize=6.5)
        ax.text(cx, y0 + 30, "khoang chứa sản phẩm", ha="center", fontsize=6.5, color="#555")
        ax.text(cx - Wd / 2 * K - 2, y0 + 24, "mặt nhãn\n(không đổi)", ha="right", fontsize=6, color=ORANGE, va="center")
    ax.annotate("", (182, 190 + d0 * K + 2), (182, 190 + (d0 + 3) * K - 1), arrowprops=dict(arrowstyle="->", lw=0.9, color="#1560b0"))
    dv = vol(rd, d1) - vol(rd, d0)
    ax.text(125, 160, f"Ví dụ minh họa hình học: màng dịch thêm {d1-d0:g} mm ⇒ thể tích khoang giảm ≈ {dv:.1f} ml.\n"
            "Đây chỉ là phép tính chỏm cầu, KHÔNG phải năng lực hấp thụ thật: hành trình thực, độ dày màng,\n"
            "ngưỡng đảo/lật và độ cứng phụ thuộc phôi, quy trình thổi chịu nhiệt và khuôn — chưa có dữ liệu.",
            ha="center", va="top", fontsize=6.8, color=RED)

    txt = [
        ("PHÂN BIỆT BA LỚP (không gộp làm một)", True),
        ("A. Kết cấu tăng độ cứng (trong CAD): bo góc R11, vai dạng vòm, hai rãnh nông chu vi ngoài vùng nhãn,", False),
        ("   gót bo, vòng đỡ đáy. Giúp chống biến dạng chung; KHÔNG hấp thụ chân không.", False),
        ("B. Cơ chế hấp thụ chân không khi nguội (cần thiết kế riêng): hướng ưu tiên là màng ở ĐÁY chuyển", False),
        ("   động, vì không cắt vào 4 mặt nhãn. Trong CAD chỉ có màng lõm tĩnh — chưa phải cơ cấu hoạt động.", False),
        ("   Một đáy lõm thông thường KHÔNG được coi là đã xử lý chân không.", False),
        ("C. Phôi + quy trình thổi chịu nhiệt + cổ/nắp phù hợp: quyết định chai có chịu được nhiệt hay không;", False),
        ("   không thể suy ra từ CAD. Cần nhà máy xác nhận.", False),
        ("RỦI RO CHÍNH: mặt phẳng 39 mm không gân dễ bị lõm vào (paneling) nếu đáy hấp thụ chưa đủ.", True),
        ("Nếu đáy không đủ, phải đánh đổi: (1) mặt nhãn hơi cong lồi, (2) lõm nông trên mặt/ở góc làm giảm", False),
        ("   diện tích nhãn phẳng, hoặc (3) tăng độ dày/khối lượng phôi. Chưa có dữ liệu để chọn.", False),
        ("Không sao chép cấu trúc độc quyền của hãng khác; sơ đồ này chỉ là nguyên lý chung.", False),
    ]
    for i, (t, b) in enumerate(txt):
        ax.text(14, 128 - i * 5.8, t, fontsize=7.2 if not b else 8, weight="bold" if b else "normal", va="top",
                color=RED if b and i else "k")

    # ---- bảng tham số
    cols = [(262, "Tham số"), (330, "Giá trị"), (362, "Nguồn")]
    ax.text(262, A3[1] - 40, "PHÂN LOẠI THAM SỐ", fontsize=8, weight="bold")
    for x, t in cols:
        ax.text(x, A3[1] - 47, t, fontsize=6.8, weight="bold")
    ax.plot([258, 410], [A3[1] - 49, A3[1] - 49], color="k", lw=0.5)
    y = A3[1] - 53
    for name, val, cls, _ in p.rows():
        v = str(val)
        v = v if len(v) < 16 else v[:14] + "…"
        ax.text(262, y, name, fontsize=5.6, va="center")
        ax.text(330, y, v, fontsize=5.6, va="center")
        ax.text(362, y, CLASS_LABEL[cls], fontsize=5.6, va="center", color=CLS_COLOR[cls], weight="bold")
        y -= 4.7
    ax.text(262, y - 2, "Chi tiết ghi chú từng tham số: config/bottle_500_params.toml", fontsize=6, color="#444")
    ax.text(262, y - 7, "Giá trị 'Giả định' không phải thông số sản xuất.", fontsize=6, color=RED)
    title_block(ax, p, res, 2)
    pdf.savefig(fig); plt.close(fig)


def make_pdf(path, p, res, outer, hollow):
    with PdfPages(path) as pdf:
        page1(pdf, p, res, outer, hollow)
        page2(pdf, p, res)
        info = pdf.infodict()
        info["Title"] = "Chai 500 ml hot-fill — concept, chưa duyệt sản xuất"
