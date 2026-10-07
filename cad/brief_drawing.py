"""Bản vẽ gửi nhà máy: đánh dấu VÙNG ỨNG VIÊN để nhà máy xác nhận/loại bỏ. Không sửa hình học.

Các vùng này KHÔNG phải kết cấu đã thiết kế. Đáy trong CAD là hình học tĩnh.
"""
import math
import textwrap

import cadquery as cq
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle, Circle

from .drawing import hlr_edges, draw_lines, dim_h, dim_v, STAMP, RED, ORANGE, A3
from .render import label_zone

BLUE = "#2f6fd0"
GREEN = "#1c8a4a"
PURPLE = "#8a2fb0"
GREY = "#555555"


def wrap_geometry(p):
    z_lo, z_hi, half = label_zone(p)
    R = p["body.corner_r"]
    flat_w = 2 * half
    perim = 4 * flat_w + 2 * math.pi * R
    h = z_hi - z_lo
    return dict(z_lo=z_lo, z_hi=z_hi, half=half, flat_w=flat_w, h=h,
                flat_face=flat_w * h, flat_total=4 * flat_w * h,
                perim=perim, wrap_area=perim * h)


def badge(ax, x, y, n, color="k"):
    ax.text(x, y, str(n), ha="center", va="center", fontsize=8, weight="bold", color=color,
            bbox=dict(boxstyle="circle,pad=0.25", fc="white", ec=color, lw=1.0), zorder=10)


def frame(ax, subtitle, page):
    ax.add_patch(Rectangle((8, 8), A3[0] - 16, A3[1] - 16, fc="none", ec="k", lw=1.0))
    ax.text(A3[0] / 2, A3[1] - 15, STAMP, ha="center", va="center", fontsize=19, weight="bold", color=RED)
    ax.text(A3[0] / 2, A3[1] - 23, subtitle, ha="center", va="center", fontsize=8.5, color=RED)
    x0, y0, w, h = 270, 12, 140, 52
    ax.add_patch(Rectangle((x0, y0), w, h, fc="white", ec="k", lw=0.8))
    ax.plot([x0, x0 + w], [y0 + 24, y0 + 24], color="k", lw=0.5)
    ax.text(x0 + 3, y0 + 47, "Chai PET 500 ml — bản vẽ HỎI NHÀ MÁY (hot-fill)", fontsize=9, weight="bold", va="center")
    ax.text(x0 + 3, y0 + 40, "Hình dáng tham chiếu; không phải thiết kế hot-fill đã kiểm chứng.", fontsize=6.5, va="center")
    ax.text(x0 + 3, y0 + 34, "Cổ/finish placeholder. Đáy là hình học tĩnh. Sơ đồ chuyển động = minh họa.", fontsize=6.5, va="center")
    ax.text(x0 + 3, y0 + 28.5, "Nguồn: config/bottle_500_params.toml · Rev A · 2026-10-07", fontsize=6, va="center", color="#444")
    ax.text(x0 + 3, y0 + 17, "Đơn vị: mm", fontsize=7, va="center")
    ax.text(x0 + 3, y0 + 10, "Tỉ lệ: 1:1 (in A3 100%) — trang 2: 2:1", fontsize=7, va="center")
    ax.text(x0 + 88, y0 + 17, STAMP, fontsize=7, weight="bold", color=RED, va="center")
    ax.text(x0 + 88, y0 + 8, f"Trang {page}/2", fontsize=7, va="center")


