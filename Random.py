import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap
import keyboard as kb
import selectMusic as sM
import configparser
import time

main_ui = uic.loadUiType("selector_ui.ui")[0]

# UI
class SelectorUI(QMainWindow, main_ui):

    # initUI(), readYourData() 실행
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUI()
        self.initConfig()
        self.yourdata = sM.readYourData()


        kb.add_hotkey('f7', lambda: self.randomStart(), suppress=True)

    # 시그널, 스타일
    def initUI(self):
        self.setWindowIcon(QIcon('icon.ico'))
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.minimizeButton.clicked.connect(lambda: self.showMinimized())
        self.closeButton.clicked.connect(lambda: self.close())
        def moveWindow(event):
            if event.buttons() == Qt.LeftButton:
                self.move(self.pos() + event.globalPos() - self.dragPos)
                self.dragPos = event.globalPos()
                event.accept()
        self.title_bar.mouseMoveEvent = moveWindow

        self.lvl_min.valueChanged.connect(lambda: self.label_lvl_min.setText(str(self.lvl_min.value())))
        self.lvl_max.valueChanged.connect(lambda: self.label_lvl_max.setText(str(self.lvl_max.value())))
        self.label_lvl_min.setText(str(self.lvl_min.value()))
        self.label_lvl_max.setText(str(self.lvl_max.value()))
        # label_ms = QLabel('{0}ms'.format(self.slider_delay.value()))
        # self.slider_delay.valueChanged.connect(lambda: label_ms.setText('{0}ms'.format(self.slider_delay.value())))
        self.cb_online.toggled.connect(self.onlineSignal)

        self.data_button.clicked.connect(lambda: DataUI(self))
        self.filter_tab_bt.setAutoExclusive(True)
        self.advanced_tab_bt.setAutoExclusive(True)
        self.filter_tab_bt.clicked.connect(self.changeTab)
        self.advanced_tab_bt.clicked.connect(self.changeTab)
        self.cb_collab.clicked.connect(self.collabSignal)
        self.cb_gg.toggled.connect(lambda: self.collabChildSignal(self.cb_gg))
        self.cb_gc.toggled.connect(lambda: self.collabChildSignal(self.cb_gc))
        self.cb_dm.toggled.connect(lambda: self.collabChildSignal(self.cb_dm))
        self.cb_cy.toggled.connect(lambda: self.collabChildSignal(self.cb_cy))
        self.cb_gf.toggled.connect(lambda: self.collabChildSignal(self.cb_gf))
        self.cb_chu.toggled.connect(lambda: self.collabChildSignal(self.cb_chu))

    def initConfig(self):
        config = configparser.ConfigParser()
        config.read('config.ini', encoding='UTF-8')

        self.values = ['4B', '5B', '6B', '8B', 'NM', 'HD', 'MX', 'SC',
                'RP', 'P1', 'P2', 'TR', 'CE', 'BS', 'VE', 'ES',
                'T1', 'T2', 'T3', 'GG', 'GC', 'DM', 'CY',
                'GF', 'CHU']
        self.checkboxes = [self.cb_4b, self.cb_5b, self.cb_6b, self.cb_8b, self.cb_nm, self.cb_hd, self.cb_mx, self.cb_sc,
                    self.cb_rp, self.cb_p1, self.cb_p2, self.cb_tr, self.cb_ce, self.cb_bs, self.cb_ve, self.cb_es,
                    self.cb_t1, self.cb_t2, self.cb_t3, self.cb_gg, self.cb_gc, self.cb_dm, self.cb_cy,
                    self.cb_gf, self.cb_chu]
        _iter = iter(self.checkboxes)

        for i in self.values:
            j = next(_iter)
            if config['FILTER'][i] == '1':
                j.setChecked(True)
        if config['FILTER']['Freestyle'] == '1':
            self.cb_freestyle.setChecked(True)
        else:
            self.cb_online.setChecked(True)
        

    def mousePressEvent(self, event):
        self.dragPos = event.globalPos()
    
    def onlineSignal(self):
        if self.cb_online.isChecked():
            self.lock_bt.move(0,0)
            self.lock_diff.move(0,0)
        else:
            self.lock_bt.move(-370,0)
            self.lock_diff.move(-370,0)

    def changeTab(self):
        if self.filter_tab_bt.isChecked():
            self.tabWidget.setCurrentIndex(0)
            self.current_tab.setText('FILTER')
        elif self.advanced_tab_bt.isChecked():
            self.tabWidget.setCurrentIndex(1)
            self.current_tab.setText('ADVANCED')
    
    def collabSignal(self):
        checkboxes = [self.cb_gg, self.cb_gc, self.cb_dm, self.cb_cy, self.cb_gf, self.cb_chu]
        if self.cb_collab.isChecked():
            for i in checkboxes:
                i.setChecked(True)
            self.collab_frame.setStyleSheet('background:#1e1e1e')
        else:
            for i in checkboxes:
                i.setChecked(False)
            self.collab_frame.setStyleSheet('background:#181819')
    
    def collabChildSignal(self, child):
        if child.isChecked():
            self.cb_collab.setChecked(True)
            self.collab_frame.setStyleSheet('background:#1e1e1e')
        else:
            if not self.cb_gg.isChecked() and not self.cb_gc.isChecked() and not self.cb_dm.isChecked() \
                and not self.cb_cy.isChecked() and not self.cb_gf.isChecked() and not self.cb_chu.isChecked():
                self.cb_collab.setChecked(False)
                self.collab_frame.setStyleSheet('background:#181819')


    # 필터 인풋 데이터
    def filterInputData(self):
        # 버튼 필터
        fil_bt = [self.values[i] for i in range(4) if self.checkboxes[i].isChecked()]
        # 스타일 필터
        fil_st = [self.values[i] for i in range(4,8) if self.checkboxes[i].isChecked()]
        # 시리즈 필터
        fil_sr = set(self.values[i] for i in range(8,25) if self.checkboxes[i].isChecked())
        # 레벨 필터
        fil_min = self.lvl_min.value()
        fil_max = self.lvl_max.value()
        # 입력 지연값
        # input_delay = self.slider_delay.value()
        input_delay = 10
        # 모드 선택값
        if self.cb_freestyle.isChecked(): isFreestyle = True
        else: isFreestyle = False

        return fil_bt, fil_st, fil_sr, fil_min, fil_max, input_delay/1000, isFreestyle
   
    # 무작위 뽑기
    def randomStart(self):
        kb.block_key('f7')
        start = time.time()
        bt_list, st_list, sr_list, min_int, max_int, input_delay, isFreestyle = self.filterInputData()
        selected_title, selected_artist, selected_btst, selected_series, bt_input, init_input, down_input, right_input = \
            sM.selectingMusic(self.yourdata, bt_list, st_list, sr_list, min_int, max_int, isFreestyle)
        print(selected_title, selected_artist, selected_btst, selected_series, sep="    ")
        def setSelectedUi(title, artist, btst, series):
            self.selectedTitle.setText(title)
            self.selectedArtist.setText(artist)
            self.selectedTitle.setStyleSheet('background:transparent; color:#ffffff')
            self.selectedArtist.setStyleSheet('background:transparent; color:#ffffff')
            if btst == None:
                self.selectedBtSt.clear()
            else:
                self.selectedBtSt.setPixmap(QPixmap('images/{0}.png'.format(btst)))

            self.ifCollab.setStyleSheet('background-color:transparent')
            if series == None:
                self.selectedSeriesBox.setStyleSheet('background-color:#c8c8c8')
                self.selectedSeriesGrad.setStyleSheet('background-color:qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(141, 141, 141, 255), stop:1 rgba(223, 223, 223, 255))')
            elif series == 'RP':
                self.selectedSeriesBox.setStyleSheet('background-color:#ffd250')
                self.selectedSeriesGrad.setStyleSheet('background-image:url(images/RP.png)')
            elif series == 'P1':
                self.selectedSeriesBox.setStyleSheet('background-color:#25deff')
                self.selectedSeriesGrad.setStyleSheet('background-image:url(images/P1.png)')
            elif series == 'P2':
                self.selectedSeriesBox.setStyleSheet('background-color:#ff5082')
                self.selectedSeriesGrad.setStyleSheet('background-image:url(images/P2.png)')
            elif series == 'TR':
                self.selectedSeriesBox.setStyleSheet('background-color:#7582ff')
                self.selectedSeriesGrad.setStyleSheet('background-image:url(images/TR.png)')
            elif series == 'CE':
                self.selectedSeriesBox.setStyleSheet('background-color:#ffffff')
                self.selectedSeriesGrad.setStyleSheet('background-image:url(images/CE.png)')
                self.selectedTitle.setStyleSheet('background:transparent; color:#000000')
                self.selectedArtist.setStyleSheet('background:transparent; color:#000000')
            elif series == 'BS':
                self.selectedSeriesBox.setStyleSheet('background-color:#e90000')
                self.selectedSeriesGrad.setStyleSheet('background-image:url(images/BS.png)')
            elif series == 'VE':
                self.selectedSeriesBox.setStyleSheet('background-color:#ff7f42')
                self.selectedSeriesGrad.setStyleSheet('background-image:url(images/VE.png)')
            elif series == 'ES':
                self.selectedSeriesBox.setStyleSheet('background-color:#34df26')
                self.selectedSeriesGrad.setStyleSheet('background-image:url(images/ES.png)')
            elif series == 'T1':
                self.selectedSeriesBox.setStyleSheet('background-color:#f01cc8')
                self.selectedSeriesGrad.setStyleSheet('background-image:url(images/T1.png)')
            elif series == 'T2':
                self.selectedSeriesBox.setStyleSheet('background-color:#c35a00')
                self.selectedSeriesGrad.setStyleSheet('background-image:url(images/T2.png)')
            elif series == 'T3':
                self.selectedSeriesBox.setStyleSheet('background-color:#568bff')
                self.selectedSeriesGrad.setStyleSheet('background-image:url(images/T3.png)')
            else:
                self.selectedSeriesBox.setStyleSheet('background-color:#c0c0c0')
                self.selectedSeriesGrad.setStyleSheet('background-image:url(images/COL.png)')
                if series == 'GG': self.ifCollab.setStyleSheet('background-color:#d73e0e')
                elif series == 'GC': self.ifCollab.setStyleSheet('background-color:#51eefe')
                elif series == 'DM': self.ifCollab.setStyleSheet('background-color:#98e3d6')
                elif series == 'CY': self.ifCollab.setStyleSheet('background-color:#ec1538')
                elif series == 'GF': self.ifCollab.setStyleSheet('background-color:#fdb426')
                elif series == 'CHU': self.ifCollab.setStyleSheet('background-color:#ffd700')
        setSelectedUi(selected_title, selected_artist, selected_btst,selected_series)
        if selected_title != 'None':
            sM.inputKeyboard(selected_title, bt_input, init_input, down_input, right_input, input_delay, isFreestyle)
        print(time.time() - start)
        kb.unblock_key('f7')



