import sys

# from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QDesktopWidget, QLabel, QHBoxLayout, QVBoxLayout,
                             QWidget, QMainWindow, QLineEdit, QPushButton, QCheckBox)

from controller.cas_streamer import CasEntryStreamer
from lib.debugmodule import Log


class CasStreamerFrame(QMainWindow):
    """
    current issue:
    1. backend 에서 invalid req body 가 뜨면 client는 재전송을 하는데
       이때 스트리머 정지버튼 누르면 뻗음 => 2.0 적용 완료
    2. cas, cas_ird, cas_simple, cas_file 체크박스 만들면 좋을듯 => 2.0 적용 완료
    """
    def __init__(self, title):
        from datetime import datetime
        super(CasStreamerFrame, self).__init__()
        self.title = title
        self.streamer = CasEntryStreamer()
        self.tag = 'CasStreamerFrame'

        self.local_dirpath = 'C:\\Users\\WITLab\\Desktop\\2019 natural\\%s' % (datetime.now().strftime('%Y%m%d'))
        self.url = 'http://127.0.0.1:4000/api/nl/witlab/cas/'

        # create widgets
        self.layout_local = QHBoxLayout()
        self.layout_remote = QHBoxLayout()
        self.layout_sendtype = QHBoxLayout()
        self.layout_status = QHBoxLayout()
        self.main_layout = QVBoxLayout()
        self.lbl_dir = QLabel()
        self.ledt_dirpath = QLineEdit(self.local_dirpath)
        self.lbl_url = QLabel()
        self.ledt_url = QLineEdit(self.url)
        self.lbl_sendtype = QLabel()
        self.chbx_basic = QCheckBox('basic')
        self.chbx_ird = QCheckBox('ird')
        self.chbx_simple = QCheckBox('simple')
        self.chbx_file = QCheckBox('file')
        self.lbl_state = QLabel()
        self.btn_start = QPushButton('START')
        self.main_widget = QWidget()

        self.setupUi()
        self.createActions()

    def setupUi(self):
        self.setGeometry(0, 0, 500, 100)
        self.setWindowTitle(self.title)
        # self.setWindowIcon(QIcon('icon.png'))
        self.wnd2Center()

        # add widgets
        self.layout_local.addWidget(self.lbl_dir)
        self.layout_local.addWidget(self.ledt_dirpath)
        self.layout_remote.addWidget(self.lbl_url)
        self.layout_remote.addWidget(self.ledt_url)
        self.layout_sendtype.addWidget(self.lbl_sendtype)
        self.layout_sendtype.addWidget(self.chbx_basic)
        self.layout_sendtype.addWidget(self.chbx_ird)
        self.layout_sendtype.addWidget(self.chbx_simple)
        self.layout_sendtype.addWidget(self.chbx_file)
        self.layout_status.addWidget(self.lbl_state)
        self.layout_status.addWidget(self.btn_start)
        self.main_layout.addLayout(self.layout_local)
        self.main_layout.addLayout(self.layout_remote)
        self.main_layout.addLayout(self.layout_sendtype)
        self.main_layout.addLayout(self.layout_status)

        # set properties
        self.lbl_dir.setText('Local Directory to Watch')
        self.lbl_url.setText('Remote API URL')
        self.lbl_sendtype.setText('Send Data Type')
        self.lbl_state.setText('Streaming Status: Stopped')
        self.lbl_state.setStyleSheet('QLabel {color: red;}')
        self.chbx_basic.setChecked(True)
        self.chbx_ird.setChecked(True)
        self.chbx_simple.setChecked(True)

        # file streaming : to be continued...
        self.chbx_file.setEnabled(False)

        # set layout and stretch widgets
        self.layout_local.setContentsMargins(5, 5, 5, 5)
        self.layout_local.setStretchFactor(self.lbl_dir, 3)
        self.layout_local.setStretchFactor(self.ledt_dirpath, 7)
        self.layout_remote.setContentsMargins(5, 5, 5, 5)
        self.layout_remote.setStretchFactor(self.lbl_url, 3)
        self.layout_remote.setStretchFactor(self.ledt_url, 7)
        self.layout_sendtype.setContentsMargins(5, 5, 5, 5)
        self.layout_sendtype.setStretchFactor(self.lbl_sendtype, 3)
        self.layout_sendtype.setStretchFactor(self.chbx_basic, 7/4)
        self.layout_sendtype.setStretchFactor(self.chbx_ird, 7/4)
        self.layout_sendtype.setStretchFactor(self.chbx_simple, 7/4)
        self.layout_sendtype.setStretchFactor(self.chbx_file, 7/4)
        self.layout_status.setContentsMargins(5, 5, 5, 5)
        self.layout_status.setStretchFactor(self.lbl_state, 5)
        self.layout_status.setStretchFactor(self.btn_start, 5)
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

    def createActions(self):
        self.btn_start.clicked.connect(self.on_btn_start_clicked)

    def on_btn_start_clicked(self):
        self.toggle_streaming()

    def get_flags(self):
        return {
            'basic': self.chbx_basic.isChecked(),
            'ird': self.chbx_ird.isChecked(),
            'simple': self.chbx_simple.isChecked(),
            'file': self.chbx_file.isChecked()
        }

    def toggle_streaming(self):
        self.local_dirpath = self.ledt_dirpath.text()
        self.url = self.ledt_url.text()

        if self.streamer.is_streaming:
            # streaming off
            self.streamer.streaming_off()

            # enable checkbox
            self.chbx_basic.setEnabled(True)
            self.chbx_ird.setEnabled(True)
            self.chbx_simple.setEnabled(True)

            # change btn caption
            self.lbl_state.setText('Streaming Status: Stopped')
            self.lbl_state.setStyleSheet('QLabel {color: red;}')
            self.btn_start.setText('START')

        else:
            try:
                # setup
                self.streamer.setup_streamer(self.local_dirpath, self.url, self.get_flags())
                # streaming on
                self.streamer.streaming_on()
            except Exception as e:
                Log.e(self.tag, 'streaming start error! :', e.__class__.__name__)
                return

            # disable checkbox
            self.chbx_basic.setEnabled(False)
            self.chbx_ird.setEnabled(False)
            self.chbx_simple.setEnabled(False)

            # change btn caption
            self.lbl_state.setText('Streaming Status: Streaming')
            self.lbl_state.setStyleSheet('QLabel {color: green;}')
            self.btn_start.setText('STOP')

        Log.d(self.tag, self.lbl_state.text(), ',', self.local_dirpath)

    def wnd2Center(self):
        # geometry of the main window
        qr = self.frameGeometry()
        # center point of screen
        cp = QDesktopWidget().availableGeometry().center()
        # move rectangle's center point to screen's center point
        qr.moveCenter(cp)
        # top left of rectangle becomes top left of window centering it
        self.move(qr.topLeft())

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.streamer.streaming_off()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CasStreamerFrame('WitLab CAS data streamer v2.0 (Jake, Momentum)')
    window.show()
    app.exec_()
