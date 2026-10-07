"""Dựng concept chai 500 ml: STEP, preview, (bản vẽ + báo cáo ở bước sau).
Chạy: .venv/bin/python build.py [model|previews|all]
"""
import json
import sys
from pathlib import Path

import cadquery as cq

from cad.params import Params
from cad import model as M
from cad import render as R
from cad import drawing as D
from cad import brief_drawing as BD
from cad import brief as B

OUT = Path(__file__).parent / "out"
OUT.mkdir(exist_ok=True)
STAMP = "CONCEPT — CHƯA DUYỆT SẢN XUẤT"


def build_model(p):
    outer = M.build_outer(p)
    hollow = M.build_hollow(p, outer)
    cavity = M.cavity_of(outer, hollow)
    return outer, hollow, cavity


def checks(p, outer, hollow, cavity):
    res = {}
    for name, wp in (("outer", outer), ("hollow", hollow), ("cavity", cavity)):
        s = wp.val()
        res[f"{name}_valid"] = bool(s.isValid())
        res[f"{name}_solids"] = len(wp.solids().vals())
    bb = outer.val().BoundingBox()
    res["bbox_mm"] = [round(bb.xlen, 3), round(bb.ylen, 3), round(bb.zlen, 3)]
    H = p["body.height_total"]
    res["bbox_matches_ref"] = (abs(bb.xlen - p["body.width"]) < 0.01 and abs(bb.ylen - p["body.depth"]) < 0.01
                               and abs(bb.zlen - H) < 0.01)
    brim = M.volume_ml(cavity)
    zf = H - p["capacity.fill_point_drop_from_top"]
    res["cavity_brimful_ml"] = round(brim, 1)
    res["cavity_ml_at_assumed_fill_point"] = round(M.fill_volume_ml(cavity, zf), 1)
    res["assumed_fill_point_z_mm"] = zf
    z500 = M.fill_level_for_ml(cavity, p["capacity.target_fill_ml"])
    res["fill_level_z_for_target_mm"] = round(z500, 2)
    res["headspace_pct_at_target"] = round(100 * (brim - p["capacity.target_fill_ml"]) / brim, 1)
    z_lo, z_hi, half = R.label_zone(p)
    res["label_zone"] = dict(z_lo=z_lo, z_hi=z_hi, flat_width=2 * half, height=z_hi - z_lo,
                             area_per_face_mm2=round(2 * half * (z_hi - z_lo), 0),
                             area_4_faces_mm2=round(4 * 2 * half * (z_hi - z_lo), 0))
    return res


def export_step(outer, hollow):
    cq.exporters.export(hollow, str(OUT / "chai_500ml_concept.step"))        # khoang trong giả định
    cq.exporters.export(outer, str(OUT / "chai_500ml_concept_outer.step"))   # chỉ hình học ngoài
    for f in ("chai_500ml_concept.step", "chai_500ml_concept_outer.step"):
        back = cq.importers.importStep(str(OUT / f))
        assert back.val().isValid() and len(back.solids().vals()) == 1, f
        print("STEP OK:", f, round(back.val().Volume() / 1000, 1), "cm3")


def previews(p, outer, hollow):
    mesh = R.Mesh(outer.val())
    foot = "Concept hình học: neck/finish là placeholder (xám). Không phải bản vẽ sản xuất."
    names = ["front", "side", "top", "bottom", "persp", "persp_low"]
    imgs = []
    for v in names:
        im = R.render(mesh, mesh.tri_colors(p), v)
        R.caption(im, R.VIEWS[v]["title"], "mm — " + STAMP)
        im.save(OUT / f"preview_{v}.png")
        imgs.append(im)
        print("saved", v)
    R.sheet(imgs, 3, OUT / "preview_tong_hop.png", f"Chai 500 ml hot-fill — {STAMP}", foot)

    # vùng nhãn tô màu: preview riêng
    lab = []
    for v in ("front", "side", "persp"):
        im = R.render(mesh, mesh.tri_colors(p, label=True), v)
        R.caption(im, R.VIEWS[v]["title"] + " — vùng nhãn (cam)", "4 mặt phẳng, liên tục, không gân ngang")
        lab.append(im)
    R.sheet(lab, 3, OUT / "preview_vung_nhan.png", f"Vùng nhãn — {STAMP}",
            "Cam = vùng nhãn phẳng liên tục (đã chừa mép so với rãnh). Xám = cổ placeholder.")

    # mặt cắt khoang trong (mô hình hình học, thành đều giả định)
    half = cq.Workplane("XY").box(200, 100, 300, centered=(True, False, False)).translate((0, 0, -5))
    cut = hollow.intersect(half)
    ms = R.Mesh(cut.val())
    im = R.render(ms, ms.tri_colors(p), "front")
    R.caption(im, "Mặt cắt giữa (y=0)", "thành đều giả định — KHÔNG đại diện phân bố độ dày sau thổi")
    im2 = R.render(ms, ms.tri_colors(p), "persp")
    R.caption(im2, "Mặt cắt, phối cảnh", STAMP)
    R.sheet([im, im2], 2, OUT / "preview_mat_cat.png", f"Mặt cắt khoang trong — {STAMP}",
            "Mô hình hình học với thành đều t giả định; chỉ minh họa khoang trong.")


if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else "all"
    p = Params()
    outer, hollow, cavity = build_model(p)
    res = checks(p, outer, hollow, cavity)
    print(json.dumps(res, indent=1, ensure_ascii=False))
    (OUT / "kiem_tra.json").write_text(json.dumps(res, indent=1, ensure_ascii=False))
    if stage in ("model", "all", "previews"):
        export_step(outer, hollow)
    if stage in ("previews", "all"):
        previews(p, outer, hollow)
    if stage in ("drawing", "all"):
        D.make_pdf(OUT / "ban_ve_so_bo_500ml.pdf", p, res, outer, hollow)
        print("PDF OK")
    if stage in ("brief", "all"):
        BD.make_pdf(OUT / "ban_ve_gui_nha_may_500ml.pdf", p, res, outer, hollow)
        print("BRIEF PDF OK")
        B.write_all(p, res)
        print("BRIEF DOCS OK")
