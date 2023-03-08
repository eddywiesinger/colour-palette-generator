import os
import time

from dotenv import load_dotenv
from flask import Flask, render_template, url_for, request
from flask_bootstrap import Bootstrap4
from werkzeug.utils import secure_filename
from PIL import Image
import numpy as np

load_dotenv()

IMAGES_PATH = './static/images'

application = Flask(__name__, static_folder='static')
application.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
application.config['UPLOAD_FOLDER'] = IMAGES_PATH

Bootstrap4(application)

DEFAULT_FILE = 'sample.jpg'
DEFAULT_NUM_COLORS = 10
DEFAULT_DELTA = 24

last_path = None


def rgb_to_hex(r, g, b):
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)


@application.route('/', methods=['GET', 'POST'])
def home():
    global last_path
    if request.method == 'POST':
        file = request.files.get('image', os.path.join(IMAGES_PATH, DEFAULT_FILE))
        if file.filename:
            new_path = os.path.join(IMAGES_PATH, secure_filename(file.filename))
            file.save(new_path)
            last_path = new_path
        else:
            file = last_path
        num_colours = request.form.get('num_colours', DEFAULT_NUM_COLORS, type=int)
        delta = request.form.get('delta', DEFAULT_DELTA, type=int)
    else:
        file = os.path.join(IMAGES_PATH, DEFAULT_FILE)
        last_path = file
        num_colours = DEFAULT_NUM_COLORS
        delta = DEFAULT_DELTA

    ticks = round((255 / delta)) + 1
    cat = {}
    cats = np.rint(np.linspace(0, 255, ticks))
    cats = [int(n) for n in cats]
    print(cats)

    img = Image.open(file)
    img_array = np.array(img)
    print(f"Image shape: {img_array.shape},Total pixels: {img_array.shape[0] * img_array.shape[1]}")

    start_time = time.time()

    for rows in img_array:
        for rgb in rows:
            idx_rgb_dec = np.rint((ticks - 1) * (rgb / 255))
            idx_rgb = (int(idx_rgb_dec[0]), int(idx_rgb_dec[1]), int(idx_rgb_dec[2]))
            try:
                cat[idx_rgb] += 1
            except KeyError:
                cat[idx_rgb] = 1
    sorted_cat = sorted(cat.items(), key=lambda x: x[1])
    highest_colour_counts = reversed(sorted_cat[-num_colours:])
    highest_colours = []
    for idx_vec, cnt in highest_colour_counts:
        r_idx, g_idx, b_idx = idx_vec
        red = cats[r_idx]
        green = cats[g_idx]
        blue = cats[b_idx]
        rgb_tuple = (red, green, blue)
        c_hex = rgb_to_hex(red, green, blue)
        highest_colours.append([rgb_tuple, c_hex, cnt])

    end_time = time.time()

    print(f"Duration: {round(end_time - start_time, 2)}s")

    try:
        img_path = os.path.join(IMAGES_PATH, file.filename)
    except:
        img_path = file
    return render_template('index.html',
                           img_path=img_path,
                           image=file,
                           highest_colour_counts=highest_colours,
                           num_colours=num_colours,
                           delta=delta,
                           total_bins=sum(cat.values()))


if __name__ == "__main__":
    application.run(host='127.0.0.1', port=5000)
