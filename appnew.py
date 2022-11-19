import os
import urllib.request
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename

import cv2
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog, DatasetCatalog
import sys
import os

# path = "airports/"

cfg = get_cfg()

cfg.merge_from_file(model_zoo.get_config_file("COCO-Detection/faster_rcnn_R_50_FPN_1x.yaml"))
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5  # set threshold for this model
cfg.MODEL.ROI_HEADS.NUM_CLASSES = 3
cfg.MODEL.WEIGHTS = 'model_0023999.pth'
cfg.MODEL.DEVICE = 'cpu'

predictor = DefaultPredictor(cfg)

UPLOAD_FOLDER = 'static/uploads/'

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['POST','GET'])
def upload_image():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No image selected for uploading')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # print('upload_image filename: ' + filename)
            output_images = []
            im = cv2.imread(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            h, w = im.shape[:2]
            nb_r, nb_c = 3, 3

            new_h = h if h % nb_r == 0 else h - (h % nb_r)
            new_w = w if w % nb_c == 0 else w - (w % nb_c)

            im = cv2.resize(im, (new_w, new_h))
            cnt = 0
            for a in range(0, new_h, new_h // nb_r):
                for b in range(0, new_w, new_w // nb_c):
                    cnt += 1
                    cell = im[a: a + (new_h // nb_r), b: b + (new_w // nb_c), :]
                    outputs = predictor(cell)

                    for i in range(len(outputs["instances"])):
                        box = outputs["instances"].get('pred_boxes')[i].tensor[0]

                        x, y = int(box[0]), int(box[1])
                        x_end, y_end = int(box[2]), int(box[3])
                        conf = outputs["instances"].get('scores')[i]
                        class_id = int(outputs["instances"].get('pred_classes')[i])

                        cv2.rectangle(cell, (x, y), (x_end, y_end), (255, 0, 0), 2)
                        cv2.putText(cell, f"class {class_id}: {conf:.2f}", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                    op = f'static/output/{filename.split(".")[0]}_{cnt}_out.jpg'
                    cv2.imwrite(op, cell)
                    print(op)
                    output_images.append(op)
            flash('Image successfully uploaded and displayed below')
            return render_template('upload.html', filename=filename, output_images=output_images)
        else:
            flash('Allowed image types are -> png, jpg, jpeg, gif')
            return redirect(request.url)
    else:
        return render_template('upload.html')


@app.route('/display/<filename>')
def display_image(filename):
    # print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5003", debug=True)
