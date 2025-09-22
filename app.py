import os, io, json
import numpy as np
from PIL import Image
from flask import Flask, request, jsonify, send_from_directory
import keras
from scripts.rule_engine import interpret

IMG_SIZE = 128
BASE = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE,"model")
WEB_DIR   = os.path.join(BASE,"web")

model = keras.models.load_model(os.path.join(MODEL_DIR,"model.h5"))
LABELS = [l.strip() for l in open(os.path.join(MODEL_DIR,"labels.txt"),"r",encoding="utf-8").read().splitlines() if l.strip()]
ATTR_CFG = json.load(open(os.path.join(MODEL_DIR,"attr_config.json"),"r",encoding="utf-8"))

app = Flask(__name__, static_folder=WEB_DIR, template_folder=WEB_DIR)

def preprocess(img: Image.Image):
    im = img.convert("L").resize((IMG_SIZE,IMG_SIZE))
    arr = np.asarray(im, dtype=np.float32)/255.0
    return arr.flatten()[None,:]

def argmax_and_name(arr, names):
    idx = int(np.argmax(arr)); return names[idx], float(arr[idx])

@app.route("/")
def index():
    return send_from_directory(WEB_DIR, "index.html")

@app.route("/<path:p>")
def static_files(p):
    return send_from_directory(WEB_DIR, p)

@app.route("/api/predict", methods=["POST"])
def api_predict():
    if "file" not in request.files or "line_type" not in request.form:
        return jsonify({"error":"file và line_type (life|heart|head|fate) là bắt buộc"}), 400
    line_type = request.form["line_type"].strip().lower()
    if line_type not in LABELS:
        return jsonify({"error":"line_type không hợp lệ"}), 400
    img = Image.open(io.BytesIO(request.files["file"].read()))
    X = preprocess(img)
    preds = model.predict(X, verbose=0)
    # unpack theo thứ tự outputs trong train_multihead.py
    pred = {
        "line_type": argmax_and_name(preds[0][0], ATTR_CFG["line_type"])[0],
        "length_cls": argmax_and_name(preds[1][0], ATTR_CFG["length_cls"])[0],
        "slope_cls":  argmax_and_name(preds[2][0], ATTR_CFG["slope_cls"])[0],
        "curv_cls":   argmax_and_name(preds[3][0], ATTR_CFG["curv_cls"])[0],
        "breaks_cls": argmax_and_name(preds[4][0], ATTR_CFG["breaks_cls"])[0],
    }
    # dùng line_type người dùng chọn để diễn giải (ưu tiên user choice)
    expl = interpret(line_type, pred)
    return jsonify({"attributes": pred, "line_type_input": line_type, "interpretation": expl})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
