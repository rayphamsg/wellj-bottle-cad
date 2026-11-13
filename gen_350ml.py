# Sinh ban ve chai PET 350ml (don vi mm, kho A3 420x297, ty le 1:1)
import math
H, R, RN, CX, Y0 = 165, 28.5, 14, 70, 32   # cao, ban kinh than, ban kinh co, tam, goc Y
Lh, Lw = 74, 179                              # cao nhan, chu vi nhan (pi*57)
PANELS, PW, PY1, PY2 = 6, 23, 86, 146
o = []
def a(s): o.append(s)
def L(x1,y1,x2,y2,c="#000",w=.35,d=""): a(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="{w}" {f"stroke-dasharray=\"{d}\"" if d else ""}/>')
def T(x,y,s,sz=3.5,anc="middle",w="normal"): a(f'<text stroke="none" fill="#000" x="{x}" y="{y}" font-size="{sz}" text-anchor="{anc}" font-weight="{w}">{s}</text>')
def dimv(x,ya,yb,txt,side=-1):  # kich thuoc dung
    L(x,ya,x,yb,w=.25); 
    for y in (ya,yb): L(x-1.2,y,x+1.2,y,w=.25)
    a(f'<text stroke="none" fill="#000" transform="translate({x+side*1.2*-1+ (-1.5 if side<0 else 3.5)},{(ya+yb)/2}) rotate(-90)" font-size="3.5" text-anchor="middle">{txt}</text>')
def dimh(y,xa,xb,txt):
    L(xa,y,xb,y,w=.25)
    for x in (xa,xb): L(x,y-1.2,x,y+1.2,w=.25)
    T((xa+xb)/2,y-1.5,txt)
Y=lambda y:Y0+y
a('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 297" width="420mm" height="297mm" font-family="Arial,sans-serif" fill="none" stroke="#000">')
a('<rect width="420" height="297" fill="#fff" stroke="none"/><rect x="5" y="5" width="410" height="287" stroke-width=".7"/>')
# --- profile mat truoc
def side(s):
    p=lambda x,y:f"{CX+s*x:.2f},{Y(y):.2f}"
    return p
r=side(1); l=side(-1)
d=(f"M {l(13.5,0)} L {r(13.5,0)} L {r(13.5,19)} L {r(16.5,21)} L {r(16.5,23.5)} L {r(14.5,24.5)} L {r(14.5,27)} "
   f"C {r(23,28)} {r(R,44)} {r(R,74)} L {r(R,148)} C {r(R,158)} {r(25,163)} {r(22,165)} L {l(22,165)} "
   f"C {l(25,163)} {l(R,158)} {l(R,148)} L {l(R,74)} C {l(R,44)} {l(23,28)} {l(14.5,27)} "
   f"L {l(14.5,24.5)} L {l(16.5,23.5)} L {l(16.5,21)} L {l(13.5,19)} Z")
a(f'<path d="{d}" stroke-width=".8" fill="#eef4f8"/>')
for y in (3,6.5,10,13.5): L(CX-13.5,Y(y),CX+13.5,Y(y),w=.25)   # ren ren
L(CX-R,Y(74),CX+R,Y(74),w=.3,d="1.5 1")                         # vai/than
L(CX-R,Y(148),CX+R,Y(148),w=.3,d="1.5 1")
for th in (0,60,-60):                                            # gan vai
    sx=math.sin(math.radians(th)); L(CX+14.5*sx,Y(27),CX+R*sx,Y(74),w=.25)
for th,w in ((0,PW),(60,PW*.5),(-60,PW*.5)):                     # o loi than
    xc=CX+R*math.sin(math.radians(th)); a(f'<rect x="{xc-w/2:.2f}" y="{Y(PY1)}" width="{w:.2f}" height="{PY2-PY1}" rx="{min(7,w/2):.1f}" stroke-width=".4"/>')
a(f'<rect x="{CX-R-.01}" y="{Y(74)}" width="{2*R}" height="{Lh}" stroke="#d00" stroke-width=".4" stroke-dasharray="2 1"/>')
pass
L(CX,Y(-6),CX,Y(H+4),w=.2,d="6 1 1 1")
# kich thuoc
dimv(CX+R+16,Y(0),Y(H),f"{H}±2",1); L(CX+R,Y(H),CX+R+17,Y(H),w=.2); L(CX+14,Y(0),CX+R+17,Y(0),w=.2)
dimv(CX-R-8,Y(74),Y(148),f"{Lh}",-1); L(CX-R,Y(74),CX-R-9,Y(74),w=.2); L(CX-R,Y(148),CX-R-9,Y(148),w=.2)
dimv(CX-R-18,Y(0),Y(21),"21",-1); L(CX-13.5,Y(0),CX-R-19,Y(0),w=.2); L(CX-16.5,Y(21),CX-R-19,Y(21),w=.2)
dimh(Y(-4),CX-13.5,CX+13.5,"Ø28"); dimh(Y(H+7),CX-R,CX+R,"Ø57±1")
T(CX+R+24,Y(30),"Mức rót: 360ml±5 @85°C",3,"start"); T(CX+R+24,Y(34),"350ml±5 sau khi nguội 20°C",3,"start")
T(CX,Y(H+16),"MẶT TRƯỚC (1:1)",4,w="bold")
# --- trai nhan phang
LX,LY=135,Y(60)
T(LX+Lw/2,LY-8,"TRẢI PHẲNG VÙNG NHÃN (1:1)",4,w="bold")
a(f'<rect x="{LX}" y="{LY}" width="{Lw}" height="{Lh}" stroke="#d00" stroke-width=".6"/>')
for i in range(PANELS):
    xc=LX+Lw/PANELS*(i+.5); a(f'<rect x="{xc-PW/2:.2f}" y="{LY+PY1-74}" width="{PW}" height="{PY2-PY1}" rx="7" fill="#dde8ee" stroke-width=".4"/>')
    T(xc,LY+PY1-74+(PY2-PY1)/2+1,f"{i+1}",3)
dimh(LY+Lh+7,LX,LX+Lw,f"{Lw} (chu vi π×57)"); dimv(LX-7,LY,LY+Lh,f"{Lh}",-1)
dimh(LY-2,LX+Lw/PANELS*.5-PW/2,LX+Lw/PANELS*.5+PW/2,f"{PW}")
dimv(LX+Lw+8,LY+PY1-74,LY+PY2-74,f"{PY2-PY1}",1)
dimv(LX+Lw+16,LY,LY+PY1-74,f"{PY1-74}",1)
T(LX+Lw/2,LY+Lh+16,"Nhãn nên dán trên phần thân thẳng; 6 ô lõm cách đều 60° (cần đối chiếu mẫu thật)",3)
# --- top / bottom
VX=360
T(VX,Y(8),"TOP VIEW",4,w="bold"); a(f'<circle cx="{VX}" cy="{Y(32)}" r="16.5"/><circle cx="{VX}" cy="{Y(32)}" r="14"/><circle cx="{VX}" cy="{Y(32)}" r="11"/>')
T(VX,Y(110),"BOTTOM VIEW",4,w="bold"); by=Y(140)
a(f'<circle cx="{VX}" cy="{by}" r="{R}"/><circle cx="{VX}" cy="{by}" r="22"/><circle cx="{VX}" cy="{by}" r="6"/>')
for k in range(5):
    t=math.radians(k*72+18); a(f'<path d="M {VX+6*math.cos(t):.1f},{by+6*math.sin(t):.1f} Q {VX+15*math.cos(t+.5):.1f},{by+15*math.sin(t+.5):.1f} {VX+20*math.cos(t):.1f},{by+20*math.sin(t):.1f}" stroke-width=".4"/>')
# --- khung ten
a('<rect x="5" y="240" width="410" height="52" stroke-width=".6"/>')
L(5,240,415,240,w=.7)
L(70,240,70,292,w=.4); L(260,240,260,292,w=.4)
for x in (330,370): L(x,266,x,292,w=.4)
L(260,266,415,266,w=.4)
T(37,255,"Công Ty TNHH-SXTM",3.5,w="bold"); T(37,261,"Dịch Vụ Minh Thông",3.5,w="bold"); T(165,252,"Khách Hàng",4)
T(337,251,"Chai Pet",5,w="bold"); T(337,262,"350ml – HOT FILL – Ø28",5,w="bold")
T(300,283,"Scale 1:1",3.5); T(345,283,"Gram: ___",3.5); T(392,283,"Trang 1",3.5)
T(300,273,"Vật liệu: PET",3.5)
T(165,272,"BẢN NHÁP – kích thước ước lượng từ ảnh/video, cần đo lại mẫu thật",3.2)
a('</svg>')
open("chai-350ml.svg","w").write("\n".join(o))
