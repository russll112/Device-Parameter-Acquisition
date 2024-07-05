import os
import glob
import argparse
import xml.etree.ElementTree as ET
import json

address = './mydata/labels/train_json/IMG_'
output_dir = './mydata/labels/train/IMG_'
# i = 100
for i in range(2100, 2400):
    address_i = address + str(i) + '.json'
    # print(address_i)
    try:
        with open(address_i, 'r', encoding='utf-8') as file:
            # 使用json.load()方法解析JSON数据
            data = json.load(file)

            # print(data['shapes'], data['imageHeight'], data['imageWidth'])
            point = data['shapes'][0]
            width = data['imageWidth']
            height = data['imageHeight']
            print(point)
            x1 = point['points'][0][0]
            y1 = point['points'][0][1]
            x2 = point['points'][1][0]
            y2 = point['points'][1][1]
            x3 = point['points'][2][0]
            y3 = point['points'][2][1]
            x4 = point['points'][3][0]
            y4 = point['points'][3][1]
            # print(x1,y1,x2,y2,x3,y3,x4,y4)
            # YOLO数据集标注为逆时针
            yolo_x1 = round(float(x4 / width), 6)
            yolo_y1 = round(float(y4 / height), 6)
            yolo_x2 = round(float(x3 / width), 6)
            yolo_y2 = round(float(y3 / height), 6)
            yolo_x3 = round(float(x2 / width), 6)
            yolo_y3 = round(float(y2 / height), 6)
            yolo_x4 = round(float(x1 / width), 6)
            yolo_y4 = round(float(y1 / height), 6)
            f = open(output_dir + str(i) + '.txt', 'x')
            f.write(f'{0} {yolo_x1:.6f} {yolo_y1:.6f} {yolo_x2:.6f} {yolo_y2:.6f}'
                    f' {yolo_x3:.6f} {yolo_y3:.6f} {yolo_x4:.6f} {yolo_y4:.6f} \n')
            print(address_i)

            f1 = open('./mydata/train.txt', 'a')
            print(1)
            f1.write(f'data/UCAS50/images/train/IMG_'+str(i)+'.jpg'+'\n')
            i = i + 1

    except:
        continue
