# Ban ve chai PET 350ml + trai phang shrink sleeve (mm, A3 420x297, 1:1)
# So do thu cong: A=170, B=90, C1=175, C2=C3=C4=188, D=90, E=19, F(do)=70
import math
A,B,E,D = 170,90,19,90
C1,C2,C3,C4 = 175,188,188,188
R = C2/math.pi/2            # ban kinh than ~29.9
R1 = C1/math.pi/2           # ban kinh o vai ~27.9
TOP = A-E-B                 # mep tren sleeve, tinh tu mieng = 61
CX,Y0 = 72,30
o=[]
a=o.append
Y=lambda y:Y0+y
def L(x1,y1,x2,y2,c="#000",w=.3,d=""):
    a(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{c}" stroke-width="{w}"'+(f' stroke-dasharray="{d}"' if d else '')+'/>')
def T(x,y,s,sz=3.5,anc="middle",w="normal",c="#000"):
    a(f'<text stroke="none" fill="{c}" x="{x}" y="{y}" font-size="{sz}" text-anchor="{anc}" font-weight="{w}">{s}</text>')
def dimv(x,ya,yb,txt,tx=-2):
    L(x,ya,x,yb,w=.25)
    for y in (ya,yb): L(x-1.2,y,x+1.2,y,w=.25)
    a(f'<text stroke="none" fill="#000" transform="translate({x+tx},{(ya+yb)/2}) rotate(-90)" font-size="3.3" text-anchor="middle">{txt}</text>')
def dimh(y,xa,xb,txt):
    L(xa,y,xb,y,w=.25)
    for x in (xa,xb): L(x,y-1.2,x,y+1.2,w=.25)
    T((xa+xb)/2,y-1.5,txt,3.3)
a('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 297" width="420mm" height="297mm" font-family="Arial,sans-serif" fill="none" stroke="#000">')
a('<rect width="420" height="297" fill="#fff" stroke="none"/><rect x="5" y="5" width="410" height="287" stroke-width=".7"/>')
# ---- profile (nua phai -> doi xung)
S0=(13.5,0)
segs=[("L",[],(13.5,19)),("L",[],(16.5,21)),("L",[],(16.5,23.5)),("L",[],(14.5,24.5)),("L",[],(14.5,27)),
 ("C",[(26,30),(R1,42)],(R1,TOP)),("C",[(R1,TOP+4),(R,TOP+6)],(R,TOP+11)),
 ("L",[],(R,A-8)),("C",[(R,A-3),(R-1.5,A-.5)],(R-4,A))]
p=lambda sg,pt:f"{CX+sg*pt[0]:.2f},{Y(pt[1]):.2f}"
d=f"M {p(1,S0)} "
st=S0; starts=[]
for k,c,e in segs:
    starts.append(st); d+=k+" "+" ".join(p(1,q) for q in c+[e])+" "; st=e
d+=f"L {p(-1,st)} "
for (k,c,e),s0 in zip(reversed(segs),reversed(starts)):
    d+=k+" "+" ".join(p(-1,q) for q in list(reversed(c))+[s0])+" "
d+=f"L {p(-1,S0)} Z"
a(f'<path d="{d}" stroke-width=".8" fill="#eef4f8"/>')
for y in (3,6.5,10,13.5): L(CX-13.5,Y(y),CX+13.5,Y(y),w=.25)
L(CX,Y(-6),CX,Y(A+4),w=.2,d="6 1 1 1")
# vung sleeve + cac day chu vi (vi tri gan dung tu anh)
a(f'<rect x="{CX-R-3}" y="{Y(TOP)}" width="{2*R+6}" height="{B}" stroke="#d00" stroke-width=".4" stroke-dasharray="2 1" fill="#d00" fill-opacity=".06"/>')
cy={"C1":0,"C2":14,"C3":42,"C4":B-12}
for n,v in zip(("C1","C2","C3","C4"),(C1,C2,C3,C4)):
    yy=Y(TOP+cy[n]); L(CX-R-3,yy,CX+R+3,yy,c="#06c",w=.3); T(CX+R+5,yy+1,f"{n}={v}",3,"start",c="#06c")
# kich thuoc
dimv(CX+R+30,Y(0),Y(A),f"A = {A}",3); L(CX+14,Y(0),CX+R+31,Y(0),w=.2); L(CX+R-4,Y(A),CX+R+31,Y(A),w=.2)
dimv(CX-R-8,Y(TOP),Y(TOP+B),f"B = D = {B}",-2); L(CX-R,Y(TOP),CX-R-9,Y(TOP),w=.2); L(CX-R,Y(TOP+B),CX-R-9,Y(TOP+B),w=.2)
dimv(CX-R-8,Y(TOP+B),Y(A),f"E = {E}",-2); L(CX-R+4,Y(A),CX-R-9,Y(A),w=.2)
dimv(CX-R-18,Y(0),Y(TOP),f"F = {TOP}",-2); L(CX-13.5,Y(0),CX-R-19,Y(0),w=.2); L(CX-R-3,Y(TOP),CX-R-19,Y(TOP),w=.2)
dimv(CX-R-28,Y(0),Y(21),"21",-2); L(CX-R-19,Y(21),CX-R-29,Y(21),w=.2); L(CX-R-19,Y(0),CX-R-29,Y(0),w=.2)
dimh(Y(-4),CX-14,CX+14,"Ø28 (F28_1810)"); dimh(Y(A+7),CX-R,CX+R,f"Ø{round(2*R)} (C2-C4)")
T(CX,Y(A+17),"MẶT TRƯỚC (1:1)",4,w="bold")
# ---- trai phang sleeve
LW=188; SEAM=7; LX,LY=150,Y(TOP)
T(LX+(LW+SEAM)/2,LY-18,"TRẢI PHẲNG SHRINK SLEEVE (1:1)",4,w="bold")
a(f'<rect x="{LX}" y="{LY}" width="{LW+SEAM}" height="{B}" stroke="#d00" stroke-width=".6"/>')
a(f'<rect x="{LX+LW}" y="{LY}" width="{SEAM}" height="{B}" fill="#d00" fill-opacity=".15" stroke="none"/>')
T(LX+LW+SEAM/2,LY+B/2,"mép dán",2.8,c="#a00")
a(f'<rect x="{LX+3}" y="{LY+3}" width="{LW-6}" height="{B-6}" stroke="#090" stroke-width=".3" stroke-dasharray="2 1"/>')
T(LX+LW/2,LY+B/2,"VÙNG IN AN TOÀN",3,c="#090")
for n,v in zip(("C1","C2","C3","C4"),(C1,C2,C3,C4)):
    yy=LY+cy[n]; L(LX,yy,LX+LW,yy,c="#06c",w=.3,d="3 1.5")
    T(LX+3,yy-1,f"{n} = {v}",3,"start",c="#06c")
    a(f'<rect x="{LX+(LW-v)/2:.1f}" y="{yy-.4}" width="{v}" height=".8" fill="#06c" stroke="none"/>')
dimh(LY+B+7,LX,LX+LW,f"{LW} (= chu vi C2-C4)"); dimh(LY+B+16,LX,LX+LW+SEAM,f"{LW+SEAM} (gồm mép dán {SEAM}, nhà in xác nhận)")
dimv(LX-7,LY,LY+B,f"{B}",-2)
T(LX+(LW+SEAM)/2,LY+B+30,"Mép trên (C1) bị co 175/188 = 93%; mép dưới tự do. Cần nhà in làm dieline + distortion grid.",3)
T(LX+(LW+SEAM)/2,LY+B+35,"Số đo thủ công, sai lệch nhỏ; F đo = 70 nhưng A-B-E = 61 (lệch 9 mm).",3)
# ---- khung ten
a('<rect x="5" y="240" width="410" height="52" stroke-width=".6"/>')
L(70,240,70,292,w=.4); L(260,240,260,292,w=.4); L(260,266,415,266,w=.4)
for x in (330,370): L(x,266,x,292,w=.4)
T(37,255,"Công Ty TNHH-SXTM",3.5,w="bold"); T(37,261,"Dịch Vụ Minh Thông",3.5,w="bold"); T(165,252,"Khách Hàng",4)
T(337,251,"Chai Pet",5,w="bold"); T(337,262,"350ml – CỔ F28_1810 – SLEEVE",4.5,w="bold")
T(300,273,"Vật liệu: PET",3.5); T(300,283,"Scale 1:1",3.5); T(345,283,"Gram: 16–20",3.5); T(392,283,"Trang 1",3.5)
T(165,272,"Theo số đo thủ công (phiếu đo). Hình dạng chi tiết là sơ lược.",3.2)
a('</svg>')
open("chai-350ml.svg","w").write("\n".join(o))
