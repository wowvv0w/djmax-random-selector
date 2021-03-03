import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QPushButton, QGroupBox, QCheckBox, \
    QSlider, QGridLayout, QLabel, QMessageBox, QRadioButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import pandas as pd
import random
import keyboard as kb
from string import ascii_letters
import time

# 필요한 메서드 모음
class RandomSelector():

    # 변수 선언
    def __init__(self):

        self.isnt_alphabet = lambda x: x not in ascii_letters
        self.name = ('Title', 'Artist', 'Genre', 'Series', '4BNM', '4BHD', '4BMX', '4BSC',
            '5BNM', '5BHD', '5BMX', '5BSC', '6BNM', '6BHD', '6BMX', '6BSC',
            '8BNM', '8BHD', '8BMX', '8BSC', 'Length')
        self._styles = ('NM', 'HD', 'MX', 'SC')

    # YourData 읽기
    def readYourData(self):

        data = pd.read_csv("YourData.csv", names = self.name)
        # data = pd.read_csv("test_data.csv", names = self.name)

        return data

    # 곡 무작위 선정
    def selectingMusic(self, data, buttons, styles, series, diff_min, diff_max, isFreestyle):

        filtered = data[data['Series'].isin(series)]
        if isFreestyle:
            diff_list = ['{0}B{1}'.format(i, j) for i in buttons for j in styles]
            filtered = filtered.reset_index(drop=True)
            candidate_list = ['{0} {1}'.format(filtered.loc[i, 'Title'], j) for i in range(len(filtered))
                    for j in diff_list if filtered.loc[i, j] >= diff_min and filtered.loc[i, j] <= diff_max]
        else:
            candidate_list = filtered['Title'].tolist()
        

        try:
            selected = random.choice(candidate_list)
        except IndexError:
            return 'None', None, None, None, None


        if self.isnt_alphabet(selected[0]):
            init_input = 'a'
        else:
            init_input = selected[0].lower()

        find_sinit = data['Title'].tolist()
        if self.isnt_alphabet(selected[0]):
            sinit_list = [find_sinit[i] for i in range(len(find_sinit)) if self.isnt_alphabet(find_sinit[i][0])]
        else:
            sinit_list = [find_sinit[i] for i in range(len(find_sinit)) if find_sinit[i][0] == selected[0].lower()
                                                                        or find_sinit[i][0] == selected[0].upper()]
        if isFreestyle:
            down_input = sinit_list.index(selected[:-5])
        else:
            down_input = sinit_list.index(selected)
        

        if isFreestyle:
            bt_input = selected[-4]
            find_btst = ['{0}B{1}'.format(selected[-4], self._styles[i]) for i in range(self._styles.index(selected[-2:]) + 1)]
            find_smusic = filtered[filtered['Title'] == selected[:-5]]
            find_smusic = find_smusic[[*find_btst]]
            find_smusic = find_smusic.values.tolist()[0][:len(find_btst)]
            sub_count = find_smusic.count(0)
            right_input = len(find_btst) - sub_count - 1
        else:
            bt_input, right_input = None, None

        return selected, bt_input, init_input, down_input, right_input

    # 키보드 자동 입력
    def inputKeyboard(self, music, bt, init, down, right, input_delay, isFreestyle):
        
        delay = lambda: time.sleep(input_delay)
        press = lambda key: kb.press_and_release(key)

        if isFreestyle:
            press(bt)
            delay()
        press('page up')
        delay()
        press(init)
        delay()
        if self.isnt_alphabet(music[0]):
            press('page up')
            delay()
            press('page up')
            delay()
            press('page down')
            delay()
        for i in range(down):
            press("down arrow")
            delay()
        if isFreestyle:
            for i in range(right):
                press("right arrow")
                delay()

    # YourData 생성
    def createYourData(self, series):

        data = pd.read_csv("AllTrackData.csv", names = self.name)

        filtered = data[data['Series'].isin(series)]

        filtered = self.specialMusicFilter(filtered, series)
        
        filtered.to_csv("YourData.csv", index=None, header=None)
        # filtered.to_csv("test_data.csv", index=None, header=None)
    
    def specialMusicFilter(self, df, series):

        # RP in DLC 삭제 조건
        if not series > {'TR'}:
            df = df.drop(df[df['Title'] == 'Nevermind'].index)
        if not series > {'CE'}:
            df = df.drop(df[df['Title'] == 'Rising The Sonic'].index)
        if not series > {'BS'}:
            df = df.drop(df[df['Title'] == 'ANALYS'].index)
        if not series > {'T1'}:
            df = df.drop(df[df['Title'] == 'Do you want it'].index)
        if not series > {'T2'}:
            df = df.drop(df[df['Title'] == 'End of Mythology'].index)
        if not series > {'T3'}:
            df = df.drop(df[df['Title'] == 'ALiCE'].index)

        # Link Disc 삭제 조건
        if series > {'CE'} and not series > {'BS'} and not series > {'T1'}:
            df = df.drop(df[df['Title'] == 'Here in the Moment ~Extended Mix~'].index)
        if not series > {'CE'} and series > {'BS'} and not series > {'T1'}:
            df = df.drop(df[df['Title'] == 'Airwave ~Extended Mix~'].index)
        if not series > {'CE'} and not series > {'BS'} and series > {'T1'}:
            df = df.drop(df[df['Title'] == 'SON OF SUN ~Extended Mix~'].index)
        
        return df






