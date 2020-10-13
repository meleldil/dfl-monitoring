"""
Libraries import
"""
import sys
from datetime import datetime
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QApplication, QWidget, QToolTip, QProgressBar, QPushButton
from PyQt5.QtGui import QIcon, QFont
import pandas as pd
import requests
from bs4 import BeautifulSoup

"""
Dataset import
"""
df = pd.read_excel('mon.xlsx')

sozd = []
for i in df['dfl']:
    sozd.append(i)

sozd_links = []
for i in sozd:
    s = 'https://sozd.duma.gov.ru/bill/' + i
    sozd_links.append(s)

"""
Thread with Monitoring
"""


class PBThread(QThread):
    def __init__(self, mainwindow):
        super().__init__()
        self.mainwindow = mainwindow

    def run(self):
        progress = 0
        seek = []

        for link in sozd_links:
            page = requests.get(link)
            text = page.text
            soup = BeautifulSoup(text, "lxml")

            for event in soup.find_all('span', {'class': 'hron_date'}):
                try:
                    event_date = datetime.strptime(event.text[:10], '%d.%m.%Y').date()
                    if selected_date <= event_date and link not in seek:
                        seek.append(link)
                except:
                    pass
            for doc in soup.find_all('a', {'class': 'a_event_files'}):
                try:
                    full_title = doc.attrs['title']
                    doc_date = datetime.strptime(full_title[:10], '%d.%m.%Y').date()
                    if selected_date <= doc_date and link not in seek:
                        seek.append(link)
                except:
                    pass
            progress += 100 / len(sozd_links)

            self.mainwindow.progressBar.setValue(int(progress))

            output = pd.DataFrame(seek)
            output.to_excel('output.xlsx')


"""
GUI
"""


class PBmainwindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setGeometry(300, 300, 450, 300)
        self.setWindowTitle('Mon')
        self.setWindowIcon(QIcon('eagle.png'))

        QToolTip.setFont(QFont('SansSerif', 10))

        self.calendar = QtWidgets.QCalendarWidget(self)
        self.calendar.setToolTip('Выберите дату')
        self.calendar.move(20, 20)
        self.calendar.setGridVisible(True)
        self.calendar.clicked.connect(self.date_selection)

        self.pushButton = QPushButton('Start', self)
        self.pushButton.setGeometry(QtCore.QRect(240, 220, 75, 23))

        self.progressBar = QProgressBar(self)
        self.progressBar.setRange(0, 100)
        self.progressBar.setGeometry(QtCore.QRect(30, 220, 201, 23))

        self.pushButton.clicked.connect(self.launch)
        self.PBThread_instance = PBThread(mainwindow=self)

    def date_selection(self, Qdate):
        date = '{0}.{1}.{2}'.format(Qdate.day(), Qdate.month(), Qdate.year())
        global selected_date
        selected_date = datetime.strptime(date, '%d.%m.%Y').date()

    def launch(self):
        self.PBThread_instance.start()


app = QApplication(sys.argv)
main = PBmainwindow()
main.show()
sys.exit(app.exec_())
