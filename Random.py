import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QSystemTrayIcon
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont, QFontDatabase
import keyboard as kb
import selectMusic as sM
import configparser
from threading import Thread

main_ui = uic.loadUiType("selector_ui.ui")[0]

# UI
class SelectorUI(QMainWindow, main_ui):

    # initUI(), readYourData() 실행
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.history = HistoryUI(self)
        self.initUI()
        self.initConfig()
        self.yourdata = sM.readYourData()
        self.isRunning = False
        self.isDebug = False
                
        kb.on_press_key('f7', lambda e: self.check(str(e)), suppress=True)

    # 랜덤 선곡 시작 여부 조사
    def check(self, e):
        if not self.isRunning:
            print('\n\n\n\n\n\nstart')
            thd_rS = Thread(target=self.randomStart)
            thd_rS.start()
        else:
            print('denied')

    # 시그널, 스타일
    def initUI(self):
        # 폰트DB
        self.fontDB = QFontDatabase()
        self.fontDB.addApplicationFont('fonts/Lato-Black.ttf')
        self.fontDB.addApplicationFont('fonts/Lato-Bold.ttf')
        self.fontDB.addApplicationFont('fonts/Lato-Light.ttf')
        self.fontDB.addApplicationFont('fonts/Lato-Regular.ttf')
        self.fontDB.addApplicationFont('fonts/Lato-Thin.ttf')
        # 윈도우 창
        self.setWindowIcon(QIcon('icon.ico'))
        self.setWindowFlags(Qt.FramelessWindowHint)
        # 시스템 트레이
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(QIcon('icon.ico'))
        self.tray.activated.connect(self.show)
        self.tray.activated.connect(self.tray.hide)
        self.tray.hide()
        # 상단바
        self.minimizeButton.clicked.connect(self.hide)
        self.minimizeButton.clicked.connect(self.tray.show)
        self.closeButton.clicked.connect(self.close)
        def moveWindow(event):
            if event.buttons() == Qt.LeftButton:
                self.move(self.pos() + event.globalPos() - self.dragPos)
                self.dragPos = event.globalPos()
                event.accept()
        self.title_bar.mouseMoveEvent = moveWindow
        # 레벨
        self.lvl_min.valueChanged.connect(lambda: self.lvlChanged(self.lvl_min, self.label_lvl_min))
        self.lvl_max.valueChanged.connect(lambda: self.lvlChanged(self.lvl_max, self.label_lvl_max))
        self.label_lvl_min.setText(str(self.lvl_min.value()))
        self.label_lvl_max.setText(str(self.lvl_max.value()))
        # 입력 지연
        self.label_ms.setText('{0}ms'.format(self.slider_delay.value()))
        self.slider_delay.valueChanged.connect(lambda: self.label_ms.setText('{0}ms'.format(self.slider_delay.value())))
        self.input_lb.clicked.connect(lambda: self.slider_delay.setValue(self.slider_delay.value() - 10))
        self.input_rb.clicked.connect(lambda: self.slider_delay.setValue(self.slider_delay.value() + 10))
        # 온라인
        self.cb_online.toggled.connect(self.onlineSignal)
        # 데이터 수정
        self.data_button.clicked.connect(lambda: DataUI(self))
        # 탭
        self.filter_tab_bt.setAutoExclusive(True)
        self.advanced_tab_bt.setAutoExclusive(True)
        self.filter_tab_bt.toggled.connect(self.changeTab)
        # 콜라보
        self.cb_collab.clicked.connect(self.collabSignal)
        self.cb_gg.toggled.connect(lambda: self.collabChildSignal(self.cb_gg))
        self.cb_gc.toggled.connect(lambda: self.collabChildSignal(self.cb_gc))
        self.cb_dm.toggled.connect(lambda: self.collabChildSignal(self.cb_dm))
        self.cb_cy.toggled.connect(lambda: self.collabChildSignal(self.cb_cy))
        self.cb_gf.toggled.connect(lambda: self.collabChildSignal(self.cb_gf))
        self.cb_chu.toggled.connect(lambda: self.collabChildSignal(self.cb_chu))
        # 히스토리
        self.history_button.toggled.connect(self.historySignal)

    # 설정값 가져오기
    def initConfig(self):
        config = configparser.ConfigParser()
        config.read('config.ini')

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
        self.lvl_min.setValue(int(config['FILTER']['min']))
        self.lvl_max.setValue(int(config['FILTER']['max']))
        if config['FILTER']['freestyle'] == '1':
            self.cb_freestyle.setChecked(True)
        else:
            self.cb_online.setChecked(True)
        self.slider_delay.setValue(int(config['ADVANCED']['input_delay']))
        
    # 상단바: 마우스 클릭시 위치 저장
    def mousePressEvent(self, event):
        self.dragPos = event.globalPos()
    
    def lvlChanged(self, lvl, label):
        label.setText(str(lvl.value()))
        if lvl.value() <= 5:
            label.setStyleSheet('color:#f4bb00')
            lvl.setStyleSheet('QSlider::handle:horizontal{background: #f4bb00}')
        elif lvl.value() >= 11:
            label.setStyleSheet('color:#f40052')
            lvl.setStyleSheet('QSlider::handle:horizontal{background: #f40052}')
        else:
            label.setStyleSheet('color:#f45c00')
            lvl.setStyleSheet('QSlider::handle:horizontal{background: #f45c00}')
            
    # 온라인 시그널
    def onlineSignal(self):
        if self.cb_online.isChecked():
            self.lock_bt.move(0,0)
            self.lock_diff.move(0,0)
        else:
            self.lock_bt.move(-370,0)
            self.lock_diff.move(-370,0)

    # 탭 시그널
    def changeTab(self):
        if self.filter_tab_bt.isChecked():
            self.tabWidget.setCurrentIndex(0)
            self.current_tab.setText('FILTER')
        else:
            self.tabWidget.setCurrentIndex(1)
            self.current_tab.setText('ADVANCED')
    
    # 콜라보 시그널
    def collabSignal(self):
        checkboxes = [self.cb_gg, self.cb_gc, self.cb_dm, self.cb_cy, self.cb_gf, self.cb_chu]
        if self.cb_collab.isChecked():
            for i in checkboxes:
                i.setChecked(True)
            self.collab_frame.setStyleSheet('QFrame{\n	background-color: #1e1e1e;\n}')
        else:
            for i in checkboxes:
                i.setChecked(False)
            self.collab_frame.setStyleSheet('QFrame{\n	background-color: rgba(0, 0, 0, 87);\n}')
    
    # 콜라보 하위 시그널
    def collabChildSignal(self, child):
        if child.isChecked():
            self.cb_collab.setChecked(True)
            self.collab_frame.setStyleSheet('QFrame{\n	background-color: #1e1e1e;\n}')
        else:
            if not self.cb_gg.isChecked() and not self.cb_gc.isChecked() and not self.cb_dm.isChecked() \
                and not self.cb_cy.isChecked() and not self.cb_gf.isChecked() and not self.cb_chu.isChecked():
                self.cb_collab.setChecked(False)
                self.collab_frame.setStyleSheet('QFrame{\n	background-color: rgba(0, 0, 0, 87);\n}')

    def historySignal(self):
        if self.history_button.isChecked():
            self.history.show()
            self.history_button.setText('ON')
        else:
            self.history.close()
            self.history_button.setText('OFF')

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
        input_delay = self.slider_delay.value()
        # 모드 선택값
        if self.cb_freestyle.isChecked(): isFreestyle = True
        else: isFreestyle = False

        return fil_bt, fil_st, fil_sr, fil_min, fil_max, input_delay/1000, isFreestyle

    # 무작위 뽑기
    def randomStart(self):
        self.isRunning = True
        bt_list, st_list, sr_list, min_int, max_int, input_delay, isFreestyle = self.filterInputData()
        selected_title, selected_btst, bt_input, init_input, down_input, right_input = \
            sM.selectingMusic(self.yourdata, bt_list, st_list, sr_list, min_int, max_int, isFreestyle)
        print(selected_title, selected_btst)
        if selected_title:
            print('macro activate')
            sM.inputKeyboard(selected_title, bt_input, init_input, down_input, right_input, input_delay, isFreestyle, self.isDebug)
        _str = str(selected_title) + ' / ' + str(selected_btst)
        self.history.history_list.addItem(_str)
        self.isRunning = False
        print('finish')

    # 종료 시 설정값 수정
    def closeEvent(self, event):
        config = configparser.ConfigParser()
        config.read('config.ini')
        _iter = iter(self.values)
        for i in self.checkboxes:
            j = next(_iter)
            if i.isChecked():
                config['FILTER'][j] = '1'
            else:
                config['FILTER'][j] = '0'
        config['FILTER']['min'] = str(self.lvl_min.value())
        config['FILTER']['max'] = str(self.lvl_max.value())
        if self.cb_freestyle.isChecked():
            config['FILTER']['freestyle'] = '1'
        else:
            config['FILTER']['freestyle'] = '0'
        config['ADVANCED']['input_delay'] = str(self.slider_delay.value())
        with open('config.ini', 'w') as configfile:
            config.write(configfile)

            