# UI
class SelectorUI(QWidget, RandomSelector):

    # initUI(), readYourData() 실행
    def __init__(self):
        super().__init__()
        self.initUI()
        self.yourdata = self.readYourData()

    # UI 생성
    def initUI(self):
        layout = QVBoxLayout()

        tabs = QTabWidget()
        tab1 = QWidget()
        tab2 = QWidget()

        tabs.addTab(tab1, 'Filter'); tabs.addTab(tab2, 'Data')

        tab1.layout = QVBoxLayout()
        tab1.layout.addLayout(self.createFilterTab())
        tab1.setLayout(tab1.layout)

        tab2.layout = QVBoxLayout()
        tab2.layout.addLayout(self.createDataTab())
        tab2.setLayout(tab2.layout)

        layout.addWidget(tabs)
        self.setLayout(layout)
        
        self.setWindowTitle('DJMAX RESPECT V MUSIC RANDOM SELECTOR')
        self.setFixedSize(self.sizeHint())
        self.move(300, 300)
        self.setWindowIcon(QIcon('icon.ico'))
        self.show()

        kb.add_hotkey('f7', lambda: self.randomStart(), suppress=True, trigger_on_release=True)

    # 필터 탭 생성
    def createFilterTab(self):
        vbox_l = QVBoxLayout()
        vbox_r = QVBoxLayout()
        hbox = QHBoxLayout()

        startLabel = QLabel('Press F7 to Start Random Selector', self)
        startLabel.setAlignment(Qt.AlignCenter)

        self.selectedLabel = QLabel('', self)
        self.selectedLabel.setAlignment(Qt.AlignCenter)

        vbox_l.addWidget(self.createButtonTunesGroup())
        vbox_l.addWidget(self.createDifficultyGroup())
        vbox_l.addWidget(self.createModeGroup())
        vbox_l.addWidget(self.createInputDelayGroup())
        vbox_l.addWidget(startLabel)
        vbox_l.addWidget(self.selectedLabel)
        vbox_r.addWidget(self.createSeriesGroup())

        hbox.addLayout(vbox_l); hbox.addLayout(vbox_r)

        return hbox

    def createButtonTunesGroup(self):
        self.bt_groupbox = QGroupBox("BUTTON TUNES")

        self.cb_4b = QCheckBox('4B', self); self.cb_5b = QCheckBox('5B', self)
        self.cb_6b = QCheckBox('6B', self); self.cb_8b = QCheckBox('8B', self)

        self.cb_4b.toggle(); self.cb_5b.toggle(); self.cb_6b.toggle(); self.cb_8b.toggle()

        hbox = QHBoxLayout()
        hbox.addWidget(self.cb_4b); hbox.addWidget(self.cb_5b); hbox.addWidget(self.cb_6b); hbox.addWidget(self.cb_8b)

        self.bt_groupbox.setLayout(hbox)

        return self.bt_groupbox

    def createDifficultyGroup(self):
        self.df_groupbox = QGroupBox("DIFFICULTY")

        self.lvl_min = QSlider(Qt.Horizontal, self)
        self.lvl_max = QSlider(Qt.Horizontal, self)
        self.cb_nm = QCheckBox('NORMAL', self); self.cb_hd = QCheckBox('HARD', self)
        self.cb_mx = QCheckBox('MAXIMUM', self); self.cb_sc = QCheckBox('SC', self)

        self.cb_nm.toggle(); self.cb_hd.toggle(); self.cb_mx.toggle(); self.cb_sc.toggle()

        self.lvl_min.setRange(1, 15); self.lvl_max.setRange(1, 15)
        self.lvl_min.setPageStep(1); self.lvl_max.setPageStep(1)
        self.lvl_max.setValue(15)
        self.lvl_min.setTickPosition(2); self.lvl_max.setTickPosition(2)

        self.lvl_min.valueChanged.connect(lambda: label1.setText(str(self.lvl_min.value())))
        self.lvl_max.valueChanged.connect(lambda: label2.setText(str(self.lvl_max.value())))
        label_min = QLabel('MIN', self); label1 = QLabel((str(self.lvl_min.value())), self)
        label_max = QLabel('MAX', self); label2 = QLabel((str(self.lvl_max.value())), self)
        label1.setFixedSize(16, 15); label2.setFixedSize(16, 15)
        label_min.setFixedSize(30, 15); label_max.setFixedSize(30, 15)
        label1.setAlignment(Qt.AlignRight); label2.setAlignment(Qt.AlignRight);
        label_min.setAlignment(Qt.AlignLeft); label_max.setAlignment(Qt.AlignLeft);

        hbox_style = QHBoxLayout()
        hbox_style.addWidget(self.cb_nm); hbox_style.addWidget(self.cb_hd)
        hbox_style.addWidget(self.cb_mx); hbox_style.addWidget(self.cb_sc)

        hbox_min = QHBoxLayout()
        hbox_max = QHBoxLayout()
        vbox = QVBoxLayout()

        hbox_min.addWidget(label_min); hbox_min.addWidget(self.lvl_min); hbox_min.addWidget(label1)
        hbox_max.addWidget(label_max); hbox_max.addWidget(self.lvl_max); hbox_max.addWidget(label2)
        vbox.addLayout(hbox_min); vbox.addLayout(hbox_max); vbox.addLayout(hbox_style)

        self.df_groupbox.setLayout(vbox)
        return self.df_groupbox

    def createSeriesGroup(self):
        groupbox = QGroupBox("CATEGORIES")
        self.gb_collab = QGroupBox("COLLABORATION")
        self.gb_collab.setFlat(True)
        self.gb_collab.setCheckable(True)

        self.cb_rp = QCheckBox('RESPECT', self); self.cb_p1 = QCheckBox('PORTABLE 1', self); self.cb_p2 = QCheckBox('PORTABLE 2', self)
        self.cb_tr = QCheckBox('TRILOGY', self); self.cb_ce = QCheckBox('CLAZZIQUAI', self); self.cb_bs = QCheckBox('BLACK SQUARE', self)
        self.cb_ve = QCheckBox('V EXTENSION', self); self.cb_es = QCheckBox('EMOTIONAL S.', self)
        self.cb_t1 = QCheckBox('TECHNIKA 1', self); self.cb_t2 = QCheckBox('TECHNIKA 2', self); self.cb_t3 = QCheckBox('TECHNIKA 3', self)
        self.cb_gg = QCheckBox('GUILTY GEAR', self); self.cb_gc = QCheckBox('GROOVE COASTER', self); self.cb_dm = QCheckBox('DEEMO', self)
        self.cb_cy = QCheckBox('CYTUS', self); self.cb_gf = QCheckBox("GIRLS' FRONTLINE", self); self.cb_chu = QCheckBox('CHUNITHM', self)

        self.cb_rp.toggle(); self.cb_p1.toggle(); self.cb_p2.toggle()
        self.cb_tr.toggle(); self.cb_ce.toggle(); self.cb_bs.toggle()
        self.cb_ve.toggle(); self.cb_es.toggle()
        self.cb_t1.toggle(); self.cb_t2.toggle(); self.cb_t3.toggle()
        self.cb_gg.toggle(); self.cb_gc.toggle(); self.cb_dm.toggle()
        self.cb_cy.toggle(); self.cb_gf.toggle(); self.cb_chu.toggle()

        vbox = QVBoxLayout()
        vbox_col = QVBoxLayout()
        vbox.addWidget(self.cb_rp); vbox.addWidget(self.cb_p1); vbox.addWidget(self.cb_p2)
        vbox.addWidget(self.cb_tr); vbox.addWidget(self.cb_ce); vbox.addWidget(self.cb_bs)
        vbox.addWidget(self.cb_ve); vbox.addWidget(self.cb_es)
        vbox.addWidget(self.cb_t1); vbox.addWidget(self.cb_t2); vbox.addWidget(self.cb_t3)
        vbox_col.addWidget(self.cb_gg); vbox_col.addWidget(self.cb_gc); vbox_col.addWidget(self.cb_dm)
        vbox_col.addWidget(self.cb_cy); vbox_col.addWidget(self.cb_gf); vbox_col.addWidget(self.cb_chu)

        self.gb_collab.setLayout(vbox_col)
        vbox.addWidget(self.gb_collab)
        groupbox.setLayout(vbox)

        return groupbox

    def createInputDelayGroup(self):
        groupbox = QGroupBox("INPUT DELAY")

        self.slider_delay = QSlider(Qt.Horizontal, self)
        self.slider_delay.setValue(30)
        self.slider_delay.setRange(10, 100)
        self.slider_delay.setTickPosition(2)
        self.slider_delay.setTickInterval(10)
        label_ms = QLabel('{0}ms'.format(self.slider_delay.value()))
        label_ms.setFixedSize(43,15)
        label_ms.setAlignment(Qt.AlignRight)

        self.slider_delay.valueChanged.connect(lambda: label_ms.setText('{0}ms'.format(self.slider_delay.value())))

        hbox = QHBoxLayout()
        vbox = QVBoxLayout()
        hbox.addWidget(self.slider_delay)
        hbox.addWidget(label_ms)

        vbox.addLayout(hbox)
        groupbox.setLayout(vbox)

        return groupbox

    def createModeGroup(self):
        groupbox = QGroupBox('MODE')
        self.cb_freestyle = QRadioButton('FREESTYLE', self)
        self.cb_online = QRadioButton('ONLINE\n(categories filter only)', self)

        self.cb_freestyle.toggle()
        
        self.cb_online.toggled.connect(self.onlineSignal)

        hbox = QHBoxLayout()
        hbox.addWidget(self.cb_freestyle); hbox.addWidget(self.cb_online)

        groupbox.setLayout(hbox)

        return groupbox
    
    def onlineSignal(self):
        if self.cb_online.isChecked():
            self.bt_groupbox.setEnabled(False)
            self.df_groupbox.setEnabled(False)
        else:
            self.bt_groupbox.setEnabled(True)
            self.df_groupbox.setEnabled(True)


    # 데이터 탭 생성
    def createDataTab(self):
        
        how2use = QLabel("Select Your Own DLCs and Press 'Create'\n\nDo it at initial execution or when you purchase new DLC")
        how2use.setAlignment(Qt.AlignCenter)
        self.yd_cb_tr = QCheckBox('TRILOGY', self); self.yd_cb_ce = QCheckBox('CLAZZIQUAI', self); self.yd_cb_bs = QCheckBox('BLACK SQUARE', self)
        self.yd_cb_ve = QCheckBox('V EXTENSION', self); self.yd_cb_es = QCheckBox('EMOTIONAL S.', self)
        self.yd_cb_t1 = QCheckBox('TECHNIKA 1', self); self.yd_cb_t2 = QCheckBox('TECHNIKA 2', self); self.yd_cb_t3 = QCheckBox('TECHNIKA 3', self)
        self.yd_cb_gc = QCheckBox('GROOVE COASTER', self); self.yd_cb_dm = QCheckBox('DEEMO', self)
        self.yd_cb_cy = QCheckBox('CYTUS', self); self.yd_cb_gf = QCheckBox("GIRLS' FRONTLINE", self); self.yd_cb_chu = QCheckBox('CHUNITHM', self)
        createButton = QPushButton('Create', self)
        createButton.setFixedHeight(50)

        createButton.clicked.connect(self.createDataInputData)

        vbox = QVBoxLayout()
        grid = QGridLayout()
        
        grid.addWidget(self.yd_cb_tr, 0, 0); grid.addWidget(self.yd_cb_ce, 0, 1); grid.addWidget(self.yd_cb_bs, 0, 2)
        grid.addWidget(self.yd_cb_ve, 1, 0); grid.addWidget(self.yd_cb_es, 1, 1); grid.addWidget(self.yd_cb_t1, 1, 2)
        grid.addWidget(self.yd_cb_t2, 2, 0); grid.addWidget(self.yd_cb_t3, 2, 1); grid.addWidget(self.yd_cb_gc, 2, 2)
        grid.addWidget(self.yd_cb_dm, 3, 0); grid.addWidget(self.yd_cb_cy, 3, 1); grid.addWidget(self.yd_cb_gf, 3, 2)
        grid.addWidget(self.yd_cb_chu,4, 0)

        vbox.addStretch(5)
        vbox.addWidget(how2use)
        vbox.addStretch(2)
        vbox.addLayout(grid)
        vbox.addStretch(2)
        vbox.addWidget(createButton)
        vbox.addStretch(5)

        return vbox

    # 필터 인풋 데이터
    def filterInputData(self):
        # 버튼 필터
        fil_bt = []
        if self.cb_4b.isChecked():
            fil_bt.append(4)
        if self.cb_5b.isChecked():
            fil_bt.append(5)
        if self.cb_6b.isChecked():
            fil_bt.append(6)
        if self.cb_8b.isChecked():
            fil_bt.append(8)

        # 스타일 필터
        fil_st = []
        if self.cb_nm.isChecked():
            fil_st.append('NM')
        if self.cb_hd.isChecked():
            fil_st.append('HD')
        if self.cb_mx.isChecked():
            fil_st.append('MX')
        if self.cb_sc.isChecked():
            fil_st.append("SC")

        # 시리즈 필터
        fil_sr = set()
        if self.cb_rp.isChecked():
            fil_sr.add('RP')
        if self.cb_p1.isChecked():
            fil_sr.add('P1')
        if self.cb_p2.isChecked():
            fil_sr.add('P2')
        if self.cb_tr.isChecked():
            fil_sr.add("TR")
        if self.cb_ce.isChecked():
            fil_sr.add('CE')
        if self.cb_bs.isChecked():
            fil_sr.add('BS')
        if self.cb_ve.isChecked():
            fil_sr.add('VE')
        if self.cb_es.isChecked():
            fil_sr.add("ES")
        if self.cb_t1.isChecked():
            fil_sr.add('T1')
        if self.cb_t2.isChecked():
            fil_sr.add('T2')
        if self.cb_t3.isChecked():
            fil_sr.add('T3')
        if self.gb_collab.isChecked():
            if self.cb_gg.isChecked():
                fil_sr.add("GG")
            if self.cb_gc.isChecked():
                fil_sr.add('GC')
            if self.cb_dm.isChecked():
                fil_sr.add('DM')
            if self.cb_cy.isChecked():
                fil_sr.add('CY')
            if self.cb_gf.isChecked():
                fil_sr.add("GF")
            if self.cb_chu.isChecked():
                fil_sr.add("CHU")

        # 레벨 필터
        fil_min = self.lvl_min.value()
        fil_max = self.lvl_max.value()

        # 입력 지연값
        input_delay = self.slider_delay.value()

        # 모드 선택값
        if self.cb_freestyle.isChecked():
            isFreestyle = True
        else:
            isFreestyle = False

        return fil_bt, fil_st, fil_sr, fil_min, fil_max, input_delay/1000, isFreestyle

    # 데이터 생성 인풋 데이터 & YourData.csv 생성
    def createDataInputData(self):
        
        fil_yd_sr = set()
        if self.yd_cb_tr.isChecked():
            fil_yd_sr.add("TR")
        if self.yd_cb_ce.isChecked():
            fil_yd_sr.add('CE')
        if self.yd_cb_bs.isChecked():
            fil_yd_sr.add('BS')
        if self.yd_cb_ve.isChecked():
            fil_yd_sr.add('VE')
        if self.yd_cb_es.isChecked():
            fil_yd_sr.add("ES")
        if self.yd_cb_t1.isChecked():
            fil_yd_sr.add('T1')
        if self.yd_cb_t2.isChecked():
            fil_yd_sr.add('T2')
        if self.yd_cb_t3.isChecked():
            fil_yd_sr.add('T3')
        if self.yd_cb_gc.isChecked():
            fil_yd_sr.add('GC')
        if self.yd_cb_dm.isChecked():
            fil_yd_sr.add('DM')
        if self.yd_cb_cy.isChecked():
            fil_yd_sr.add('CY')
        if self.yd_cb_gf.isChecked():
            fil_yd_sr.add("GF")
        if self.yd_cb_chu.isChecked():
            fil_yd_sr.add("CHU")

        fil_yd_sr.add('RP')
        fil_yd_sr.add('P1')
        fil_yd_sr.add('P2')
        fil_yd_sr.add('GG')
        
        self.createYourData(fil_yd_sr)

        msgBox = QMessageBox.information(self, ' ', 'Success!')
        
    # 무작위 뽑기
    def randomStart(self):
        bt_list, st_list, sr_list, min_int, max_int, input_delay, isFreestyle = self.filterInputData()
        selected_music, bt_input, init_input, down_input, right_input = \
            self.selectingMusic(self.yourdata, bt_list, st_list, sr_list, min_int, max_int, isFreestyle)
        print(selected_music)
        self.selectedLabel.setText(selected_music)
        if selected_music != 'None':
            self.inputKeyboard(selected_music, bt_input, init_input, down_input, right_input, input_delay, isFreestyle)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SelectorUI()
    sys.exit(app.exec_())