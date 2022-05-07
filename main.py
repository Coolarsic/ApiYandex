import sys
import math
from io import BytesIO

import requests
from PIL import Image, ImageQt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QLineEdit, QTextBrowser, QMessageBox
from PyQt5.Qt import Qt
from yandexmaps import get_coords, get_full_address, lonlat_distance, get_nearest_object


def screen_to_geo(pos):
    targetscale = ex.target_scale
    dy = 225 - pos[1]
    dx = pos[0] - 300
    lx = ex.target_coordinates[0] + round(dx / 300 * targetscale * 2, 6)
    ly = ex.target_coordinates[1] + round(dy / 225 * targetscale * 2, 6)
    return round(lx, 6), round(ly, 6)


SCREEN_SIZE = [800, 550]


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.target_place = 'Калининград, Советский Проспект, 159'
        self.target_coordinates = list(map(float, get_coords(self.target_place)))
        self.target_scale = 0.004
        self.target_layer = 'map'
        self.target_index = ''
        self.target_marker_is = False
        self.show_index = False
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
        button.move(SCREEN_SIZE[0] - 180, SCREEN_SIZE[1] - (SCREEN_SIZE[1] // 20 * 20))
        button.clicked.connect(self.set_layer_map)
        button.resize(160, 25)

        # button
        button2 = QPushButton('Спутник', self)
        button2.move(SCREEN_SIZE[0] - 180, SCREEN_SIZE[1] - (SCREEN_SIZE[1] // 20 * 19))
        button2.clicked.connect(self.set_layer_sat)
        button2.resize(160, 25)

        # button
        button3 = QPushButton('Гибрид', self)
        button3.move(SCREEN_SIZE[0] - 180, SCREEN_SIZE[1] - (SCREEN_SIZE[1] // 20 * 18))
        button3.clicked.connect(self.set_layer_gib)
        button3.resize(160, 25)

        # search line
        self.search_line = QLineEdit(self)
        self.search_line.move(SCREEN_SIZE[0] - (SCREEN_SIZE[0] // 20 * 19), SCREEN_SIZE[1] - 50)
        self.search_line.resize(500, 32)

        # search button
        search_button = QPushButton('Искать', self)
        search_button.move(SCREEN_SIZE[0] - 180, SCREEN_SIZE[1] - 50)
        search_button.clicked.connect(self.search_by_address)
        search_button.resize(160, 32)

        # remove marker button
        remove_marker_button = QPushButton('Сброс поискового\nрезультата', self)
        remove_marker_button.move(SCREEN_SIZE[0] - 180, SCREEN_SIZE[1] - 100)
        remove_marker_button.clicked.connect(self.remove_target_marker)
        remove_marker_button.resize(160, 50)

        # address browser
        self.address_browser = QTextBrowser(self)
        self.address_browser.move(SCREEN_SIZE[0] - 180, SCREEN_SIZE[1] // 5)
        self.address_browser.resize(160, 250)

        # turn on off button index
        self.index_button = QPushButton('Показывать почтовый\nиндекс', self)
        self.index_button.move(SCREEN_SIZE[0] - 180, SCREEN_SIZE[1] - 150)
        self.index_button.clicked.connect(self.turn_on_off_index)
        self.index_button.resize(160, 50)

    def search_by_address(self):
        request = self.search_line.text()
        if not request:
            msg = QMessageBox()
            msg.setWindowTitle("Ошибка")
            msg.setText("Строчечка поиска то пустая. Надо бы ее заполнить")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
            return
        object_coordinates = list(map(float, get_coords(request)))
        if self.target_marker_is:
            self.markers.pop(0)
        self.markers.append([object_coordinates[0], ',', object_coordinates[1], ',', 'pm2', 'rd', 'm'])
        self.target_coordinates = object_coordinates
        self.target_marker_is = True
        self.update_image()
        full_address = get_full_address(request)
        self.target_place = full_address[0]
        self.target_index = full_address[1]
        if not self.show_index:
            self.address_browser.setText(full_address[0])
        else:
            self.address_browser.setText(', '.join(full_address))

    def turn_on_off_index(self):
        if self.target_index is None:
            self.show_index = not self.show_index
            if self.show_index:
                self.index_button.setText('Скрывать почтовый\nиндекс')
            else:
                self.index_button.setText('Показывать почтовый\nиндекс')
            msg = QMessageBox()
            msg.setWindowTitle("Ошибка")
            msg.setText("Короче апи Zндекса не выдает индекс")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
            return
        self.show_index = not self.show_index
        if self.show_index:
            self.index_button.setText('Скрывать почтовый\nиндекс')
            self.address_browser.setText(', '.join([self.target_place] + [self.target_index]))
        else:
            self.index_button.setText('Показывать почтовый\nиндекс')
            self.address_browser.setText(self.target_place)

    def remove_target_marker(self):
        if self.target_marker_is:
            self.markers.pop(0)
            self.target_marker_is = False
            self.update_image()
            self.address_browser.clear()
            self.search_line.clear()

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

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            dlx, dly = screen_to_geo((e.pos().x(), e.pos().y()))
            text = get_nearest_object((dlx, dly))
            ex.markers.clear()
            ex.markers.append([dlx, ',', dly, ',', 'pm2', 'rd', 'm'])
            ex.update_image()
            full_address = get_full_address(text)
            if type(full_address) == tuple:
                self.target_index = full_address[-1]
                self.target_place = full_address[0]
                if self.show_index:
                    ex.address_browser.setText(', '.join(full_address))
                else:
                    ex.address_browser.setText(full_address[0])
            else:
                self.target_place = full_address
                self.target_index = None
                ex.address_browser.setText(full_address)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())