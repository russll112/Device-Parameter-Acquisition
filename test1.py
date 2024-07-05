from paddleocr import PaddleOCR, draw_ocr
from paddle import *
import os
import cv2

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"



ocr = PaddleOCR(use_angle_cls=True, lang="ch")  # need to run only once to download and load model into memory
result = ocr.ocr('IMG_2314.jpg', cls=True)
ocr_result = {}

for idx in range(len(result)):
    res = result[idx]
    for line in res:
        print(line)

from PIL import Image

result = result[0]
image = Image.open('IMG_2314.jpg').convert('RGB')
boxes = [line[0] for line in result]
txts = [line[1][0] for line in result]
scores = [line[1][1] for line in result]
im_show = draw_ocr(image, boxes, font_path='doc/fonts/simfang.ttf')
im_show = Image.fromarray(im_show)
im_show.save('result.jpg')




