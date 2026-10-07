"""Dựng concept chai PET 500 ml (hình học). KHÔNG phải mô hình sản xuất / chịu nhiệt."""
import math
import cadquery as cq

from .params import Params


def _prism(w, d, r, z0, z1):
    return (cq.Workplane("XY").workplane(offset=z0).rect(w, d).extrude(z1 - z0)
            .edges("|Z").fillet(r))


def _envelope(p):
    """Vật quay bao vai: thẳng đến shoulder_start_z, rồi thu theo đường cong lồi về cổ."""
    zs, zt = p["zones.shoulder_start_z"], p["zones.shoulder_top_z"]
    r_end = p["neck.finish_od"] / 2 + 2.0          # gờ vai rộng hơn cổ 2 mm
    half_diag = (p["body.width"] / 2 - p["body.corner_r"]) * math.sqrt(2) + p["body.corner_r"]
    r_big = half_diag + 1.5
    n = 28
    pe = p["zones.shoulder_curve_exp"]
    pts = []
    for i in range(1, n + 1):
        sfrac = i / n
        pts.append((r_end + (r_big - r_end) * (1 - sfrac ** pe), zs + (zt - zs) * sfrac))
    pts[-1] = (r_end, zt)
    prof = (cq.Workplane("XZ").moveTo(0, -5).lineTo(r_big, -5).lineTo(r_big, zs)
            .spline(pts, tangents=[(0, 1), (-0.6, 0.8)], includeCurrent=True)
            .lineTo(0, zt).close())
    return prof.revolve(360, (0, 0, 0), (0, 1, 0))


def _band_cutter(p, zc):
    w, d, r = p["body.width"], p["body.depth"], p["body.corner_r"]
    bw, bd = p["features.band_width"], p["features.band_depth"]
    z0 = zc - bw / 2
    outer = cq.Workplane("XY").workplane(offset=z0).rect(w + 20, d + 20).extrude(bw)
    inner = _prism(w - 2 * bd, d - 2 * bd, max(r - bd, 1.0), z0 - 1, z0 + bw + 1)
    return outer.cut(inner)


def _base_recess(p):
    rd, dp = p["base.diaphragm_r"], p["base.diaphragm_depth"]
    rs = (rd ** 2 + dp ** 2) / (2 * dp)
    zc = dp - rs
    mid = (rd / 2, zc + math.sqrt(rs ** 2 - (rd / 2) ** 2))
    prof = (cq.Workplane("XZ").moveTo(0, -1).lineTo(rd, -1).lineTo(rd, 0)
            .threePointArc(mid, (0, dp)).close())
    return prof.revolve(360, (0, 0, 0), (0, 1, 0))


def build_outer(p: Params, with_ring=True):
    w, d, r = p["body.width"], p["body.depth"], p["body.corner_r"]
    zt = p["zones.shoulder_top_z"]
    prism = _prism(w, d, r, 0, zt)
    prism = prism.faces("<Z").edges().fillet(p["features.heel_fillet_r"])
    body = prism.intersect(_envelope(p))
    if p["features.upper_band_enable"]:
        body = body.cut(_band_cutter(p, p["features.upper_band_z"]))
    if p["features.lower_band_enable"]:
        body = body.cut(_band_cutter(p, p["features.lower_band_z"]))
    body = body.cut(_base_recess(p))

    H = p["body.height_total"]
    neck_r = p["neck.finish_od"] / 2
    neck = cq.Workplane("XY").workplane(offset=zt - 4).circle(neck_r).extrude(H - zt + 4)
    rz, rh = p["neck.support_ring_z"], p["neck.support_ring_h"]
    ring = cq.Workplane("XY").workplane(offset=rz).circle(p["neck.support_ring_od"] / 2).extrude(rh)
    body = body.union(neck)
    return body.union(ring) if with_ring else body


def build_hollow(p: Params, outer):
    """Vỏ rỗng: thành đồng đều t_model (giả định) + ống finish placeholder. Chỉ là mô hình hình học."""
    t = p["wall.t_model"]
    shell = build_outer(p, with_ring=False).faces(">Z").shell(-t)
    rz, rh = p["neck.support_ring_z"], p["neck.support_ring_h"]
    ring = (cq.Workplane("XY").workplane(offset=rz).circle(p["neck.support_ring_od"] / 2)
            .circle(p["neck.finish_id"] / 2).extrude(rh))
    zt = p["zones.shoulder_top_z"]
    H = p["body.height_total"]
    r_in = p["neck.finish_id"] / 2
    r_out = p["neck.finish_od"] / 2 - t * 0.5
    insert = (cq.Workplane("XY").workplane(offset=zt - 1).circle(r_out).circle(r_in)
              .extrude(H - zt + 1))
    return shell.union(insert).union(ring)   # vòng đỡ khuyên, thông lỗ miệng


def cavity_of(outer, hollow):
    return outer.cut(hollow)


def volume_ml(wp):
    return wp.val().Volume() / 1000.0


def fill_volume_ml(cavity, z_level):
    box = cq.Workplane("XY").box(200, 200, z_level, centered=(True, True, False))
    return volume_ml(cavity.intersect(box))


def fill_level_for_ml(cavity, target_ml, lo=100.0, hi=188.0):
    for _ in range(40):
        mid = (lo + hi) / 2
        if fill_volume_ml(cavity, mid) < target_ml:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2
