import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QFileDialog, QGridLayout, QWidget, QDialog, \
    QVBoxLayout, QMessageBox, QAction, QSpacerItem, QSizePolicy, QHBoxLayout
from PyQt5.QtGui import QPixmap, QFont, QPalette, QBrush
from PyQt5.QtCore import Qt, QRect
from affine_transformation import affine
from detect_polygon import detection
from OCR import ocr_recognize
import cv2
import pickle
import json
import csv


class ResultWindow(QDialog):
    def __init__(self, ocr_result):
        super().__init__()
        self.setWindowTitle("识别结果")
        self.setGeometry(200, 200, 600, 400)
        self.ocr_result = ocr_result

        layout = QVBoxLayout()

        self.result_label = QLabel(self)
        self.result_label.setAlignment(Qt.AlignCenter)
        # 设置字体大小
        font = QFont()
        font.setPointSize(16)  # 将16替换为你想要的字号大小
        self.result_label.setFont(font)
        layout.addWidget(self.result_label)

        if self.ocr_result:
            result_text = "\n".join(f"{key}: {value}" for key, value in self.ocr_result.items())
        else:
            result_text = "暂无识别结果"

        self.result_label.setText(result_text)

        self.export_button = QPushButton('结果导出', self)
        self.export_button.clicked.connect(self.export_results)
        layout.addWidget(self.export_button, alignment=Qt.AlignRight | Qt.AlignBottom)

        self.setLayout(layout)

    def export_results(self):
        if not self.ocr_result:
            QMessageBox.warning(self, "警告", "没有识别结果可以导出。")
            return

        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "选择导出文件", "",
                                                   "JSON文件 (*.json);;文本文件 (*.txt);;CSV文件 (*.csv)",
                                                   options=options)

        if file_path:
            if file_path.endswith('.json'):
                self.export_to_json(file_path)
            elif file_path.endswith('.txt'):
                self.export_to_txt(file_path)
            elif file_path.endswith('.csv'):
                self.export_to_csv(file_path)

    def export_to_json(self, file_path):
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.ocr_result, f, ensure_ascii=False, indent=4)
            QMessageBox.information(self, "成功", f"结果已导出到 {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出失败: {e}")

    def export_to_txt(self, file_path):
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                for key, value in self.ocr_result.items():
                    f.write(f"{key}: {value}\n")
            QMessageBox.information(self, "成功", f"结果已导出到 {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出失败: {e}")

    def export_to_csv(self, file_path):
        try:
            with open(file_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(self.ocr_result.keys())
                writer.writerow(self.ocr_result.values())
            QMessageBox.information(self, "成功", f"结果已导出到 {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出失败: {e}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("基于计算机视觉的设备参数采集")
        self.setGeometry(100, 100, 1000, 600)

        self.current_image_path = None
        self.step_count = 0
        self.intermediate_image_path = None
        self.detection_result = None
        self.ocr_result = None

        self.initUI()

    def initUI(self):
        # 设置背景图片
        self.setAutoFillBackground(True)
        palette = QPalette()
        pixmap = QPixmap("background.png")
        pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation)
        palette.setBrush(QPalette.Window, QBrush(pixmap))
        self.setPalette(palette)

        # 菜单栏
        menubar = self.menuBar()
        view_result_action = QAction('查看结果', self)
        view_result_action.triggered.connect(self.view_results)
        menubar.addAction(view_result_action)



        # 设置全局字体
        font = QFont("Arial", 14)
        # 初始化中央小部件和网格布局
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        grid_layout = QGridLayout(central_widget)
        grid_layout.setSpacing(0)


        # 创建一个垂直布局用于左侧按钮
        left_button_layout = QVBoxLayout()
        left_button_layout.setSpacing(30)  # 设置按钮之间的间距

        # 添加一个空白标签用于调整顶部间距
        top_spacer_label = QLabel(self)
        top_spacer_label.setFixedSize(500, 165)  # 调整第二个参数来设置顶部间距的高度
        left_button_layout.addWidget(top_spacer_label)




        # 左侧按钮
        self.rx_button = QPushButton('设备1', self)
        self.rx_button.setFont(font)
        self.rx_button.setFixedSize(100, 30)
        self.rx_button.setStyleSheet("background-color: rgba(255, 255, 255, 0.5);")
        self.rx_button.clicked.connect(self.open_image)
        left_button_layout.addWidget(self.rx_button, alignment=Qt.AlignLeft | Qt.AlignTop)

        self.label_button = QPushButton('设备2', self)
        self.label_button.setFont(font)
        self.label_button.setFixedSize(100, 30)
        self.label_button.setStyleSheet("background-color: rgba(255, 255, 255, 0.5);")
        self.label_button.clicked.connect(self.open_image)
        left_button_layout.addWidget(self.label_button)

        self.stretch_button = QPushButton('设备3', self)
        self.stretch_button.setFont(font)
        self.stretch_button.setFixedSize(100, 30)
        self.stretch_button.setStyleSheet("background-color: rgba(255, 255, 255, 0.5);")
        self.stretch_button.clicked.connect(self.open_image)
        left_button_layout.addWidget(self.stretch_button, alignment=Qt.AlignLeft | Qt.AlignTop)

        grid_layout.addLayout(left_button_layout, 0, 0, 3, 1, alignment=Qt.AlignLeft | Qt.AlignTop)

        # 创建一个内部的水平布局
        image_layout = QHBoxLayout()

        # 图片展示框
        self.image_label = QLabel('图片展示区域', self)
        # 添加一个空白的小部件到内部布局中，用于调整图片展示框的位置
        spacer = QWidget()
        spacer.setFixedSize(142, 545)  # 根据需要调整空白小部件的大小
        image_layout.addWidget(spacer)

        # 将图片展示框添加到内部布局中
        image_layout.addWidget(self.image_label)
        self.image_label.setStyleSheet("QLabel { background-color : lightgray;  }")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setFont(font)
        self.image_label.setFixedSize(685, 400)


        # 将内部布局添加到网格布局中
        grid_layout.addLayout(image_layout, 0, 0, 3, 3, alignment=Qt.AlignRight | Qt.AlignTop)

        # 调整层次顺序
        self.rx_button.raise_()
        self.label_button.raise_()
        self.stretch_button.raise_()

        # 创建一个水平布局用于放置按钮
        button_layout = QHBoxLayout()

        # 添加一个空白的小部件到上方，用于微调位置
        spacer_widget = QWidget()
        spacer_widget.setFixedSize(250, 126)  # 根据需要调整空白小部件的大小

        # 创建一个垂直布局来包含空白小部件和按钮水平布局
        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(spacer_widget)
        vertical_layout.addLayout(button_layout)

        # 将垂直布局添加到网格布局中
        grid_layout.addLayout(vertical_layout, 2, 2, 1, 2, alignment=Qt.AlignLeft | Qt.AlignTop)

        # 创建一键识别按钮
        self.confirm_button = QPushButton('一键识别', self)
        self.confirm_button.setFont(font)
        self.confirm_button.setFixedSize(100, 30)
        self.confirm_button.setStyleSheet("background-color: rgba(255, 255, 255, 0.5);")
        self.confirm_button.clicked.connect(self.confirm_action)

        # 创建分步识别按钮
        self.batch_confirm_button = QPushButton('分步识别', self)
        self.batch_confirm_button.setFont(font)
        self.batch_confirm_button.setFixedSize(100, 30)
        self.batch_confirm_button.setStyleSheet("background-color: rgba(255, 255, 255, 0.5);")
        self.batch_confirm_button.clicked.connect(self.batch_confirm_action)

        # 添加按钮和空白小部件到水平布局中，并设置间距
        button_layout.addWidget(self.confirm_button)
        button_layout.addSpacing(20)  # 增加按钮之间的间距
        button_layout.addWidget(self.batch_confirm_button)

    def open_image(self):
        print(1)
        options = QFileDialog.Options()
        print("Opening file dialog...")  # 添加调试信息
        file_name, _ = QFileDialog.getOpenFileName(self, "选择图片文件", "",
                                                   "图片文件 (*.png *.jpg *.bmp);;所有文件 (*)", options=options)
        if file_name:
            print(f"Selected file: {file_name}")  # 添加调试信息
            self.current_image_path = file_name
            self.display_image(file_name)
            self.step_count = 0
            self.intermediate_image_path = file_name
            self.detection_result = None
            self.ocr_result = None
        else:
            print("No file selected")  # 添加调试信息

    def display_image(self, file_path):
        print(f"Displaying image: {file_path}")  # 添加调试信息
        pixmap = QPixmap(file_path)
        if pixmap.isNull():
            print("Failed to load image")  # 添加调试信息
        else:
            self.image_label.setPixmap(pixmap)
            self.image_label.setScaledContents(True)

    def confirm_action(self):
        if self.current_image_path:
            processed_image_path = self.process_image(self.current_image_path)
            if processed_image_path:
                self.display_image(processed_image_path)

    def batch_confirm_action(self):
        if self.current_image_path:
            if self.step_count == 0:
                processed_image_path = self.step_one(self.intermediate_image_path)
                self.intermediate_image_path = processed_image_path
            elif self.step_count == 1:
                processed_image_path = self.step_two(self.intermediate_image_path)
                self.intermediate_image_path = processed_image_path
            elif self.step_count == 2:
                processed_image_path = self.step_three(self.intermediate_image_path)
            self.display_image(processed_image_path)
            self.step_count = (self.step_count + 1) % 3

    def step_one(self, image_path):
        try:
            image_detect, image_label = detection(image_path)
            intermediate_image_path = "step_one.png"
            cv2.imwrite(intermediate_image_path, image_detect)
            self.detection_result = image_label
            with open('detection_result.pkl', 'wb') as f:
                pickle.dump(self.detection_result, f)
            return intermediate_image_path
        except Exception as e:
            print(f"Error in step one: {e}")
            return None

    def step_two(self, image_path):
        try:
            image = cv2.imread(image_path)
            with open('detection_result.pkl', 'rb') as f:
                image_label = pickle.load(f)
            cut_image = affine(image, image_label)
            intermediate_image_path = "step_two.png"
            cv2.imwrite(intermediate_image_path, cut_image)
            return intermediate_image_path
        except Exception as e:
            print(f"Error in step two: {e}")
            return None

    def step_three(self, image_path):
        try:
            self.ocr_result = ocr_recognize(image_path)
            final_image_path = "result.jpg"
            return final_image_path
        except Exception as e:
            print(f"Error in step three: {e}")
            return None

    def process_image(self, image_path):
        try:
            image = cv2.imread(image_path)
            if image is None:
                print("Error: Cannot read image.")
                return None
            image_detect, image_label = detection(image_path)
            cut_image = affine(image, image_label)
            processed_image_path = "processed_image.png"
            cv2.imwrite(processed_image_path, cut_image)
            self.ocr_result = ocr_recognize("processed_image.png")
            ocr_dir = "result.jpg"
            return ocr_dir
        except Exception as e:
            print(f"Error in process_image: {e}")
            return None

    def view_results(self):
        result_window = ResultWindow(self.ocr_result)
        result_window.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