# 데이터 수정 Dialog
class DataUI(QDialog):
    def __init__(self, parent):
        super(DataUI, self).__init__(parent)
        data_ui = 'modify_data_ui.ui'
        uic.loadUi(data_ui, self)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setWindowModality(Qt.ApplicationModal)
        self.modifyButton.clicked.connect(lambda: self.modifyDataInputData(parent))
        self.cancelButton.clicked.connect(lambda: self.cancelModify(parent))
        parent.lock_all.move(0, 0)

        modify_data_check = set(parent.yourdata['Series'].values)
        self.yd_values = ['TR', 'CE', 'BS', 'VE', 'ES',
                    'T1', 'T2', 'T3', 'GC', 'DM',
                    'CY', 'GF', 'CHU']
        self.yd_checkboxes = [self.yd_cb_tr, self.yd_cb_ce, self.yd_cb_bs, self.yd_cb_ve, self.yd_cb_es,
                    self.yd_cb_t1, self.yd_cb_t2, self.yd_cb_t3, self.yd_cb_gc, self.yd_cb_dm,
                    self.yd_cb_cy, self.yd_cb_gf, self.yd_cb_chu]
        _iter = iter(self.yd_checkboxes)
        for i in self.yd_values:
            j = next(_iter)
            if i in modify_data_check:
                j.setChecked(True)

        self.show()
    
    # 데이터 생성 인풋 데이터 & YourData.csv 생성
    def modifyDataInputData(self, parent):
        fil_yd_sr = set(self.yd_values[i] for i in range(13) if self.yd_checkboxes[i].isChecked())
        fil_yd_sr.add('RP')
        fil_yd_sr.add('P1')
        fil_yd_sr.add('P2')
        fil_yd_sr.add('GG')
        sM.modifyYourData(fil_yd_sr)
        parent.yourdata = sM.readYourData()
        parent.lock_all.move(0, -540)
        self.close()
    
    def cancelModify(self, parent):
        parent.lock_all.move(0, -540)
        self.close()
        
class HistoryUI(QDialog):
    def __init__(self, parent):
        super(HistoryUI, self).__init__(parent)
        history_ui = 'history_ui.ui'
        uic.loadUi(history_ui, self)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.clearButton.clicked.connect(self.history_list.clear)
        self.closeButton.clicked.connect(lambda: parent.history_button.setChecked(False))
        self.aotButton.toggled.connect(self.AlwaysOnTop)

        def moveWindow(event):
            if event.buttons() == Qt.LeftButton:
                self.move(self.pos() + event.globalPos() - self.dragPos)
                self.dragPos = event.globalPos()
                event.accept()
        self.title_bar.mouseMoveEvent = moveWindow
    def mousePressEvent(self, event):
        self.dragPos = event.globalPos()
    
    def AlwaysOnTop(self):
        if self.aotButton.isChecked():
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
            self.show()
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
            self.show()
        


        


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SelectorUI()
    ex.show()
    sys.exit(app.exec_())