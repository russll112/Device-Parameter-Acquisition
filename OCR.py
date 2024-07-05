from paddleocr import PaddleOCR, draw_ocr
from paddle import *
import os
import cv2

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"


def ocr_recognize(img_path):
    ocr = PaddleOCR(use_angle_cls=True, lang="ch")  # need to run only once to download and load model into memory
    result = ocr.ocr(img_path, cls=True)
    ocr_result = {}

    for idx in range(len(result)):
        res = result[idx]
        for line in res:
            print(line)

    from PIL import Image

    result = result[0]
    image = Image.open(img_path).convert('RGB')
    boxes = [line[0] for line in result]
    txts = [line[1][0] for line in result]
    scores = [line[1][1] for line in result]
    im_show = draw_ocr(image, boxes, font_path='doc/fonts/simfang.ttf')
    im_show = Image.fromarray(im_show)
    im_show.save('result.jpg')
    im_show = draw_ocr(image, boxes, txts, scores, font_path='doc/fonts/simfang.ttf')
    im_show = Image.fromarray(im_show)
    im_show.save('txt.jpg')

    # 将识别结果转换为字典
    for i, txt in enumerate(txts):
        ocr_result[f"text_{i}"] = txt

    return ocr_result