def page1(pdf, p, res, outer):
    g = wrap_geometry(p)
    W, H = p["body.width"], p["body.height_total"]
    fig = plt.figure(figsize=(A3[0] / 25.4, A3[1] / 25.4))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, A3[0]); ax.set_ylim(0, A3[1]); ax.axis("off")
    frame(ax, "BẢN VẼ ĐỂ NHÀ MÁY XÁC NHẬN / ĐÁNH DẤU — các vùng ①–⑥ là VỊ TRÍ ỨNG VIÊN, không phải kết cấu đã thiết kế", 1)
    ax.text(148, A3[1] - 32, "NHÀ MÁY: khoanh / ghi trực tiếp lên bản vẽ này (kích thước, chức năng, phần nào loại bỏ, phần nào cần thêm).",
            fontsize=8, weight="bold", color="#111")

    base_y, fx = 64, 72
    # --- vùng ứng viên (tô trước để nét CAD nằm trên)
    def band(z0, z1, color, alpha=0.18, x0=-W / 2, x1=W / 2):
        ax.add_patch(Rectangle((fx + x0, base_y + z0), x1 - x0, z1 - z0, fc=color, ec=color, alpha=alpha, lw=0))
        ax.add_patch(Rectangle((fx + x0, base_y + z0), x1 - x0, z1 - z0, fc="none", ec=color, lw=0.7, ls="--"))
    heel_top = p["zones.heel_top_z"]
    band(0, heel_top, BLUE)                                    # ②
    band(g["z_hi"], p["zones.shoulder_start_z"], BLUE)         # ③ (118..128)
    band(p["zones.shoulder_start_z"], p["zones.shoulder_top_z"], BLUE)   # ④
    # vùng nhãn quấn quanh (nhạt) + phẳng (cam) + hai dải góc (⑤)
    band(g["z_lo"], g["z_hi"], PURPLE, alpha=0.10)
    band(g["z_lo"], g["z_hi"], GREEN, alpha=0.22, x0=-W / 2, x1=-g["half"])
    band(g["z_lo"], g["z_hi"], GREEN, alpha=0.22, x0=g["half"], x1=W / 2)
    band(g["z_lo"], g["z_hi"], ORANGE, alpha=0.30, x0=-g["half"], x1=g["half"])
    draw_lines(ax, hlr_edges(outer.val(), (0, -1, 0), (1, 0, 0)), fx, base_y)

    zc = (g["z_lo"] + g["z_hi"]) / 2
    ax.text(fx, base_y + zc + 10, f"⑥ NHÃN PHẲNG\n{g['flat_w']:.0f} × {g['h']:.0f}\n= {g['flat_face']:,.0f} mm²/mặt".replace(",", "."),
            ha="center", va="center", fontsize=6.6, color="#7a3000", weight="bold")
    ax.text(fx, base_y + zc - 14, "NHÃN QUẤN (gồm bo góc)\nchu vi %.1f × %.0f\n≈ %s mm²" % (g["perim"], g["h"], f"{g['wrap_area']:,.0f}".replace(",", ".")),
            ha="center", va="center", fontsize=6.0, color=PURPLE)
    ax.text(fx, base_y - 24, "NHÌN TRƯỚC (= nhìn bên)", ha="center", fontsize=8, weight="bold")

    # --- huy hiệu & dẫn
    xr = fx + W / 2
    def lead(num, z, color, dx=16, dy=0):
        ax.annotate("", (xr + 0.5, base_y + z), (xr + dx - 3, base_y + z + dy), arrowprops=dict(arrowstyle="-", lw=0.5, color=color))
        badge(ax, xr + dx, base_y + z + dy, num, color)
    lead(2, heel_top / 2, BLUE)
    lead(3, (g["z_hi"] + p["zones.shoulder_start_z"]) / 2, BLUE)
    lead(4, (p["zones.shoulder_start_z"] + p["zones.shoulder_top_z"]) / 2 + 3, BLUE, dy=3)
    ax.annotate("", (fx + g["half"] + 5, base_y + g["z_lo"] + 14), (xr + 13, base_y + g["z_lo"] + 14), arrowprops=dict(arrowstyle="-", lw=0.5, color=GREEN))
    badge(ax, xr + 16, base_y + g["z_lo"] + 14, 5, GREEN)
    ax.annotate("", (fx + 8, base_y + g["z_hi"] - 12), (xr + 13, base_y + g["z_hi"] - 12), arrowprops=dict(arrowstyle="-", lw=0.5, color=ORANGE))
    badge(ax, xr + 16, base_y + g["z_hi"] - 12, 6, ORANGE)
    ax.annotate("", (fx, base_y + 0.5), (fx + 40, base_y - 10), arrowprops=dict(arrowstyle="-", lw=0.5, color=BLUE))
    badge(ax, fx + 43, base_y - 11, 1, BLUE)
    ax.text(fx + 49, base_y - 11, "đáy: xem hình dưới", fontsize=6, va="center", color=BLUE)

    # --- kích thước
    xl = fx - W / 2 - 8
    chain = [0, heel_top, g["z_lo"], g["z_hi"], p["zones.shoulder_start_z"], p["zones.shoulder_top_z"], H]
    for a, b in zip(chain[:-1], chain[1:]):
        if b - a >= 2.9:
            dim_v(ax, xl, base_y + a, base_y + b, f"{b-a:g}", ext_to=fx - W / 2 - 1)
    dim_v(ax, xl - 12, base_y, base_y + H, f"{H:g} (ảnh)", ext_to=xl)
    dim_h(ax, base_y - 9, fx - W / 2, fx + W / 2, f"{W:g} (ảnh)", ext_from=base_y)
    dim_h(ax, base_y + H + 8, fx - p["neck.finish_od"] / 2, fx + p["neck.finish_od"] / 2,
          f"Ø{p['neck.finish_od']:g} (ảnh; cổ PLACEHOLDER)", ext_from=base_y + H)
    ax.text(fx, base_y + H + 15, "CỔ / FINISH: PLACEHOLDER — chờ nhà máy cung cấp chuẩn", ha="center", fontsize=6.3, color=RED)

    # --- bảng vùng (cột giữa)
    tx0, ty = 148, A3[1] - 44
    ax.text(tx0, ty, "VÙNG ỨNG VIÊN & CÂU HỎI (đề nghị ưu tiên 1 → 4; mong nhà máy điều chỉnh)", fontsize=8, weight="bold")
    zones = [
        (1, BLUE, "ĐÁY — màng trung tâm + vòng đỡ  [ưu tiên 1]",
         "Hỏi: có xử lý chân không CHỦ YẾU ở đáy được không? Chức năng nếu có: hấp thụ co thể tích khi nguội bằng cơ cấu đáy chuyển động. "
         "CAD hiện chỉ có màng lõm tĩnh R%g, sâu %g — chưa phải cơ cấu hoạt động. Không chạm vùng nhãn." % (p["base.diaphragm_r"], p["base.diaphragm_depth"])),
        (2, BLUE, "GÓT / dưới nhãn (z 0–%g)  [ưu tiên 2]" % heel_top,
         "Chức năng nếu thêm: ổn định đứng, cứng hóa chuyển tiếp thân–đáy, đỡ tải khi đáy chuyển động, chống lật đáy. Không chạm nhãn."),
        (3, BLUE, "VÀNH TRÊN NHÃN (z %g–%g)  [ưu tiên 2]" % (g["z_hi"], p["zones.shoulder_start_z"]),
         "Chức năng nếu thêm: vòng cứng hóa chu vi, giữ phẳng mép trên mặt nhãn. CAD có rãnh nông %g × %g. Không chạm nhãn." % (p["features.band_width"], p["features.band_depth"])),
        (4, BLUE, "VAI (z %g–%g)  [ưu tiên 3]" % (p["zones.shoulder_start_z"], p["zones.shoulder_top_z"]),
         "Chức năng nếu thêm: cứng hóa vai, giảm co/biến dạng vai khi nguội, chịu tải đứng khi đóng nắp/xếp chồng. Không chạm nhãn; đổi hình vai ảnh hưởng nhận diện."),
        (5, GREEN, "BỐN GÓC thân (R%g, z %g–%g)  [ưu tiên 3]" % (p["body.corner_r"], g["z_lo"], g["z_hi"]),
         "Chức năng nếu thêm: giữ cứng vòng thân (góc là phần cứng nhất). Chỉ đổi bán kính/độ sâu nếu cần. Ảnh hưởng nhãn QUẤN (không ảnh hưởng nhãn phẳng)."),
        (6, ORANGE, "MẶT NHÃN PHẲNG %g × %g  [chỉ phương án cuối]" % (g["flat_w"], g["h"]),
         "Mục tiêu: KHÔNG thêm gân/panel. Nếu bắt buộc: nêu loại (cong lồi / lõm nông), độ sâu mm, vị trí và diện tích nhãn phẳng còn lại."),
    ]
    yy = ty - 8
    for n, col, head, body in zones:
        badge(ax, tx0 + 3, yy - 1.5, n, col)
        ax.text(tx0 + 9, yy, head, fontsize=7, weight="bold", va="center", color=col if col != ORANGE else "#a04a00")
        yy -= 4.5
        for ln in textwrap.wrap(body, 74):
            ax.text(tx0 + 9, yy, ln, fontsize=6.1, va="center")
            yy -= 3.7
        yy -= 3.0

    # --- chú giải
    lg_y = yy - 2
    ax.text(tx0, lg_y, "CHÚ GIẢI MÀU", fontsize=7, weight="bold")
    for i, (c, t) in enumerate([(BLUE, "xanh dương: ngoài vùng nhãn (không chạm nhãn)"),
                                (GREEN, "xanh lá: góc — chạm nhãn quấn, không chạm nhãn phẳng"),
                                (ORANGE, "cam: nhãn phẳng 4 mặt (cần giữ tối đa)"),
                                (PURPLE, "tím nhạt: phạm vi nhãn quấn quanh thân")]):
        ax.add_patch(Rectangle((tx0, lg_y - 6 - i * 4.6), 5, 3, fc=c, ec=c, alpha=0.45))
        ax.text(tx0 + 8, lg_y - 4.7 - i * 4.6, t, fontsize=6.2, va="center")

    # --- hình chiếu trên / dưới (cột phải)
    cx, ty0, by0 = 335, 205, 120
    draw_lines(ax, hlr_edges(outer.val(), (0, 0, 1), (1, 0, 0)), cx, ty0)
    R = p["body.corner_r"]
    for sgn in (1, -1):
        ax.plot([cx - g["half"], cx + g["half"]], [ty0 + sgn * W / 2] * 2, color=ORANGE, lw=2.4)
        ax.plot([cx + sgn * W / 2] * 2, [ty0 - g["half"], ty0 + g["half"]], color=ORANGE, lw=2.4)
    for sx_ in (1, -1):
        for sy_ in (1, -1):
            c = (cx + sx_ * (W / 2 - R), ty0 + sy_ * (W / 2 - R))
            ang = {(1, 1): (0, 90), (-1, 1): (90, 180), (-1, -1): (180, 270), (1, -1): (270, 360)}[(sx_, sy_)]
            from matplotlib.patches import Arc
            ax.add_patch(Arc(c, 2 * R, 2 * R, theta1=ang[0], theta2=ang[1], color=GREEN, lw=2.4))
    ax.text(cx, ty0 + W / 2 + 6, "NHÌN TRÊN — nhãn phẳng (cam), góc (xanh lá) ⑤⑥", ha="center", fontsize=6.8, weight="bold")
    dim_h(ax, ty0 - W / 2 - 7, cx - W / 2, cx + W / 2, f"{W:g}", ext_from=ty0 - W / 2)
    dim_h(ax, ty0 + W / 2 + 16, cx - g["half"], cx + g["half"], f"{g['flat_w']:g} phẳng", ext_from=ty0 + W / 2)
    draw_lines(ax, hlr_edges(outer.val(), (0, 0, -1), (1, 0, 0)), cx, by0)
    rd = p["base.diaphragm_r"]
    ax.add_patch(Circle((cx, by0), rd, fc=BLUE, ec=BLUE, alpha=0.20, lw=0))
    ax.add_patch(Circle((cx, by0), rd, fc="none", ec=BLUE, lw=0.8, ls="--"))
    badge(ax, cx, by0, 1, BLUE)
    ax.text(cx, by0 + W / 2 + 6, "NHÌN DƯỚI — đáy ① (hình học tĩnh)", ha="center", fontsize=6.8, weight="bold")
    ax.text(cx, by0 - W / 2 - 7, f"màng R{rd:g}, lõm {p['base.diaphragm_depth']:g}; gót bo R{p['features.heel_fillet_r']:g}",
            ha="center", fontsize=6.2)
    pdf.savefig(fig); plt.close(fig)