class DataUI(QDialog):
    def __init__(self, parent):
        super(DataUI, self).__init__(parent)
        data_ui = 'modify_data_ui.ui'
        uic.loadUi(data_ui, self)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setWindowModality(Qt.ApplicationModal)
        self.modifyButton.clicked.connect(self.modifyDataInputData)
        self.cancelButton.clicked.connect(lambda: self.close())
        self.show()
    
    # 데이터 생성 인풋 데이터 & YourData.csv 생성
    def modifyDataInputData(self):
        values = ['TR', 'CE', 'BS', 'VE', 'ES',
                    'T1', 'T2', 'T3', 'GC', 'DM',
                    'CY', 'GF', 'CHU']
        checkboxes = [self.yd_cb_tr, self.yd_cb_ce, self.yd_cb_bs, self.yd_cb_ve, self.yd_cb_es,
                    self.yd_cb_t1, self.yd_cb_t2, self.yd_cb_t3, self.yd_cb_gc, self.yd_cb_dm,
                    self.yd_cb_cy, self.yd_cb_gf, self.yd_cb_chu]
        fil_yd_sr = set(values[i] for i in range(13) if checkboxes[i].isChecked())
        fil_yd_sr.add('RP')
        fil_yd_sr.add('P1')
        fil_yd_sr.add('P2')
        fil_yd_sr.add('GG')
        sM.modifyYourData(fil_yd_sr)
        self.close()
        


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SelectorUI()
    ex.show()
    sys.exit(app.exec_())