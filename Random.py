import sys
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import keyboard as kb
import selectMusic as sM
main_ui = uic.loadUiType("selector_ui.ui")[0]

# UI
class SelectorUI(QMainWindow, main_ui):

    # initUI(), readYourData() 실행
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUI()
        self.yourdata = sM.readYourData()
        kb.add_hotkey('f7', lambda: self.randomStart(), suppress=True)

    # 시그널, 스타일
    def initUI(self):
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
        self.data_button.clicked.connect(self.clickedData)
        self.filter_tab_bt.setAutoExclusive(True)
        self.advanced_tab_bt.setAutoExclusive(True)
        self.filter_tab_bt.clicked.connect(self.changeTab)
        self.advanced_tab_bt.clicked.connect(self.changeTab)

        self.cb_collab.clicked.connect(self.collabSignal)

    def mousePressEvent(self, event):
        self.dragPos = event.globalPos()
    
    def onlineSignal(self):
        if self.cb_online.isChecked():
            self.bt_groupbox.setEnabled(False)
            self.diff_groupbox.setEnabled(False)
            self.lock_bt.move(0,0)
            self.lock_diff.move(0,0)
        else:
            self.bt_groupbox.setEnabled(True)
            self.diff_groupbox.setEnabled(True)
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
        if self.cb_collab.isChecked():
            self.collab_frame.setEnabled(True)
            self.collab_frame.setStyleSheet('background:#1e1e1e')
        else:
            self.collab_frame.setEnabled(False)
            self.collab_frame.setStyleSheet('background:#181819')

    def clickedData(self):
        DataUI(self)

    # 필터 인풋 데이터
    def filterInputData(self):
        # 버튼 필터
        fil_bt = []
        if self.cb_4b.isChecked(): fil_bt.append(4)
        if self.cb_5b.isChecked(): fil_bt.append(5)
        if self.cb_6b.isChecked(): fil_bt.append(6)
        if self.cb_8b.isChecked(): fil_bt.append(8)
        # 스타일 필터
        fil_st = []
        if self.cb_nm.isChecked(): fil_st.append('NM')
        if self.cb_hd.isChecked(): fil_st.append('HD')
        if self.cb_mx.isChecked(): fil_st.append('MX')
        if self.cb_sc.isChecked(): fil_st.append("SC")
        # 시리즈 필터
        fil_sr = set()
        if self.cb_rp.isChecked(): fil_sr.add('RP')
        if self.cb_p1.isChecked(): fil_sr.add('P1')
        if self.cb_p2.isChecked(): fil_sr.add('P2')
        if self.cb_tr.isChecked(): fil_sr.add("TR")
        if self.cb_ce.isChecked(): fil_sr.add('CE')
        if self.cb_bs.isChecked(): fil_sr.add('BS')
        if self.cb_ve.isChecked(): fil_sr.add('VE')
        if self.cb_es.isChecked(): fil_sr.add("ES")
        if self.cb_t1.isChecked(): fil_sr.add('T1')
        if self.cb_t2.isChecked(): fil_sr.add('T2')
        if self.cb_t3.isChecked(): fil_sr.add('T3')
        if self.cb_collab.isChecked():
            if self.cb_gg.isChecked(): fil_sr.add("GG")
            if self.cb_gc.isChecked(): fil_sr.add('GC')
            if self.cb_dm.isChecked(): fil_sr.add('DM')
            if self.cb_cy.isChecked(): fil_sr.add('CY')
            if self.cb_gf.isChecked(): fil_sr.add("GF")
            if self.cb_chu.isChecked(): fil_sr.add("CHU")
        # 레벨 필터
        fil_min = self.lvl_min.value()
        fil_max = self.lvl_max.value()
        # 입력 지연값
        # input_delay = self.slider_delay.value()
        input_delay = 30
        # 모드 선택값
        if self.cb_freestyle.isChecked():
            isFreestyle = True
        else:
            isFreestyle = False

        return fil_bt, fil_st, fil_sr, fil_min, fil_max, input_delay/1000, isFreestyle
   
    # 무작위 뽑기
    def randomStart(self):
        bt_list, st_list, sr_list, min_int, max_int, input_delay, isFreestyle = self.filterInputData()
        selected_music, bt_input, init_input, down_input, right_input = \
            sM.selectingMusic(self.yourdata, bt_list, st_list, sr_list, min_int, max_int, isFreestyle)
        print(selected_music)
        self.selectedLabel.setText(selected_music)
        if selected_music != 'None':
            sM.inputKeyboard(selected_music, bt_input, init_input, down_input, right_input, input_delay, isFreestyle)




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
        fil_yd_sr = set()
        if self.yd_cb_tr.isChecked(): fil_yd_sr.add("TR")
        if self.yd_cb_ce.isChecked(): fil_yd_sr.add('CE')
        if self.yd_cb_bs.isChecked(): fil_yd_sr.add('BS')
        if self.yd_cb_ve.isChecked(): fil_yd_sr.add('VE')
        if self.yd_cb_es.isChecked(): fil_yd_sr.add("ES")
        if self.yd_cb_t1.isChecked(): fil_yd_sr.add('T1')
        if self.yd_cb_t2.isChecked(): fil_yd_sr.add('T2')
        if self.yd_cb_t3.isChecked(): fil_yd_sr.add('T3')
        if self.yd_cb_gc.isChecked(): fil_yd_sr.add('GC')
        if self.yd_cb_dm.isChecked(): fil_yd_sr.add('DM')
        if self.yd_cb_cy.isChecked(): fil_yd_sr.add('CY')
        if self.yd_cb_gf.isChecked(): fil_yd_sr.add("GF")
        if self.yd_cb_chu.isChecked(): fil_yd_sr.add("CHU")
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