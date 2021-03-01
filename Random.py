import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QPushButton, QGroupBox, QCheckBox, \
    QSlider, QGridLayout, QLabel, QMessageBox
from PyQt5.QtCore import Qt
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

        return data

    # 곡 무작위 선정
    def selectingMusic(self, data, buttons, styles, series, diff_min, diff_max):

        diff_list = ['{0}B{1}'.format(i, j) for i in buttons for j in styles]

        filtered = data[data['Series'].isin(series)]
        filtered = filtered.reset_index(drop=True)
        candidate_list = ['{0} {1}'.format(filtered.loc[i, 'Title'], j) for i in range(len(filtered))
                for j in diff_list if filtered.loc[i, j] >= diff_min and filtered.loc[i, j] <= diff_max]
        
        selected = random.choice(candidate_list)

        bt_input = selected[-4]

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
        down_input = sinit_list.index(selected[:-5])

        find_btst = ['{0}B{1}'.format(selected[-4], self._styles[i]) for i in range(self._styles.index(selected[-2:]) + 1)]
        find_smusic = filtered[filtered['Title'] == selected[:-5]]
        find_smusic = find_smusic[[*find_btst]]
        find_smusic = find_smusic.values.tolist()[0][:len(find_btst)]
        sub_count = find_smusic.count(0)
        right_input = len(find_btst) - sub_count - 1

        return selected, bt_input, init_input, down_input, right_input

    # 키보드 자동 입력
    def inputKeyboard(self, music, bt, init, down, right):

        kb.press_and_release(bt)
        time.sleep(.03)
        kb.press_and_release(init)
        time.sleep(.03)
        if self.isnt_alphabet(music[0]):
            kb.press_and_release('page up')
            time.sleep(.03)
            kb.press_and_release('page up')
            time.sleep(.03)
            kb.press_and_release('page down')
            time.sleep(.03)
        for i in range(down):
            kb.press_and_release("down arrow")
            time.sleep(.03)
        for i in range(right):
            kb.press_and_release("right arrow")
            time.sleep(.03)

    # YourData 생성
    def createYourData(self, series):

        data = pd.read_csv("AllTrackData.csv", names = self.name)

        filtered = data[data['Series'].isin(series)]

        filtered = self.specialMusicFilter(filtered, series)
        
        filtered.to_csv("YourData.csv", index=None, header=None)
        # filtered.to_csv("text_data.csv", index=None, header=None)
    
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

        tabs.addTab(tab1, '필터'); tabs.addTab(tab2, '데이터')

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
        self.show()

        kb.add_hotkey('f7', lambda: self.randomStart(), suppress=True, trigger_on_release=True)

    # 필터 탭 생성
    def createFilterTab(self):
        vbox_l = QVBoxLayout()
        vbox_r = QVBoxLayout()
        hbox = QHBoxLayout()

        startLabel = QLabel('Press F7 to Start Random Selector', self)
        startLabel.setAlignment(Qt.AlignCenter)

        vbox_l.addWidget(self.createButtonTunesGroup())
        vbox_l.addWidget(self.createDifficultyGroup())
        vbox_l.addWidget(startLabel)
        vbox_r.addWidget(self.createSeriesGroup())

        hbox.addLayout(vbox_l); hbox.addLayout(vbox_r)

        return hbox

    def createButtonTunesGroup(self):
        groupbox = QGroupBox("BUTTON TUNES")

        self.cb_4b = QCheckBox('4B', self); self.cb_5b = QCheckBox('5B', self)
        self.cb_6b = QCheckBox('6B', self); self.cb_8b = QCheckBox('8B', self)

        self.cb_4b.toggle(); self.cb_5b.toggle(); self.cb_6b.toggle(); self.cb_8b.toggle()

        hbox = QHBoxLayout()
        hbox.addWidget(self.cb_4b); hbox.addWidget(self.cb_5b); hbox.addWidget(self.cb_6b); hbox.addWidget(self.cb_8b)

        groupbox.setLayout(hbox)

        return groupbox

    def createDifficultyGroup(self):
        groupbox = QGroupBox("DIFFICULTY")

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
        label1.setMinimumWidth(20); label2.setMinimumWidth(20)

        hbox_style = QHBoxLayout()
        hbox_style.addWidget(self.cb_nm); hbox_style.addWidget(self.cb_hd)
        hbox_style.addWidget(self.cb_mx); hbox_style.addWidget(self.cb_sc)

        hbox_min = QHBoxLayout()
        hbox_max = QHBoxLayout()
        vbox = QVBoxLayout()

        hbox_min.addWidget(label_min); hbox_min.addWidget(self.lvl_min); hbox_min.addWidget(label1)
        hbox_max.addWidget(label_max); hbox_max.addWidget(self.lvl_max); hbox_max.addWidget(label2)
        vbox.addLayout(hbox_min); vbox.addLayout(hbox_max); vbox.addLayout(hbox_style)

        groupbox.setLayout(vbox)
        return groupbox

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

    # 데이터 탭 생성
    def createDataTab(self):
        
        how2use = QLabel("가지고 있는 DLC를 선택한 후 'Create' 버튼을 눌러주세요.")
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

        return fil_bt, fil_st, fil_sr, fil_min, fil_max

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
        bt_list, st_list, sr_list, min_int, max_int = self.filterInputData()
        try:
            if len(bt_list) == 0:
                raise ButtonTunesError
            if min_int > max_int:
                raise MinMaxError
            if len(st_list) == 0:
                raise StyleError
            if len(sr_list) == 0:
                raise SeriesError
            selected_music, bt_input, init_input, down_input, right_input = \
                self.selectingMusic(self.yourdata, bt_list, st_list, sr_list, min_int, max_int)
            print(selected_music)
            self.inputKeyboard(selected_music, bt_input, init_input, down_input, right_input)
        except Exception as e:
            print('오류:', e)



# 에러 메세지 모음
class ButtonTunesError(Exception):
    def __init__(self):
        super().__init__('선택된 버튼이 없습니다.')

class MinMaxError(Exception):
    def __init__(self):
        super().__init__('최소 난이도가 최대 난이도보다 큽니다.')

class StyleError(Exception):
    def __init__(self):
        super().__init__('선택된 난이도가 없습니다.')

class SeriesError(Exception):
    def __init__(self):
        super().__init__('선택된 카테고리가 없습니다.')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SelectorUI()
    sys.exit(app.exec_())