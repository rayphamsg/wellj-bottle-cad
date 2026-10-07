"""Render preview PNG bằng rasterizer numpy (z-buffer). Không cần GL/GPU.

Chỉ để xem hình dáng. Không phải mô phỏng vật liệu hay kết cấu.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

PET_COLOR = (150, 195, 222)
NECK_COLOR = (170, 170, 175)
LABEL_COLOR = (238, 120, 36)


class Mesh:
    def __init__(self, shape, tol=0.08, ang=0.15):
        verts, tris = shape.tessellate(tol, ang)
        self.v = np.array([(p.x, p.y, p.z) for p in verts], float)
        self.t = np.array(tris, int)
        a, b, c = (self.v[self.t[:, i]] for i in range(3))
        fn = np.cross(b - a, c - a)
        area = np.linalg.norm(fn, axis=1)
        self.fn = fn / np.maximum(area, 1e-12)[:, None]
        self.centroid = (a + b + c) / 3
        vn = np.zeros_like(self.v)
        for i in range(3):
            np.add.at(vn, self.t[:, i], fn)       # trọng số theo diện tích
        n = np.linalg.norm(vn, axis=1)
        self.vn = vn / np.maximum(n, 1e-12)[:, None]

    def tri_colors(self, p, label=False):
        col = np.tile(np.array(PET_COLOR, float), (len(self.t), 1))
        zt = p["zones.shoulder_top_z"]
        c = self.centroid
        col[c[:, 2] > zt + 0.5] = NECK_COLOR
        if label:
            m = label_mask(self, p)
            col[m] = LABEL_COLOR
        return col


def label_zone(p):
    """Vùng nhãn phẳng liên tục trên mỗi mặt: (z_lo, z_hi, nửa_rộng)."""
    z_lo = p["zones.heel_top_z"] + p["zones.label_margin_z"]
    z_hi = p["zones.label_top_z"] - p["zones.label_margin_z"]
    half = p["body.width"] / 2 - p["body.corner_r"]
    return z_lo, z_hi, half


def label_mask(mesh, p):
    z_lo, z_hi, half = label_zone(p)
    hw, hd = p["body.width"] / 2, p["body.depth"] / 2
    c, n = mesh.centroid, mesh.fn
    zok = (c[:, 2] >= z_lo) & (c[:, 2] <= z_hi)
    on_x = (np.abs(np.abs(c[:, 0]) - hw) < 0.2) & (np.abs(n[:, 0]) > 0.99) & (np.abs(c[:, 1]) <= half)
    on_y = (np.abs(np.abs(c[:, 1]) - hd) < 0.2) & (np.abs(n[:, 1]) > 0.99) & (np.abs(c[:, 0]) <= half)
    return zok & (on_x | on_y)


def _basis(e, up):
    e = np.asarray(e, float); e /= np.linalg.norm(e)
    r = np.cross(up, e); r /= np.linalg.norm(r)
    u = np.cross(e, r)
    return np.array([r, u, e])


VIEWS = {
    "front":  dict(e=(0, -1, 0), up=(0, 0, 1), persp=False, title="Nhìn trước"),
    "side":   dict(e=(1, 0, 0), up=(0, 0, 1), persp=False, title="Nhìn bên"),
    "top":    dict(e=(0, 0, 1), up=(0, 1, 0), persp=False, title="Nhìn trên"),
    "bottom": dict(e=(0, 0, -1), up=(0, 1, 0), persp=False, title="Nhìn dưới"),
    "persp":  dict(e=(-0.55, -0.78, 0.30), up=(0, 0, 1), persp=True, title="Phối cảnh"),
    "persp_low": dict(e=(-0.55, -0.78, -0.55), up=(0, 0, 1), persp=True, title="Phối cảnh từ dưới (đáy)"),
}


def render(mesh, colors, view, size=(700, 900), ss=2, margin=0.09):
    cfg = VIEWS[view]
    R = _basis(cfg["e"], cfg["up"])
    center = mesh.v.mean(axis=0) * 0 + (mesh.v.min(0) + mesh.v.max(0)) / 2
    P = (mesh.v - center) @ R.T                   # x phải, y lên, z về phía người xem
    W, H = size[0] * ss, size[1] * ss
    if cfg["persp"]:
        D = 650.0
        f = D / (D - P[:, 2])
        X, Y = P[:, 0] * f, P[:, 1] * f
    else:
        X, Y = P[:, 0], P[:, 1]
    sx = (1 - 2 * margin) * W / (X.max() - X.min())
    sy = (1 - 2 * margin) * H / (Y.max() - Y.min())
    s = min(sx, sy)
    px = W / 2 + (X - (X.max() + X.min()) / 2) * s
    py = H / 2 + 0.035 * H - (Y - (Y.max() + Y.min()) / 2) * s
    Z = P[:, 2]
    Nc = mesh.vn @ R.T                            # pháp tuyến trong hệ camera

    zbuf = np.full((H, W), -1e9)
    img = np.full((H, W, 3), 255.0)
    L1 = np.array([-0.35, 0.45, 0.82]); L1 /= np.linalg.norm(L1)
    L2 = np.array([0.8, 0.2, 0.55]); L2 /= np.linalg.norm(L2)

    for k, tri in enumerate(mesh.t):
        x0, x1, x2 = px[tri]; y0, y1, y2 = py[tri]
        minx, maxx = int(max(np.floor(min(x0, x1, x2)), 0)), int(min(np.ceil(max(x0, x1, x2)), W - 1))
        miny, maxy = int(max(np.floor(min(y0, y1, y2)), 0)), int(min(np.ceil(max(y0, y1, y2)), H - 1))
        if maxx < minx or maxy < miny:
            continue
        den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
        if abs(den) < 1e-12:
            continue
        gx, gy = np.meshgrid(np.arange(minx, maxx + 1) + 0.5, np.arange(miny, maxy + 1) + 0.5)
        w0 = ((y1 - y2) * (gx - x2) + (x2 - x1) * (gy - y2)) / den
        w1 = ((y2 - y0) * (gx - x2) + (x0 - x2) * (gy - y2)) / den
        w2 = 1 - w0 - w1
        m = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
        if not m.any():
            continue
        z = w0 * Z[tri[0]] + w1 * Z[tri[1]] + w2 * Z[tri[2]]
        sub = zbuf[miny:maxy + 1, minx:maxx + 1]
        upd = m & (z > sub)
        if not upd.any():
            continue
        sub[upd] = z[upd]
        n = (w0[upd, None] * Nc[tri[0]] + w1[upd, None] * Nc[tri[1]] + w2[upd, None] * Nc[tri[2]])
        n /= np.maximum(np.linalg.norm(n, axis=1), 1e-9)[:, None]
        shade = 0.30 + 0.55 * np.abs(n @ L1) + 0.30 * np.abs(n @ L2) + 0.25 * np.abs(n[:, 2]) ** 6
        # bóng nhẹ theo góc nhìn để giữ khối ở mặt vuông góc tia nhìn
        out = np.clip(colors[k][None, :] * np.clip(shade, 0, 1.15)[:, None], 0, 255)
        simg = img[miny:maxy + 1, minx:maxx + 1]
        simg[upd] = out
    im = Image.fromarray(img.astype(np.uint8)).resize(size, Image.LANCZOS)
    return im


def caption(im, text, sub=None):
    d = ImageDraw.Draw(im)
    d.text((16, 12), text, fill=(20, 20, 20), font=ImageFont.truetype(FONT_B, 22))
    if sub:
        d.text((16, 42), sub, fill=(90, 90, 90), font=ImageFont.truetype(FONT, 15))
    return im


def sheet(images, cols, path, title, footer):
    w, h = images[0].size
    rows = (len(images) + cols - 1) // cols
    top, bot = 60, 40
    S = Image.new("RGB", (w * cols, h * rows + top + bot), (255, 255, 255))
    for i, im in enumerate(images):
        S.paste(im, ((i % cols) * w, top + (i // cols) * h))
    d = ImageDraw.Draw(S)
    d.text((16, 16), title, fill=(160, 20, 20), font=ImageFont.truetype(FONT_B, 24))
    d.text((16, S.size[1] - 30), footer, fill=(90, 90, 90), font=ImageFont.truetype(FONT, 15))
    S.save(path)
    return S
