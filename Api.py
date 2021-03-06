import sys

import requests
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFocus()
        uic.loadUi('1.ui', self)
        self.setWindowTitle('MapApi')
        self.buttonGroup.buttonClicked.connect(self.generate)
        self.radioButton_3.clicked.connect(self.generate)
        self.radioButton_4.clicked.connect(self.generate)
        self.type = False
        self.pushButton.clicked.connect(self.search)
        self.pushButton_2.clicked.connect(self.vipe)

    def keyPressEvent(self, event):
        global map_params
        if event.key() == Qt.Key_PageDown:
            if float(map_params['spn'].split(',')[0]) * 1.1 < 40 and \
                    float(map_params['spn'].split(',')[1]) * 1.1 < 40:
                map_params['spn'] = ','.join([str(float(map_params['spn'].split(',')[0]) * 1.1),
                                              str(float(map_params['spn'].split(',')[1]) * 1.1)])
        elif event.key() == Qt.Key_PageUp:
            if float(map_params['spn'].split(',')[0]) * 0.1 > 0.001 and \
                    float(map_params['spn'].split(',')[1]) * 0.1 > 0.001:
                map_params['spn'] = ','.join([str(float(map_params['spn'].split(',')[0]) * 0.1),
                                              str(float(map_params['spn'].split(',')[1]) * 0.1)])
        elif event.key() == Qt.Key_Up:
            map_params['ll'] = ','.join([str(float(map_params['ll'].split(',')[0])),
                                         str(float(map_params['ll'].split(',')[1]) +
                                             float(map_params['spn'].split(',')[0]))])
        elif event.key() == Qt.Key_Down:
            map_params['ll'] = ','.join(
                [str(float(map_params['ll'].split(',')[0])),
                 str(float(map_params['ll'].split(',')[1]) -
                     float(map_params['spn'].split(',')[0]))])
        elif event.key() == Qt.Key_Right:
            map_params['ll'] = ','.join(
                [str(float(map_params['ll'].split(',')[0]) +
                     float(map_params['spn'].split(',')[0])),
                 str(float(map_params['ll'].split(',')[1]))])
        elif event.key() == Qt.Key_Left:
            map_params['ll'] = ','.join(
                [str(float(map_params['ll'].split(',')[0]) -
                     float(map_params['spn'].split(',')[0])),
                 str(float(map_params['ll'].split(',')[1]))])
        request()

    def generate(self):
        global map_params
        for button in self.buttonGroup.buttons():
            if button.isChecked():
                map_params['l'] = button.text()
                if button.text() == 'sat':
                    self.type = True
                else:
                    self.type = False
        if self.radioButton_4.isChecked():
            map_params['l'] += f',{self.radioButton_4.text()}'
        if self.radioButton_3.isChecked():
            map_params['l'] += f',{self.radioButton_3.text()}'
        request()

    def search(self):
        global map_params
        geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
        geocoder_params = {
            "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
            "geocode": self.lineEdit.text(),
            "format": "json"}
        try:
            response = requests.get(geocoder_api_server, params=geocoder_params)
            json_response = response.json()
            toponym = json_response["response"]["GeoObjectCollection"][
                "featureMember"][0]["GeoObject"]
            address = toponym['metaDataProperty']['GeocoderMetaData']['Address']['formatted']
            try:
                index = toponym['metaDataProperty']['GeocoderMetaData']['Address']['postal_code']
            except Exception:
                print(1)
                self.checkBox.setCheckState(False)
            toponym_coodrinates = toponym["Point"]["pos"]
            toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
        except Exception:
            return
        map_params['ll'] = ','.join([toponym_longitude, toponym_lattitude])
        map_params['pt'] = f"{','.join([toponym_longitude, toponym_lattitude])}" \
                           f",flag"
        self.textBrowser.setPlainText('\n'.join(address.split(', ')))
        if self.checkBox.isChecked():
            self.textBrowser.setPlainText('\n'.join(address.split(', ')) + '\n' + index)
        else:
            self.textBrowser.setPlainText('\n'.join(address.split(', ')))
        request()

    def vipe(self):
        global map_params
        map_params.pop('pt', None)
        self.lineEdit.setText('')
        self.textBrowser.setPlainText('')
        request()

    def load_image(self, image):
        self.pixmap = QPixmap(image)
        self.label.setPixmap(self.pixmap)


app = QApplication(sys.argv)
ex = MyWidget()
server = 'https://static-maps.yandex.ru/1.x/'
map_params = {
    'll': '37.795384,55.694768',
    'spn': '0.5,0.5',
    'l': 'map'
}


def request():
    response = requests.get(server, params=map_params)
    if response:
        if not ex.type:
            map_file = "map.png"
        else:
            map_file = 'map.jpg'
        with open(map_file, "wb") as file:
            file.write(response.content)
            ex.load_image(map_file)
    else:
        print("Ошибка выполнения запроса:")


request()
ex.show()
sys.exit(app.exec_())
