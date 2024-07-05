import cv2
import numpy as np

img = cv2.imread('./test/IMG_2321.jpg')
# start = time.time()
new_size = (1600, 1080)
img = cv2.resize(img, new_size)
hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
# RGB转HSV
mask = np.zeros(hsv_img.shape[:2], dtype=np.uint8)
mask[(hsv_img[:, :, 0] >= 100) & (hsv_img[:, :, 0] <= 200) & (hsv_img[:, :, 1] >= 0) &
     (hsv_img[:, :, 1] <= 200) & (hsv_img[:, :, 2] >= 0) & (hsv_img[:, :, 2] <= 100)] = 1
result = cv2.bitwise_and(img, img, mask=mask)
# 灰度处理
gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)

# 高斯滤波
blur = cv2.GaussianBlur(gray, (3, 3), 0)

# 边缘检测
# 转灰度，做单通道计算比较节省时间
edges = cv2.Canny(blur, 38, 128, apertureSize=3)
cv2.imshow("edges", edges)
cv2.waitKey(0)

# 所有轮廓的列表contours和分层信息
contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
print("轮廓数量：", len(contours))
# print(hierarchy)

img_copy = img.copy()  # 复制原图，避免在原图上直接画框

area_max = 0  # 查找最大切片
cnt_max = 0
for cnt in contours:
    x, y, w, h = cv2.boundingRect(cnt)  # 获取轮廓的边界矩形
    area = w * h
    if area > area_max:
        area_max = area
        cnt_max = cnt

# 画出最小矩形框架
x, y, w, h = cv2.boundingRect(cnt_max)
cv2.rectangle(img_copy, (x, y), (x + w, y + h), (0, 255, 0), 1)  # 绿

# 获取最小外接矩阵，中心点坐标，宽高，旋转角度
rect = cv2.minAreaRect(cnt_max)
# 旋转角度为rect[2]，获取旋转角度
center = np.intp(rect[0])
width = np.intp(rect[1][0])
height = np.intp(rect[1][1])
angle = np.intp(rect[2])

# 获取矩形四个顶点，浮点型
box = cv2.boxPoints(rect)
# 取整
box = np.intp(box)
cv2.drawContours(img_copy, [box], 0, (0, 0, 255), 1)  # 红

area = w * h
print("xywh", x, y, w, h)
print("矩形面积：", area)

cv2.imshow("result", img_copy)
cv2.waitKey(0)
cut_image_green = img_copy[y:y + h, x:x + w]
# 切出绿色矩形
# cv2.imshow("cut_image_green", cut_image_green)
# cv2.waitKey(0)
cv2.imwrite('cut_image_green.jpg', cut_image_green)


# 计算旋转前矩形左上顶点坐标
def left_up(box):
    top_point_y = np.min(box[:, 1])
    top_point_x = box[:, 0][np.where(box[:, 1] == top_point_y)][0]
    top_point = [top_point_x, top_point_y]
    return top_point


# 计算旋转后矩形左上顶点坐标(中心点位置不变)
def calculate_left_up(top_point):
    c = (center[0] ** 2 + center[1] ** 2) ** 0.5
    b = ((top_point[0] - center[0]) ** 2 + (top_point[1] - center[1]) ** 2) ** 0.5
    d = c - b
    x = d * (center[0] / c)
    y = d * (center[1] / c)
    top_point_rotate = [x, y]
    return top_point_rotate


# 这里的第一个参数为旋转中心，第二个为旋转角度，第三个为旋转后的缩放因子
# 可以通过设置旋转中心，缩放因子，以及窗口大小来防止旋转后超出边界的问题
# getRotationMatrix2D函数，接收3x3矩阵
rows, cols = img_copy.shape[:2]
print(rows, cols)
M = cv2.getRotationMatrix2D((int(center[0]), int(center[1])), 270 + angle, 1)  # 转正(以矩形中心为旋转中心)
rotate_red = cv2.warpAffine(img_copy, M, (1600, 1080))

# 计算旋转后左上顶点的坐标
top_point = left_up(box)
print(top_point)
# 标出旋转前的点
cv2.circle(img_copy, (int(top_point[0]), int(top_point[1])), 0, (0, 255, 255), 6)
cv2.imshow("top_point_show", img_copy)
cv2.waitKey(0)
top_point_rotate = calculate_left_up(top_point)
print(top_point_rotate)
# 标出旋转后的点
cv2.circle(rotate_red, (int(top_point_rotate[0]), int(top_point_rotate[1])), 0, (0, 255, 255), 6)
cv2.imshow("rotate_red", rotate_red)
cv2.waitKey(0)
# cut_image_red = img_copy[0, [box]]
# #切出红色矩形
# cv2.imshow("cut_image_red", cut_image_red)
# cv2.waitKey(0)
# cv2.imwrite('cut_image_red.png', cut_image_red)
print("111")
