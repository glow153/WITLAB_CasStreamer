import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QDesktopWidget, QLabel, QHBoxLayout, QVBoxLayout,
                             QWidget, QMainWindow, QLineEdit, QPushButton)

from cas_streamer import CasEntryStreamer
from debugmodule import Log


class CasStreamerFrame(QMainWindow):
    def __init__(self, title):
        from datetime import datetime
        super(CasStreamerFrame, self).__init__()
        self.title = title
        self.streamer = CasEntryStreamer()
        self.tag = 'CasStreamerFrame'

        # create widgets
        self.layout1 = QHBoxLayout()
        self.layout2 = QHBoxLayout()
        self.layout3 = QHBoxLayout()
        self.main_layout = QVBoxLayout()
        self.lbl = QLabel('스트리밍 대상 디렉토리')
        # write your streaming directory
        self.ledt = QLineEdit('C:\\Users\\WITLab\\Desktop\\2019 natural\\%s' % (datetime.now().strftime('%Y%m%d')))
        self.lbl2 = QLabel('POST 송신 URL')
        self.ledt2 = QLineEdit('http://127.0.0.1:4000/api/nl/witlab/cas/')
        self.lbl_state = QLabel('스트리밍 상태: 멈춤')
        self.lbl_state.setStyleSheet('QLabel {color: red;}')
        self.btn = QPushButton('시작')
        self.widget = QWidget()

        self.setupUi()
        self.createActions()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.streamer.streaming_off()

    def setupUi(self):
        self.setGeometry(0, 0, 500, 100)
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon('icon.png'))
        self.wnd2Center()

        # add widgets
        self.layout1.addWidget(self.lbl)
        self.layout1.addWidget(self.ledt)
        self.layout2.addWidget(self.lbl2)
        self.layout2.addWidget(self.ledt2)
        self.layout3.addWidget(self.lbl_state)
        self.layout3.addWidget(self.btn)
        self.main_layout.addLayout(self.layout1)
        self.main_layout.addLayout(self.layout2)
        self.main_layout.addLayout(self.layout3)

        # set layout and stretch widgets
        self.layout1.setContentsMargins(5, 5, 5, 5)
        self.layout1.setStretchFactor(self.lbl, 3)
        self.layout1.setStretchFactor(self.ledt, 7)
        self.layout2.setContentsMargins(5, 5, 5, 5)
        self.layout2.setStretchFactor(self.lbl2, 3)
        self.layout2.setStretchFactor(self.ledt2, 7)
        self.layout3.setContentsMargins(5, 5, 5, 5)
        self.layout3.setStretchFactor(self.lbl_state, 5)
        self.layout3.setStretchFactor(self.btn, 5)
        self.widget.setLayout(self.main_layout)
        self.setCentralWidget(self.widget)

    def createActions(self):
        self.btn.clicked.connect(self.toggle_streaming)

    def toggle_streaming(self):
        if self.streamer.is_streaming:
            # streaming off
            self.streamer.streaming_off()

            # change btn caption
            self.lbl_state.setText('스트리밍 상태: 멈춤')
            self.lbl_state.setStyleSheet('QLabel {color: red;}')
            self.btn.setText('시작')

        else:
            try:
                # setup
                self.streamer.set_observer(self.ledt.text(), self.ledt2.text())

                # streaming on
                self.streamer.streaming_on()
            except Exception as e:
                Log.e(self.tag, 'directory path error! :', e.__class__.__name__)
                return

            # change btn caption
            self.lbl_state.setText('스트리밍 상태: 동작중')
            self.lbl_state.setStyleSheet('QLabel {color: green;}')
            self.btn.setText('정지')

        Log.d(self.tag, self.lbl_state.text(), ',', self.streamer.remote_dirpath)

    def wnd2Center(self):
        # geometry of the main window
        qr = self.frameGeometry()
        # center point of screen
        cp = QDesktopWidget().availableGeometry().center()
        # move rectangle's center point to screen's center point
        qr.moveCenter(cp)
        # top left of rectangle becomes top left of window centering it
        self.move(qr.topLeft())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CasStreamerFrame('WitLab CAS data streamer v1.2 (Jake, Momentum)')
    window.show()
    app.exec_()