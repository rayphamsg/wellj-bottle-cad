# Chai PET 350ml (ban ve chinh thuc sbv0282) + dieline shrink sleeve phu than+vai (PA C). mm, A3, 1:1
import math
H,RB,RN,NECK_H,SH_TOP,BODY_TOP = 175,31.5,13.9,21,28,67   # cao, r than, r co, cao co, vai bat dau, than bat dau (175-19.5-88.5)
S_TOP,S_BOT = 46,173            # mep tren/duoi sleeve tinh tu mieng (cao ~127, mep tren ~ O55)
SEAM,WF = 6,206                 # mep dan, chu vi film (max 200.1 x ~1.03)
Hs=S_BOT-S_TOP
b=(BODY_TOP-SH_TOP)/math.sqrt(1-(RN/RB)**2)
def rad(y):                      # ban kinh tai do sau y (tu mieng)
    if y>=BODY_TOP: return RB
    return RB*math.sqrt(max(0,1-((BODY_TOP-y)/b)**2))
CX,Y0=72,30; Y=lambda y:Y0+y
o=[];a=o.append
def L(x1,y1,x2,y2,c="#000",w=.3,d=""):
    a(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{c}" stroke-width="{w}"'+(f' stroke-dasharray="{d}"' if d else '')+'/>')
def T(x,y,s,sz=3.4,anc="middle",w="normal",c="#000"):
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
# profile phai
R=[(RN,0),(RN,19),(16.5,21),(16.5,23.5),(RN+.6,24.5),(RN+.6,SH_TOP)]
n=30
for i in range(1,n+1):
    y=SH_TOP+(BODY_TOP-SH_TOP)*i/n; R.append((rad(y),y))
R+= [(RB,H-8),(RB-.3,H-4),(RB-2,H-1),(RB-4,H)]
pts=[(CX+x,Y(y)) for x,y in R]+[(CX-x,Y(y)) for x,y in reversed(R)]
a('<path d="M '+" L ".join(f"{x:.2f},{y:.2f}" for x,y in pts)+' Z" stroke-width=".8" fill="#eef4f8"/>')
for y in (3,6.5,10,13.5): L(CX-RN,Y(y),CX+RN,Y(y),w=.25)
L(CX-RB,Y(BODY_TOP),CX+RB,Y(BODY_TOP),w=.25,d="1.5 1"); L(CX-RB,Y(H-19.5),CX+RB,Y(H-19.5),w=.25,d="1.5 1")
L(CX,Y(-6),CX,Y(H+4),w=.2,d="6 1 1 1")
# vung sleeve
a(f'<rect x="{CX-RB-3}" y="{Y(S_TOP)}" width="{2*RB+6}" height="{Hs}" stroke="#d00" stroke-width=".4" stroke-dasharray="2 1" fill="#d00" fill-opacity=".07"/>')
lv=[(S_TOP,"mép trên"),(BODY_TOP,"đầu thân"),(S_BOT,"mép dưới")]
for y,_ in lv:
    r=rad(y); L(CX-r,Y(y),CX+r,Y(y),c="#06c",w=.35)
# dimensions
dimv(CX+RB+16,Y(0),Y(H),"175 ±1",3); L(CX+RN,Y(0),CX+RB+17,Y(0),w=.2); L(CX+RB-4,Y(H),CX+RB+17,Y(H),w=.2)
dimv(CX-RB-8,Y(BODY_TOP),Y(H-19.5),"88.5 ±1",-2); L(CX-RB,Y(BODY_TOP),CX-RB-9,Y(BODY_TOP),w=.2); L(CX-RB,Y(H-19.5),CX-RB-9,Y(H-19.5),w=.2)
dimv(CX-RB-8,Y(H-19.5),Y(H),"19.5 ±1",-2); L(CX-RB+4,Y(H),CX-RB-9,Y(H),w=.2)
dimv(CX-RB-18,Y(0),Y(21),"21",-2); L(CX-RN,Y(0),CX-RB-19,Y(0),w=.2); L(CX-16.5,Y(21),CX-RB-19,Y(21),w=.2)
dimv(CX-RB-28,Y(S_TOP),Y(S_BOT),f"Sleeve {Hs}",-2); L(CX-RB-3,Y(S_TOP),CX-RB-29,Y(S_TOP),w=.2); L(CX-RB-3,Y(S_BOT),CX-RB-29,Y(S_BOT),w=.2)
dimh(Y(-4),CX-13.9,CX+13.9,"Ø27.8"); dimh(Y(H+7),CX-RB,CX+RB,"Ø63 ±0.7")
T(CX,Y(H+17),"MẶT TRƯỚC (1:1)",4,w="bold")
# dieline
LX,LY=150,Y(S_TOP)-24
T(LX+WF/2,LY-14,"DIELINE SHRINK SLEEVE – PHỦ THÂN + VAI (1:1)",4,w="bold")
a(f'<rect x="{LX}" y="{LY}" width="{WF}" height="{Hs}" stroke="#d00" stroke-width=".6"/>')
a(f'<rect x="{LX+WF-SEAM}" y="{LY}" width="{SEAM}" height="{Hs}" fill="#d00" fill-opacity=".15" stroke="none"/>'); T(LX+WF-SEAM/2,LY+Hs/2,"dán",2.6,c="#a00")
# vung chai that (chu vi theo do cao) ve doi xung
cx=LX+(WF-SEAM)/2
poly=[]
for i in range(0,41):
    y=S_TOP+Hs*i/40; poly.append((2*math.pi*rad(y),LY+(y-S_TOP)))
a('<path d="M '+" L ".join(f"{cx-w/2:.1f},{yy:.1f}" for w,yy in poly)+" L "+" L ".join(f"{cx+w/2:.1f},{yy:.1f}" for w,yy in reversed(poly))+' Z" fill="#06c" fill-opacity=".08" stroke="#06c" stroke-width=".3" stroke-dasharray="2 1"/>')
rows=[]
for y,nm in lv:
    c=2*math.pi*rad(y); yy=LY+(y-S_TOP); sh=(1-c/WF)*100
    L(LX,yy,LX+WF,yy,c="#06c",w=.3,d="3 1.5")
    rows.append((y,2*rad(y),c,sh)); T(LX+2,yy-1,f"h={H-y:.0f}: Ø{2*rad(y):.0f}, C={c:.0f}, co {sh:.0f}%",2.9,"start",c="#06c")
dimh(LY+Hs+7,LX,LX+WF,f"{WF} (chu vi film = 200 × 1.03; gồm mép dán {SEAM})"); dimv(LX-7,LY,LY+Hs,f"{Hs}",-2)
T(LX+WF/2,LY+Hs+17,"Vùng xanh = bề mặt chai thật (chu vi theo độ cao); mép trên cần giãn hình ngang ×206/173 để sau khi co hiển thị đúng.",3)
T(LX+WF/2,LY+Hs+22,"h = chiều cao tính từ đáy. Tỉ lệ co, vị trí đường hàn, lưới méo cuối cùng do nhà in màng co chốt.",3)
# khung ten
a('<rect x="5" y="240" width="410" height="52" stroke-width=".6"/>')
L(70,240,70,292,w=.4); L(260,240,260,292,w=.4); L(260,266,415,266,w=.4)
for x in (330,370): L(x,266,x,292,w=.4)
T(37,255,"Công Ty TNHH-SXTM",3.5,w="bold"); T(37,261,"Dịch Vụ Minh Thông",3.5,w="bold"); T(165,252,"Khách Hàng",4)
T(337,251,"Chai Pet",5,w="bold"); T(337,262,"350ml – SLEEVE PA.C (sbv 0282)",4.3,w="bold")
T(300,273,"Vật liệu: PET",3.5); T(300,283,"Scale 1:1",3.5); T(345,283,"Gram: 16–20",3.5); T(392,283,"Trang 1",3.5)
T(165,272,"Số liệu theo bản vẽ chính thức sbv0282. Hình dạng vai là mô hình gần đúng.",3.2)
a('</svg>'); open("chai-350ml.svg","w").write("\n".join(o))
for r in rows: print(r)