def _clip_lines(ax, lines, ox, oy, k, clip_rect):
    for kind, pts in lines:
        xs = [ox + x * k for x, _ in pts]
        ys = [oy + y * k for _, y in pts]
        ln, = ax.plot(xs, ys, color="k", lw=0.8 if kind != "smooth" else 0.45)
        ln.set_clip_path(clip_rect)


def page2(pdf, p, res, outer, hollow):
    W = p["body.width"]
    fig = plt.figure(figsize=(A3[0] / 25.4, A3[1] / 25.4))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, A3[0]); ax.set_ylim(0, A3[1]); ax.axis("off")
    frame(ax, "ĐÁY: HÌNH HỌC TĨNH TRONG CAD. Sơ đồ chuyển động và mức giảm thể tích chỉ là MINH HỌA — CHƯA KIỂM CHỨNG", 2)

    # mặt cắt đáy 2:1 (z 0..48)
    K, zc = 2.0, 48
    half_box = cq.Workplane("XY").box(200, 100, 300, centered=(True, False, False)).translate((0, 0, -5))
    cut = hollow.intersect(half_box)
    ox, oy = 78, 150
    clip = Rectangle((ox - 36 * K / 1.0 * 0.5 * 2 / 2 - 0, oy - 2), W * K + 8, zc * K + 6, transform=ax.transData)
    clip = Rectangle((ox - W / 2 * K - 4, oy - 4), W * K + 8, zc * K + 8, transform=ax.transData)
    ax.add_patch(Rectangle((ox - W / 2 * K - 4, oy - 4), W * K + 8, zc * K + 8, fc="none", ec="#999", lw=0.5, ls=":"))
    _clip_lines(ax, hlr_edges(cut.val(), (0, -1, 0), (1, 0, 0)), ox, oy, K, clip)
    ax.text(ox, oy + zc * K + 10, "MẶT CẮT ĐÁY (z 0–%d), tỉ lệ 2:1 — hình học TĨNH" % zc, ha="center", fontsize=8, weight="bold")
    ax.text(ox, oy - 12, f"thành đều {p['wall.t_model']} mm là giả định, KHÔNG phải phân bố độ dày sau thổi", ha="center", fontsize=6.3, color=RED)
    rd, d0 = p["base.diaphragm_r"], p["base.diaphragm_depth"]
    ax.annotate("", (ox - rd * K, oy - 1), (ox + rd * K, oy - 1), arrowprops=dict(arrowstyle="<->", lw=0.5))
    ax.text(ox, oy - 6, f"Ø{2*rd:g} màng (giả định)", ha="center", fontsize=6.3)
    ax.annotate("", (ox + 4, oy), (ox + 4, oy + d0 * K), arrowprops=dict(arrowstyle="<->", lw=0.5))
    ax.text(ox + 6, oy + d0 * K / 2, f"lõm {d0:g}", fontsize=6.3, va="center")
    badge(ax, ox + W / 2 * K + 12, oy + 8, 1, BLUE)
    badge(ax, ox + W / 2 * K + 12, oy + (p["zones.heel_top_z"] / 2) * K + 8, 2, BLUE)
    ax.text(ox + W / 2 * K + 18, oy + 8, "đáy", fontsize=6.3, va="center", color=BLUE)
    ax.text(ox + W / 2 * K + 18, oy + (p["zones.heel_top_z"] / 2) * K + 8, "gót", fontsize=6.3, va="center", color=BLUE)

    # sơ đồ minh họa chuyển động
    def dome_pts(r, d, n=60):
        rs = (r * r + d * d) / (2 * d)
        return [(-r + 2 * r * i / n, d - rs + math.sqrt(rs ** 2 - (-r + 2 * r * i / n) ** 2)) for i in range(n + 1)]

    def vol(r, d):
        return math.pi * d * (3 * r * r + d * d) / 6 / 1000.0

    d1 = d0 + 3.0
    Ks = 1.5
    y0 = 150
    ax.text(250, y0 + 58, "SƠ ĐỒ MINH HỌA — CHƯA KIỂM CHỨNG", fontsize=9, weight="bold", color=RED, ha="center")
    for cx, d, title in [(205, d0, "A. sau chiết rót nóng / đóng nắp\n(vị trí màng như CAD)"), (300, d1, "B. sau khi nguội (minh họa)\nmàng dịch vào trong")]:
        ax.plot([cx - W / 2 * Ks / 1.6, cx - rd * Ks / 1.6], [y0, y0], color="k", lw=1.1)
        ax.plot([cx + rd * Ks / 1.6, cx + W / 2 * Ks / 1.6], [y0, y0], color="k", lw=1.1)
        pts = dome_pts(rd, d)
        ax.plot([cx + x * Ks / 1.6 for x, _ in pts], [y0 + y * Ks / 1.6 for _, y in pts], color=BLUE, lw=1.5)
        if d == d1:
            pa = dome_pts(rd, d0)
            ax.plot([cx + x * Ks / 1.6 for x, _ in pa], [y0 + y * Ks / 1.6 for _, y in pa], color=BLUE, lw=0.8, ls=(0, (4, 3)))
        ax.plot([cx - W / 2 * Ks / 1.6] * 2, [y0, y0 + 36], color="k", lw=1.1)
        ax.plot([cx + W / 2 * Ks / 1.6] * 2, [y0, y0 + 36], color="k", lw=1.1)
        ax.text(cx, y0 + 40, title, ha="center", va="bottom", fontsize=6.8, weight="bold")
        ax.text(cx, y0 + 22, "khoang chứa sản phẩm", ha="center", fontsize=6, color=GREY)
        ax.text(cx, y0 - 7, f"lõm {d:g} mm", ha="center", fontsize=6.3)
    dv = vol(rd, d1) - vol(rd, d0)
    ax.text(250, y0 - 16, f"Ví dụ số: màng dịch thêm {d1-d0:g} mm ⇒ khoang giảm ≈ {dv:.1f} ml (tính chỏm cầu thuần hình học).",
            ha="center", fontsize=6.6, color=RED)
    ax.text(250, y0 - 21, "KHÔNG phải năng lực hấp thụ thật. Hành trình, độ dày màng, ngưỡng đảo/lật: chưa có dữ liệu.",
            ha="center", fontsize=6.6, color=RED)

    # khung tuyên bố + câu hỏi đáy
    stm = [
        ("XIN NHÀ MÁY NÊU RÕ VỀ ĐÁY", True),
        ("• Với thiết bị/khuôn hiện có, đáy có thể là cơ cấu chính hấp thụ chân không không? Loại cơ cấu, hành trình (mm), thể tích hấp thụ (ml)?", False),
        ("• Cần thay đổi gì ở đáy so với hình học tĩnh trong CAD (bán kính, độ sâu, gân, vòng đỡ, độ dày)? Đánh dấu trực tiếp lên mặt cắt bên trái.", False),
        ("• Phần còn lại (nếu đáy không đủ) cần bổ sung ở đâu? Dùng ký hiệu ②–⑥ trang 1.", False),
        ("• Có ràng buộc sở hữu trí tuệ/giấy phép với kiểu đáy bạn đề xuất không? Chúng tôi không yêu cầu sao chép cấu trúc độc quyền của hãng khác.", False),
        ("ĐIỀU KHÔNG ĐƯỢC HIỂU SAI", True),
        ("• Đáy trong CAD là hình học tĩnh. Sơ đồ A/B và con số 3,8 ml chỉ minh họa, chưa kiểm chứng.", False),
        ("• Concept này CHƯA đạt hot-fill. Thành đều %g mm, cổ placeholder, mức 500 ml ở z=%g (trong vai) đều là giả định hình học." % (p["wall.t_model"], res["fill_level_z_for_target_mm"]), False),
    ]
    yy = 122
    for t, b in stm:
        for k, ln in enumerate(textwrap.wrap(t, 140) if not b else [t]):
            ax.text(14, yy, ln, fontsize=7.5 if b else 6.6, weight="bold" if b else "normal", va="top",
                    color=RED if (b and "KHÔNG" in t) else "k")
            yy -= 5.6 if b else 4.1
        yy -= 1.6
    pdf.savefig(fig); plt.close(fig)


def make_pdf(path, p, res, outer, hollow):
    with PdfPages(path) as pdf:
        page1(pdf, p, res, outer)
        page2(pdf, p, res, outer, hollow)
        pdf.infodict()["Title"] = "Bản vẽ hỏi nhà máy — chai 500 ml (concept, chưa duyệt sản xuất)"
