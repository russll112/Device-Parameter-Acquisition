import cv2 as cv
import numpy as np
# import matplotlib.pyplot as plt

def affine(image, label):
    # ----------------------------------------------------#
    #           读取图像
    # ----------------------------------------------------#
    # image_original = cv.imread('./test/IMG_2321.jpg')
    image_original = image
    H, W, _ = image_original.shape
    point1_x = round(float(label[1] * W), 1)
    point1_y = round(float(label[2] * H), 1)
    point2_x = round(float(label[3] * W), 1)
    point2_y = round(float(label[4] * H), 1)
    point3_x = round(float(label[5] * W), 1)
    point3_y = round(float(label[6] * H), 1)
    point4_x = round(float(label[7] * W), 1)
    point4_y = round(float(label[8] * H), 1)

    points1 = np.float32([[point1_x, point1_y], [point2_x, point2_y], [point3_x, point3_y], [point4_x, point4_y]])
    points2 = np.float32([[0, 0], [1600, 0], [1600, 1080], [0, 1080]])

    mat_perspective = cv.getPerspectiveTransform(points1, points2)
    image_perspective = cv.warpPerspective(image_original, mat_perspective,
                                           (image_original.shape[1], image_original.shape[0]))

    cut_image_persepective = image_perspective[0:1080, 0:1600]
    # cv.imwrite('cut_image_persepective.png', cut_image_persepective)

    # cv.imshow("image_perspective", cut_image_persepective)
    # cv.waitKey(0)
    return cut_image_persepective
    # cv.destroyAllWindows()




