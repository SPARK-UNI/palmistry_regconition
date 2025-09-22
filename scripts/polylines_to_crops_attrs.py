import os, json, math, csv
from PIL import Image

IMG_SIZE = 128
CLASSES = ["life","heart","head","fate"]

# --- đường dẫn gốc ---
RAW_ROOT = "data/raw"
OUT_ROOT = "data/processed"

SPLITS = ["train", "valid", "test"]  # bỏ "test" nếu bạn chưa có

def bbox_from_points(pts, W, H, pad=0.15):
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    x1, y1, x2, y2 = min(xs), min(ys), max(xs), max(ys)
    pw = (x2-x1)*pad; ph = (y2-y1)*pad
    x1 = max(0, x1-pw); y1 = max(0, y1-ph)
    x2 = min(W, x2+pw); y2 = min(H, y2+ph)
    return int(x1), int(y1), int(x2), int(y2)

def poly_length(pts):
    s=0.0
    for i in range(1,len(pts)):
        dx=pts[i][0]-pts[i-1][0]; dy=pts[i][1]-pts[i-1][1]
        s += (dx*dx+dy*dy)**0.5
    return s

def avg_slope_deg(pts):
    if len(pts)<2: return 0.0
    angs=[]
    for i in range(1,len(pts)):
        dx=pts[i][0]-pts[i-1][0]; dy=pts[i][1]-pts[i-1][1]
        if dx==0 and dy==0: continue
        angs.append(math.degrees(math.atan2(dy, dx)))
    return sum(angs)/len(angs) if angs else 0.0

def avg_curvature_deg(pts):
    if len(pts)<3: return 0.0
    curvs=[]
    for i in range(1,len(pts)-1):
        ax,ay=pts[i-1]; bx,by=pts[i]; cx,cy=pts[i+1]
        v1x,v1y=bx-ax, by-ay; v2x,v2y=cx-bx, cy-by
        n1=(v1x*v1x+v1y*v1y)**0.5; n2=(v2x*v2x+v2y*v2y)**0.5
        if n1==0 or n2==0: continue
        cosang=(v1x*v2x+v1y*v2y)/(n1*n2)
        cosang=max(-1.0,min(1.0,cosang))
        curvs.append(math.degrees(math.acos(cosang)))
    return sum(curvs)/len(curvs) if curvs else 0.0

def process_split(split):
    raw_split = os.path.join(RAW_ROOT, split)
    out_split = os.path.join(OUT_ROOT, split)
    os.makedirs(out_split, exist_ok=True)
    for c in CLASSES: os.makedirs(os.path.join(out_split,c), exist_ok=True)

    coco_json = os.path.join(raw_split, "_annotations.coco.json")
    if not os.path.exists(coco_json):
        print(f"[!] Bỏ qua {split} vì không có {coco_json}")
        return

    coco=json.load(open(coco_json,"r",encoding="utf-8"))
    id2file={im["id"]:im["file_name"] for im in coco["images"]}
    id2size={im["id"]:(im["width"],im["height"]) for im in coco["images"]}
    id2cat ={c["id"]:c["name"].lower() for c in coco["categories"]}

    # đếm breaks theo (image_id, label)
    counts={}
    for ann in coco["annotations"]:
        lab=id2cat[ann["category_id"]]
        if lab not in CLASSES: continue
        key=(ann["image_id"], lab)
        counts[key]=counts.get(key,0)+1

    csv_path=os.path.join(OUT_ROOT, f"attrs_{split}.csv")
    with open(csv_path,"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=["crop_path","label","length_norm","slope_deg","curv_deg","breaks"])
        w.writeheader()

        for ann in coco["annotations"]:
            lab=id2cat[ann["category_id"]]
            if lab not in CLASSES: continue
            W,H=id2size[ann["image_id"]]
            img_path=os.path.join(raw_split,id2file[ann["image_id"]])
            if not os.path.exists(img_path): continue

            seg=ann.get("segmentation",[])
            if isinstance(seg,list) and len(seg)>0 and isinstance(seg[0],list):
                seg=seg[0]
            pts=list(zip(seg[0::2],seg[1::2])) if seg else []
            if not pts:
                x,y,wid,hei=ann["bbox"]; pts=[(x,y),(x+wid,y+hei)]
            x1,y1,x2,y2=bbox_from_points(pts,W,H)
            im=Image.open(img_path).convert("L")
            crop=im.crop((x1,y1,x2,y2)).resize((IMG_SIZE,IMG_SIZE))
            out_path=os.path.join(out_split,lab,f"{ann['image_id']}_{ann['id']}.jpg")
            crop.save(out_path,quality=95)

            L=poly_length(pts)
            length_norm=L/max(W,H)
            slope=avg_slope_deg(pts)
            curv=avg_curvature_deg(pts)
            brk=counts.get((ann["image_id"],lab),1)-1

            w.writerow({
                "crop_path": out_path.replace("\\","/"),
                "label": lab,
                "length_norm": round(length_norm,4),
                "slope_deg": round(slope,2),
                "curv_deg": round(curv,2),
                "breaks": brk
            })
    print(f"[OK] {split}: {csv_path}, crops tại {out_split}")

if __name__=="__main__":
    for s in SPLITS:
        process_split(s)
