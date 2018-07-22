import os

import cv2 as cv
import numpy as np
from tqdm import tqdm
import json
from config import img_size, image_folder, scale
from model import build_model
from utils import random_crop, preprocess_input, psnr

if __name__ == '__main__':
    model_weights_path = 'models/model.16-9.0500.hdf5'
    model = build_model()
    model.load_weights(model_weights_path)

    names_file = 'valid_names.txt'
    with open(names_file, 'r') as f:
        names = f.read().splitlines()

    if os.path.isfile('data/eval.json'):
        with open('data/eval.json') as file:
            eval = json.load(file)
    else:
        eval = {}

    h, w = img_size * scale, img_size * scale

    psnr_list = []

    for i in tqdm(range(names)):
        name = names[i]
        filename = os.path.join(image_folder, name)
        image_bgr = cv.imread(filename)
        gt = random_crop(image_bgr)

        x = cv.resize(gt, (img_size, img_size), cv.INTER_CUBIC)
        image = cv.resize(x, (h, w), cv.INTER_CUBIC)

        x = preprocess_input(x.astype(np.float32))
        x_test = np.empty((1, img_size, img_size, 3), dtype=np.float32)
        x_test[0] = x
        out = model.predict(x_test)
        out = out.reshape((h, w, 3))
        out = np.clip(out, 0.0, 255.0)
        out = out.astype(np.uint8)

        psnr_list.append(psnr(out, gt))

    print('num_valid_samples: ' + str(len(names)))
    print('PSNR(avg): {0:.5f}'.format(np.mean(psnr_list)))

    eval['psnr_list'] = psnr_list
    with open('data/eval.json', 'w') as file:
        json.dump(eval, file)