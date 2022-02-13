import sys
from io import BytesIO

import requests
from PIL import Image, ImageQt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QLineEdit
from PyQt5.Qt import Qt
from yandexmaps import get_coords

SCREEN_SIZE = [700, 550]


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.target_place = 'Калининград, Советский Проспект, 159'
        self.target_coordinates = list(map(float, get_coords(self.target_place)))
        self.target_scale = 0.004
        self.target_layer = 'map'
        self.target_marker_is = False
        self.markers = []
        self.getImage()
        self.initUI()

    def getImage(self):
        # self.target_coordinates = list(map(float, get_coords(self.target_place)))
        if len(self.markers) != 0:
            markers = '&pt='
            temp_markers = []
            for marker in self.markers:
                temp_markers.append(''.join(list(map(str, marker))))
            markers += '~'.join(temp_markers)
        else:
            markers = ''
        coords = map(str, self.target_coordinates)
        map_request = f"http://static-maps.yandex.ru/1.x/?ll={','.join(coords)}&spn={self.target_scale},{self.target_scale}&l={self.target_layer}{markers}"
        print(map_request)
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

        # Изображение
        self.image = QLabel(self)
        self.image.move(0, 0)
        self.image.resize(600, 450)
        self.image.setPixmap(QPixmap.fromImage(self.img))

        # button
        button = QPushButton('Схема', self)
        button.move(SCREEN_SIZE[0] - 80, SCREEN_SIZE[1] - (SCREEN_SIZE[1] // 20 * 20))
        button.clicked.connect(self.set_layer_map)

        # button
        button2 = QPushButton('Спутник', self)
        button2.move(SCREEN_SIZE[0] - 80, SCREEN_SIZE[1] - (SCREEN_SIZE[1] // 20 * 19))
        button2.clicked.connect(self.set_layer_sat)

        # button
        button3 = QPushButton('Гибрид', self)
        button3.move(SCREEN_SIZE[0] - 80, SCREEN_SIZE[1] - (SCREEN_SIZE[1] // 20 * 18))
        button3.clicked.connect(self.set_layer_gib)

        # search line
        self.search_line = QLineEdit(self)
        self.search_line.move(SCREEN_SIZE[0] - (SCREEN_SIZE[0] // 20 * 19), SCREEN_SIZE[1] - 50)
        self.search_line.resize(500, 32)

        # search button
        search_button = QPushButton('Искать', self)
        search_button.move(SCREEN_SIZE[0] // 20 * 16, SCREEN_SIZE[1] - 50)
        search_button.clicked.connect(self.search_by_address)
        search_button.resize(100, 32)

        # remove marker button
        remove_marker_button = QPushButton('Сброс поискового\nрезультата', self)
        remove_marker_button.move(SCREEN_SIZE[0] // 20 * 16, SCREEN_SIZE[1] - 100)
        remove_marker_button.clicked.connect(self.remove_target_marker)
        remove_marker_button.resize(100, 50)

    def search_by_address(self):
        request = self.search_line.text()
        object_coordinates = list(map(float, get_coords(request)))
        if self.target_marker_is:
            self.markers.pop(0)
        self.markers.append([object_coordinates[0], ',', object_coordinates[1], ',', 'pm2', 'rd', 'm'])
        self.target_coordinates = object_coordinates
        self.target_marker_is = True
        self.update_image()
        self.search_line.clear()

    def remove_target_marker(self):
        if self.target_marker_is:
            self.markers.pop(0)
            self.target_marker_is = False
            self.update_image()

    def set_layer_map(self):
        self.target_layer = 'map'
        self.update_image()

    def set_layer_sat(self):
        self.target_layer = 'sat'
        self.update_image()

    def set_layer_gib(self):
        self.target_layer = 'sat,skl'
        self.update_image()

    def update_image(self):
        self.getImage()
        self.image.setPixmap(QPixmap.fromImage(self.img))

    def key_page_up_process(self):
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

    def key_page_down_process(self):
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

    def keyPressEvent(self, e):
        # print('--------')
        # print(self.target_scale)
        good_keys = [Qt.Key_PageUp, Qt.Key_PageDown, Qt.Key_Up, Qt.Key_Left, Qt.Key_Right, Qt.Key_Down]
        if e.key() not in good_keys:
            return
        if e.key() == Qt.Key_PageUp:
            self.key_page_up_process()
        elif e.key() == Qt.Key_PageDown:
            self.key_page_down_process()
        elif e.key() == Qt.Key_Up:
            self.target_coordinates[1] += 0.002500
        elif e.key() == Qt.Key_Left:
            self.target_coordinates[0] -= 0.002500
        elif e.key() == Qt.Key_Right:
            self.target_coordinates[0] += 0.002500
        elif e.key() == Qt.Key_Down:
            self.target_coordinates[1] -= 0.002500
        self.update_image()
        # print(self.target_scale)
        # print('--------')
        # print()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())