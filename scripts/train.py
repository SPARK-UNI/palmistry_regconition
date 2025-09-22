import os, glob, csv, json, random
import numpy as np
from PIL import Image
import keras
from keras import layers
import tensorflow as tf

TF_ENABLE_ONEDNN_OPTS=0
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    try:
        # tránh chiếm full VRAM
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        tf.config.set_visible_devices(gpus[0], 'GPU')  # chọn GPU:0
        # Tùy chọn: mixed precision để nhanh hơn (nếu GPU hỗ trợ Tensor Cores)
        from keras import mixed_precision
        mixed_precision.set_global_policy('mixed_float16')
        print("[GPU] Using:", gpus[0])
    except Exception as e:
        print("[GPU] Could not enable GPU properly:", e)

# ====== CẤU HÌNH MẶC ĐỊNH ======
DATA_ROOT = "data/processed"     # nơi converter đã sinh crops + attrs_*.csv
OUT_DIR   = "model"              # nơi lưu model và config
IMG_SIZE  = 128
EPOCHS    = 30
BATCH     = 32
CLS_NAMES = ["life","heart","head","fate"]  # nhãn đường

# Ngưỡng bucket mặc định cho các thuộc tính (có thể chỉnh)
LEN_THRESH  = (0.45, 0.70)       # length_norm: <0.45 short; 0.45-0.70 medium; >0.70 long
SLOPE_THR   = (-10.0, 10.0)      # slope_deg: < -10 down; -10..10 flat; >10 up
CURV_THR    = (8.0, 20.0)        # curv_deg: <8 low; 8..20 med; >20 high

SEED = 42
random.seed(SEED); np.random.seed(SEED); tf.random.set_seed(SEED)

def _bucket_length(x: float) -> int:
    a, b = LEN_THRESH
    return 0 if x < a else (1 if x < b else 2)

def _bucket_slope(x: float) -> int:
    a, b = SLOPE_THR
    return 0 if x < a else (1 if x <= b else 2)

def _bucket_curv(x: float) -> int:
    a, b = CURV_THR
    return 0 if x < a else (1 if x <= b else 2)

def _bucket_breaks(n: int) -> int:
    return 0 if n == 0 else (1 if n == 1 else 2)

