import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QSystemTrayIcon
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFontDatabase
import keyboard as kb
import selectMusic as sM
import json
from threading import Thread
from collections import deque

main_ui = uic.loadUiType("selector_ui.ui")[0]

# UI
class SelectorUI(QMainWindow, main_ui):

    # initUI(), readYourData() 실행
    def __init__(self):
        super().__init__()
        self.isRunning = False
        self.isDebug = True
        self.isKeyDebug = True
        self.isInit = True
        self.yourdata = sM.readYourData(self.isDebug)
        self.previous = deque([])

        self.setupUi(self)
        self.history = HistoryUI(self)
        self.initUI()
        self.initSignal()
        self.initConfig()
                
        kb.on_press_key('f7', lambda e: self.canIStart(str(e)), suppress=True)

    # 랜덤 선곡 시작 여부 조사
    def canIStart(self, e):
        if not self.isRunning:
            print('\n\n\n\n\n\nstart')
            thd_rS = Thread(target=self.randomStart)
            thd_rS.start()
        else:
            print('denied')

    # UI 구성
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
        # 탭
        self.filter_tab_bt.toggled.connect(self.changeTab)

        # 레벨
        self.lvl_min.valueChanged.connect(lambda: self.lvlSignal(self.lvl_min, self.label_lvl_min))
        self.lvl_max.valueChanged.connect(lambda: self.lvlSignal(self.lvl_max, self.label_lvl_max))
        self.label_lvl_min.setText(str(self.lvl_min.value()))
        self.label_lvl_max.setText(str(self.lvl_max.value()))
        # 콜라보
        self.cb_collab.clicked.connect(self.collabSignal)
        self.cb_gg.toggled.connect(lambda: self.collabChildSignal(self.cb_gg))
        self.cb_gc.toggled.connect(lambda: self.collabChildSignal(self.cb_gc))
        self.cb_dm.toggled.connect(lambda: self.collabChildSignal(self.cb_dm))
        self.cb_cy.toggled.connect(lambda: self.collabChildSignal(self.cb_cy))
        self.cb_gf.toggled.connect(lambda: self.collabChildSignal(self.cb_gf))
        self.cb_chu.toggled.connect(lambda: self.collabChildSignal(self.cb_chu))
        # 데이터 수정
        self.data_button.clicked.connect(lambda: DataUI(self))

        # 입력 지연
        self.label_ms.setText('{0}ms'.format(self.slider_delay.value()))
        self.slider_delay.valueChanged.connect(lambda: self.label_ms.setText('{0}ms'.format(self.slider_delay.value())))
        self.input_lb.clicked.connect(lambda: self.slider_delay.setValue(self.slider_delay.value() - 10))
        self.input_rb.clicked.connect(lambda: self.slider_delay.setValue(self.slider_delay.value() + 10))
        # 히스토리
        self.history_button.toggled.connect(self.historySignal)
        self.history_scrollbar = self.history.history_list.verticalScrollBar()
        # 중복 방지
        self.label_pre.setText('{0}'.format(self.slider_pre.value()))
        self.slider_pre.valueChanged.connect(lambda: self.label_pre.setText('{0}'.format(self.slider_pre.value())))
        

    # 필터 시그널
    def initSignal(self):
        self.bt_list = set()
        self.st_list = set()
        self.sr_list = set()
        self.min = 1
        self.max = 15
        self.input_delay = 0.03
        self.is_freestyle = True
        # BUTTON TUNES
        self.cb_4b.toggled.connect(lambda: self.isChecked(self.bt_list, self.cb_4b, '4B'))
        self.cb_5b.toggled.connect(lambda: self.isChecked(self.bt_list, self.cb_5b, '5B'))
        self.cb_6b.toggled.connect(lambda: self.isChecked(self.bt_list, self.cb_6b, '6B'))
        self.cb_8b.toggled.connect(lambda: self.isChecked(self.bt_list, self.cb_8b, '8B'))
        # DIFFICULTY
        self.lvl_min.valueChanged.connect(lambda: self.isValueChanged(self.lvl_min))
        self.lvl_max.valueChanged.connect(lambda: self.isValueChanged(self.lvl_max))
        self.cb_nm.toggled.connect(lambda: self.isChecked(self.st_list, self.cb_nm, 'NM'))
        self.cb_hd.toggled.connect(lambda: self.isChecked(self.st_list, self.cb_hd, 'HD'))
        self.cb_mx.toggled.connect(lambda: self.isChecked(self.st_list, self.cb_mx, 'MX'))
        self.cb_sc.toggled.connect(lambda: self.isChecked(self.st_list, self.cb_sc, 'SC'))
        # MODE
        self.cb_freestyle.toggled.connect(self.FSisChecked)
        # CATEGORIES
        self.cb_rp.toggled.connect(lambda: self.isChecked(self.sr_list, self.cb_rp, 'RP'))
        self.cb_p1.toggled.connect(lambda: self.isChecked(self.sr_list, self.cb_p1, 'P1'))
        self.cb_p2.toggled.connect(lambda: self.isChecked(self.sr_list, self.cb_p2, 'P2'))
        self.cb_tr.toggled.connect(lambda: self.isChecked(self.sr_list, self.cb_tr, 'TR'))
        self.cb_ce.toggled.connect(lambda: self.isChecked(self.sr_list, self.cb_ce, 'CE'))
        self.cb_bs.toggled.connect(lambda: self.isChecked(self.sr_list, self.cb_bs, 'BS'))
        self.cb_ve.toggled.connect(lambda: self.isChecked(self.sr_list, self.cb_ve, 'VE'))
        self.cb_es.toggled.connect(lambda: self.isChecked(self.sr_list, self.cb_es, 'ES'))
        self.cb_t1.toggled.connect(lambda: self.isChecked(self.sr_list, self.cb_t1, 'T1'))
        self.cb_t2.toggled.connect(lambda: self.isChecked(self.sr_list, self.cb_t2, 'T2'))
        self.cb_t3.toggled.connect(lambda: self.isChecked(self.sr_list, self.cb_t3, 'T3'))
        self.cb_gg.toggled.connect(lambda: self.isChecked(self.sr_list, self.cb_gg, 'GG'))
        self.cb_gc.toggled.connect(lambda: self.isChecked(self.sr_list, self.cb_gc, 'GC'))
        self.cb_dm.toggled.connect(lambda: self.isChecked(self.sr_list, self.cb_dm, 'DM'))
        self.cb_cy.toggled.connect(lambda: self.isChecked(self.sr_list, self.cb_cy, 'CY'))
        self.cb_gf.toggled.connect(lambda: self.isChecked(self.sr_list, self.cb_gf, 'GF'))
        self.cb_chu.toggled.connect(lambda: self.isChecked(self.sr_list, self.cb_chu, 'CHU'))
        # ADVANCED
        self.slider_delay.valueChanged.connect(lambda: self.isValueChanged(self.slider_delay))
        self.slider_pre.valueChanged.connect(self.previousInitialize)
    
    # 설정값 불러오기
    def initConfig(self):
        if self.isDebug:
            with open('test_config.json', 'r') as f:
                config = json.load(f)
        else:
            with open('config.json', 'r') as f:
                config = json.load(f)

        self.values = ['4B', '5B', '6B', '8B', 'NM', 'HD', 'MX', 'SC',
                'RP', 'P1', 'P2', 'TR', 'CE', 'BS', 'VE', 'ES',
                'T1', 'T2', 'T3', 'GG', 'GC', 'DM', 'CY',
                'GF', 'CHU']
        self.checkboxes = [self.cb_4b, self.cb_5b, self.cb_6b, self.cb_8b, self.cb_nm, self.cb_hd, self.cb_mx, self.cb_sc,
                    self.cb_rp, self.cb_p1, self.cb_p2, self.cb_tr, self.cb_ce, self.cb_bs, self.cb_ve, self.cb_es,
                    self.cb_t1, self.cb_t2, self.cb_t3, self.cb_gg, self.cb_gc, self.cb_dm, self.cb_cy,
                    self.cb_gf, self.cb_chu]

        for i, j in zip(self.values, self.checkboxes):
            if config[i]:
                j.setChecked(True)
        self.lvl_min.setValue(config['MIN'])
        self.lvl_max.setValue(config['MAX'])
        if config['FREESTYLE']:
            self.cb_freestyle.setChecked(True)
        else:
            self.cb_online.setChecked(True)

        self.slider_delay.setValue(config['INPUT DELAY'])

        self.filtering()
        self.slider_pre.setValue(config['PREVIOUS'])

        self.isInit = False
        
    # 상단바: 마우스 클릭시 위치 저장
    def mousePressEvent(self, event):
        self.dragPos = event.globalPos()
    
    # 레벨 시그널
    def lvlSignal(self, lvl, label):
        label.setText(str(lvl.value()))
        if lvl.value() <= 5:
            label.setStyleSheet('color:#f4bb00')
            lvl.setStyleSheet('QSlider::handle:horizontal{background: #f4bb00; font: 9pt "Lato Black"}')
        elif lvl.value() >= 11:
            label.setStyleSheet('color:#f40052')
            lvl.setStyleSheet('QSlider::handle:horizontal{background: #f40052; font: 9pt "Lato Black"}')
        else:
            label.setStyleSheet('color:#f45c00')
            lvl.setStyleSheet('QSlider::handle:horizontal{background: #f45c00; font: 9pt "Lato Black"}')

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
        self.isInit = True
        checkboxes = [self.cb_gg, self.cb_gc, self.cb_dm, self.cb_cy, self.cb_gf, self.cb_chu]
        if self.cb_collab.isChecked():
            for i in checkboxes:
                i.setChecked(True)
            self.collab_frame.setStyleSheet('QFrame{\n	background-color: #1e1e1e;\n}')
        else:
            for i in checkboxes:
                i.setChecked(False)
            self.collab_frame.setStyleSheet('QFrame{\n	background-color: rgba(0, 0, 0, 87);\n}')
        self.isInit = False
        self.filtering()
    
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

    # 히스토리 시그널
    def historySignal(self):
        if self.history_button.isChecked():
            self.history.show()
            self.history_button.setText('ON')
        else:
            self.history.close()
            self.history_button.setText('OFF')

    # 버튼 확인
    def isChecked(self, _list, cb, value):
        if cb.isChecked():
            _list.add(value)
        else:
            _list.discard(value)

        if not self.isInit:
            self.filtering()
            self.previousInitialize()
    
    # 슬라이더 확인
    def isValueChanged(self, slider):
        if slider == self.lvl_min:
            self.min = slider.value()
        elif slider == self.lvl_max:
            self.max = slider.value()
        else:
            self.input_delay = slider.value() / 1000

        if not self.isInit and slider != self.slider_delay:
            self.filtering()
            self.previousInitialize()
            
    # 프리스타일 확인
    def FSisChecked(self):
        if self.cb_freestyle.isChecked():
            self.is_freestyle = True
        else:
            self.is_freestyle = False

        if not self.isInit:
            self.filtering()
            self.previousInitialize()
    
    # 필터링
    def filtering(self):
        self.fil_yourdata, self.fil_list, self.fil_title = \
                sM.filteringMusic(self.yourdata, self.bt_list, self.st_list, self.sr_list, self.min, self.max, self.is_freestyle)
        if self.fil_title:
            self.slider_pre.setMaximum(len(self.fil_title) - 1)
        else:
            self.slider_pre.setMaximum(0)

    # previous 초기화
    def previousInitialize(self):
        if self.previous:
            self.previous = deque([])
            print('initialized')

    # 무작위 뽑기
    def randomStart(self):
        self.isRunning = True
        selected_title, selected_btst, bt_input, init_input, down_input, right_input = \
            sM.selectingMusic(self.yourdata, self.fil_yourdata, self.fil_list, self.is_freestyle, self.previous)
        print(selected_title, ' | ', selected_btst)

        if selected_title:
            print('macro activate')
            sM.inputKeyboard(selected_title, bt_input, init_input, down_input, right_input,
                            self.input_delay, self.is_freestyle, self.isKeyDebug)

            _str = selected_title + '  |  ' + selected_btst
            self.history_scrollbar.setMaximum(self.history_scrollbar.maximum() + 1)
            self.history.history_list.addItem(_str)
            self.history_scrollbar.setValue(self.history_scrollbar.maximum())

            if self.slider_pre.value():
                self.previous.append(selected_title)
                if len(self.previous) > self.slider_pre.value():
                    self.previous.popleft()

        self.isRunning = False
        print('finish')

    # 종료 시 설정값 수정
    def closeEvent(self, event):
        if self.isDebug:
            with open('test_config.json', 'r') as f:
                config = json.load(f)
        else:
            with open('config.json', 'r') as f:
                config = json.load(f)

        for i, j in zip(self.checkboxes, self.values):
            if i.isChecked():
                config[j] = 1
            else:
                config[j] = 0
        config['MIN'] = self.lvl_min.value()
        config['MAX'] = self.lvl_max.value()
        if self.cb_freestyle.isChecked():
            config['FREESTYLE'] = 1
        else:
            config['FREESTYLE'] = 0
        config['INPUT DELAY'] = self.slider_delay.value()
        config['PREVIOUS'] = self.slider_pre.value()

        if self.isDebug:
            with open('test_config.json', 'w') as f:
                json.dump(config, f, indent=4)
        else:
            with open('config.json', 'w') as f:
                json.dump(config, f, indent=4)

            

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
        for i, j in zip(self.yd_values, self.yd_checkboxes):
            if i in modify_data_check:
                j.setChecked(True)

        self.show()
    
    # 데이터 생성 인풋 데이터 & YourData.csv 생성
    def modifyDataInputData(self, parent):
        fil_yd_sr = set(self.yd_values[i] for i in range(13) if self.yd_checkboxes[i].isChecked())
        fil_yd_sr.update(['RP', 'P1', 'P2', 'GG'])
        sM.modifyYourData(fil_yd_sr, parent.isDebug)
        parent.yourdata = sM.readYourData(parent.isDebug)
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