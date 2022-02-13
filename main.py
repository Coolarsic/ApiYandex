import sys
from io import BytesIO

import requests
from PIL import Image, ImageQt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.Qt import Qt
from yandexmaps import get_coords

SCREEN_SIZE = [600, 450]


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.target_coordinates = 'Калининград, Советский Проспект, 192'
        self.target_scale = 0.004
        self.getImage()
        self.initUI()

    def getImage(self):
        coords = get_coords(self.target_coordinates)
        map_request = f"http://static-maps.yandex.ru/1.x/?ll={','.join(coords)}&spn={self.target_scale},{self.target_scale}&l=map"
        response = requests.get(map_request)

        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        self.img = ImageQt.ImageQt(Image.open(BytesIO(response.content)))

    def initUI(self):
        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.setWindowTitle('Отображение карты')

        ## Изображение
        self.image = QLabel(self)
        self.image.move(0, 0)
        self.image.resize(600, 450)
        self.image.setPixmap(QPixmap.fromImage(self.img))

    def update_image(self):
        self.image.setPixmap(QPixmap.fromImage(self.img))

    def keyPressEvent(self, e):
        print('--------')
        print(self.target_scale)
        if e.key() == Qt.Key_PageUp:
            if self.target_scale == 45.824:
                return
            if 0.001 < self.target_scale < 0.007:
                self.target_scale += 0.003
            elif self.target_scale == 0.007:
                self.target_scale += 0.005
            elif self.target_scale == 0.012:
                self.target_scale += 0.011
            elif self.target_scale == 0.023:
                self.target_scale += 0.022
            elif self.target_scale == 0.045:
                self.target_scale += 0.045
            elif self.target_scale == 0.09:
                self.target_scale += 0.089
            elif self.target_scale == 0.179:
                self.target_scale += 0.179
            else:
                self.target_scale *= 2
        elif e.key() == Qt.Key_PageDown:
            if self.target_scale < 0.003:
                return
            if 0.001 < self.target_scale < 0.007:
                self.target_scale = 0.001
            elif self.target_scale == 0.007:
                self.target_scale -= 0.005
            elif self.target_scale == 0.012:
                self.target_scale -= 0.011
            elif self.target_scale == 0.023:
                self.target_scale -= 0.022
            elif self.target_scale == 0.045:
                self.target_scale -= 0.045
            elif self.target_scale == 0.09:
                self.target_scale -= 0.089
            elif self.target_scale == 0.179:
                self.target_scale -= 0.179
            else:
                self.target_scale /= 2
        self.getImage()
        self.update_image()
        print(self.target_scale)
        print('--------')
        print()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())