def load_images_and_attrs(split_name: str):
    """Đọc ảnh ROI + thuộc tính từ CSV attrs_split.csv"""
    split_dir = os.path.join(DATA_ROOT, split_name)
    csv_path  = os.path.join(DATA_ROOT, f"attrs_{split_name}.csv")
    if not (os.path.isdir(split_dir) and os.path.exists(csv_path)):
        return (np.array([]),) * 6  # X, y_line, y_len, y_slope, y_curv, y_breaks rỗng

    # Map crop_path -> row
    attrs = {}
    with open(csv_path, "r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            # chuẩn hoá path để khớp hệ điều hành
            p = os.path.normpath(row["crop_path"])
            attrs[p] = row

    X=[]; y_line=[]; y_len=[]; y_slope=[]; y_curv=[]; y_breaks=[]
    for lbl in CLS_NAMES:
        for fp in glob.glob(os.path.join(split_dir, lbl, "*")):
            key = os.path.normpath(fp)
            if key not in attrs:
                # Bỏ qua nếu CSV không có record—an toàn.
                continue
            # ảnh → xám → resize → [0,1] → flatten
            im = Image.open(fp).convert("L").resize((IMG_SIZE, IMG_SIZE))
            arr = np.asarray(im, dtype=np.float32)/255.0
            X.append(arr.flatten())

            row = attrs[key]
            # loại đường (phòng trường hợp folder sai label -> dùng CSV)
            lt = row.get("label", lbl).strip().lower()
            y_line.append(CLS_NAMES.index(lt))

            # bucket thuộc tính
            y_len.append(_bucket_length(float(row["length_norm"])))
            y_slope.append(_bucket_slope(float(row["slope_deg"])))
            y_curv.append(_bucket_curv(float(row["curv_deg"])))
            y_breaks.append(_bucket_breaks(int(row["breaks"])))

    return (np.array(X),
            np.array(y_line), np.array(y_len), np.array(y_slope),
            np.array(y_curv), np.array(y_breaks))

def build_model():
    inp = keras.Input(shape=(IMG_SIZE*IMG_SIZE,), name="pixels")
    # ANN thuần Dense-only:
    x = layers.Dense(1024, activation="relu")(inp)
    x = layers.Dense(512, activation="relu")(x)
    x = layers.Dense(256, activation="relu")(x)
    # 5 đầu ra (multi-head)
    line_type  = layers.Dense(4, activation="softmax", name="line_type")(x)
    length_cls = layers.Dense(3, activation="softmax", name="length_cls")(x)
    slope_cls  = layers.Dense(3, activation="softmax", name="slope_cls")(x)
    curv_cls   = layers.Dense(3, activation="softmax", name="curv_cls")(x)
    breaks_cls = layers.Dense(3, activation="softmax", name="breaks_cls")(x)

    model = keras.Model(inp, [line_type, length_cls, slope_cls, curv_cls, breaks_cls])
    model.compile(
        optimizer=keras.optimizers.Adam(1e-3),
        loss={
            "line_type":  "sparse_categorical_crossentropy",
            "length_cls": "sparse_categorical_crossentropy",
            "slope_cls":  "sparse_categorical_crossentropy",
            "curv_cls":   "sparse_categorical_crossentropy",
            "breaks_cls": "sparse_categorical_crossentropy",
        },
        metrics={k: "accuracy" for k in ["line_type","length_cls","slope_cls","curv_cls","breaks_cls"]}
    )
    return model

def main():
    print("==> Loading data from", DATA_ROOT)
    Xtr, ylt_tr, ylen_tr, ys_tr, yc_tr, yb_tr = load_images_and_attrs("train")
    Xval, ylt_val, ylen_val, ys_val, yc_val, yb_val = load_images_and_attrs("val")
    Xte,  ylt_te,  ylen_te,  ys_te,  yc_te,  yb_te  = load_images_and_attrs("test")

    if Xtr.size == 0:
        raise RuntimeError(f"Không tìm thấy dữ liệu train trong {DATA_ROOT}. Hãy chạy scripts/polylines_to_crops_attrs.py trước.")

    model = build_model()
    model.summary()

    callbacks=[]
    if Xval.size>0:
        callbacks = [
            keras.callbacks.ReduceLROnPlateau(monitor="val_line_type_accuracy", factor=0.5, patience=3, verbose=1),
            keras.callbacks.EarlyStopping(monitor="val_line_type_accuracy", patience=6, restore_best_weights=True, verbose=1)
        ]

    print("==> Training ...")
    model.fit(
        Xtr, {"line_type": ylt_tr, "length_cls": ylen_tr, "slope_cls": ys_tr, "curv_cls": yc_tr, "breaks_cls": yb_tr},
        validation_data=(Xval, {"line_type": ylt_val, "length_cls": ylen_val, "slope_cls": ys_val, "curv_cls": yc_val, "breaks_cls": yb_val}) if Xval.size>0 else None,
        epochs=EPOCHS, batch_size=BATCH, callbacks=callbacks, verbose=2
    )

    if Xte.size>0:
        print("==> Evaluating on test ...")
        metrics = model.evaluate(
            Xte, {"line_type": ylt_te, "length_cls": ylen_te, "slope_cls": ys_te, "curv_cls": yc_te, "breaks_cls": yb_te},
            verbose=0
        )
        print("Test metrics:", metrics)

    os.makedirs(OUT_DIR, exist_ok=True)
    model.save(os.path.join(OUT_DIR, "model.h5"))
    with open(os.path.join(OUT_DIR, "labels.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(CLS_NAMES))

    # ghi cấu hình buckets để app.py hiểu
    attr_cfg = {
        "line_type":  CLS_NAMES,
        "length_cls": ["short","medium","long"],
        "slope_cls":  ["down","flat","up"],
        "curv_cls":   ["low","medium","high"],
        "breaks_cls": ["none","one","many"],
        "thresholds": {
            "length_norm": LEN_THRESH,
            "slope_deg":   SLOPE_THR,
            "curv_deg":    CURV_THR
        }
    }
    with open(os.path.join(OUT_DIR, "attr_config.json"), "w", encoding="utf-8") as f:
        json.dump(attr_cfg, f, ensure_ascii=False, indent=2)

    print(f"==> Saved to {OUT_DIR}/model.h5, {OUT_DIR}/labels.txt, {OUT_DIR}/attr_config.json")

if __name__ == "__main__":
    main()
