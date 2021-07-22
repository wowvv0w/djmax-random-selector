import sys
import webbrowser
from threading import Thread
from collections import deque
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QSystemTrayIcon
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFontDatabase
import keyboard as kb
import dmrs


class SelectorUi(QMainWindow):

    # You can change these constants when you test codes.
    IS_TEST = False  # Use test csv and config
    IS_KEY_TEST = False  # Ignore `dmrs.select_music`

    def __init__(self):

        super().__init__()
        uic.loadUi("./ui/selector.ui", self)
        # Selector
        self.is_running = False
        self.is_init = False
        # Data
        self.yourdata = dmrs.read_data(self.IS_TEST)
        if self.IS_TEST:
            self.config = dmrs.TEST_CONFIG
        else:
            self.config = dmrs.YOUR_CONFIG
        # Update Check
        self.rs_curr_ver, self.rs_last_ver, \
            self.db_curr_ver, self.db_last_ver = dmrs.update_check()
        # Filter
        self.bt_list = set()
        self.st_list = set()
        self.sr_list = set()
        self.min = 1
        self.max = 15
        self.prefer = None
        self.is_freestyle = True
        # Advanced
        self.previous = deque([])
        self.pre_cnt = 0
        self.pre_is_under = True
        self.is_tray = False
        self.input_delay = 0.03
        self.auto_start = False
        self.favorite = set()
        self.is_favor = False
        self.is_favor_black = False
        # Filtered Data
        self.fil_yourdata = None
        self.fil_list = None
        self.fil_total = None
        # Ui
        self.setting_ui = dmrs.SettingUi(self)
        self.history_ui = dmrs.HistoryUi(self)
        self.favorite_ui = dmrs.FavoriteUi(self)
        self.preset_ui = dmrs.PresetUi(self)
        # Signals
        self.collab_children = {self.cb_gg, self.cb_gc, self.cb_dm, self.cb_cy, self.cb_gf, self.cb_chu, self.cb_esti}
        self.ui_signal()
        self.filter_signal()
        # Configuration
        self.btn_diff = [
            ('4B', self.cb_4b), ('5B', self.cb_5b), ('6B', self.cb_6b), ('8B', self.cb_8b),
            ('NM', self.cb_nm), ('HD', self.cb_hd), ('MX', self.cb_mx), ('SC', self.cb_sc)
            ]
        self.categories = [
            ('RP', self.cb_rp, self.lock___), ('P1', self.cb_p1, self.lock___),
            ('P2', self.cb_p2, self.lock___), ('P3', self.cb_p3, self.lock_p3),
            ('TR', self.cb_tr, self.lock_tr), ('CE', self.cb_ce, self.lock_ce),
            ('BS', self.cb_bs, self.lock_bs), ('VE', self.cb_ve, self.lock_ve),
            ('ES', self.cb_es, self.lock_es), ('T1', self.cb_t1, self.lock_t1),
            ('T2', self.cb_t2, self.lock_t2), ('T3', self.cb_t3, self.lock_t3),
            ('GG', self.cb_gg, self.lock___), ('GC', self.cb_gc, self.lock_gc),
            ('DM', self.cb_dm, self.lock_dm), ('CY', self.cb_cy, self.lock_cy),
            ('GF', self.cb_gf, self.lock_gf), ('CHU', self.cb_chu, self.lock_chu),
            ('ESTI', self.cb_esti, self.lock_esti)
            ]
        self.enabled_check = set(self.yourdata['Series'].values)
        dmrs.import_config(self, self.config, True)
        dmrs.lock_series(self.categories, self.enabled_check)
        # Hotkey
        kb.add_hotkey('f7', self.check_state, suppress=True)
        # Others


    def check_state(self):

        if not self.is_running:
            print('start')
            thd_rs = Thread(target=self.random_start)
            thd_rs.start()
        else:
            print('denied')

    def random_start(self):

        self.is_running = True

        if self.erm_slider.value() < len(self.previous):
            self.update_previous()
        
        picked_title, picked_btst, check_list, input_list = \
            dmrs.pick_music(
                self.yourdata, self.fil_yourdata, self.fil_list,
                self.prefer, self.is_freestyle, self.previous, self.auto_start
                )
        print(picked_title, ' | ', picked_btst)

        if picked_title:
            print('macro activate')
            if not self.IS_KEY_TEST:
                dmrs.select_music(self.input_delay, check_list, input_list)

            _str = picked_title + '  |  ' + picked_btst
            self.history_scrollbar.setMaximum(self.history_scrollbar.maximum() + 1)
            self.history_ui.history_list.addItem(_str)
            self.history_scrollbar.setValue(self.history_scrollbar.maximum())

            self.update_previous(title=picked_title)

        self.is_running = False
        print('finish')


    def ui_signal(self):

        # FontDB
        self.fontDB = QFontDatabase()
        self.fontDB.addApplicationFont('./fonts/Lato-Black.ttf')
        self.fontDB.addApplicationFont('./fonts/Lato-Bold.ttf')
        self.fontDB.addApplicationFont('./fonts/Lato-Light.ttf')
        self.fontDB.addApplicationFont('./fonts/Lato-Regular.ttf')
        self.fontDB.addApplicationFont('./fonts/Lato-Thin.ttf')
        # Window
        self.setWindowIcon(QIcon('./images/icon.ico'))
        self.setWindowFlags(Qt.FramelessWindowHint)
        # System tray
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(QIcon('./images/icon.ico'))
        self.tray.activated.connect(self.show)
        self.tray.activated.connect(self.tray.hide)
        self.tray.hide()
        # Top bar
        self.minimize_button.clicked.connect(self.minimize_signal)
        self.close_button.clicked.connect(self.close)
        self.update_button.clicked.connect(lambda: webbrowser.open('https://github.com/wowvv0w/DJMAX_Random_Selector/releases'))
        if self.rs_curr_ver >= self.rs_last_ver:
            self.update_button.setVisible(False)
        def move_window(event):
            if event.buttons() == Qt.LeftButton:
                self.move(self.pos() + event.globalPos() - self.drag_pos)
                self.drag_pos = event.globalPos()
                event.accept()
        self.title_bar.mouseMoveEvent = move_window
        # Tab
        self.filter_tab_bt.toggled.connect(self.tab_signal)

        # Level
        self.lvl_min.valueChanged.connect(lambda: self.lvl_signal(self.lvl_min))
        self.lvl_max.valueChanged.connect(lambda: self.lvl_signal(self.lvl_max))
        # Collaboration
        self.cb_collab.clicked.connect(self.collab_signal)
        self.cb_gg.toggled.connect(lambda: self.collab_child_signal(self.cb_gg))
        self.cb_gc.toggled.connect(lambda: self.collab_child_signal(self.cb_gc))
        self.cb_dm.toggled.connect(lambda: self.collab_child_signal(self.cb_dm))
        self.cb_cy.toggled.connect(lambda: self.collab_child_signal(self.cb_cy))
        self.cb_gf.toggled.connect(lambda: self.collab_child_signal(self.cb_gf))
        self.cb_chu.toggled.connect(lambda: self.collab_child_signal(self.cb_chu))
        self.cb_esti.toggled.connect(lambda: self.collab_child_signal(self.cb_esti))
        # Bottom Bar
        if self.db_curr_ver < self.db_last_ver:
            self.setting_button.setIcon(QIcon('./images/setting_update.png'))
        self.setting_button.clicked.connect(self.setting_ui.show)
        self.preset_button.clicked.connect(self.preset_ui.show)

        # Input delay
        self.delay_ms.setText(f'{self.delay_slider.value()}ms')
        self.delay_slider.valueChanged.connect(
            lambda: self.delay_ms.setText(f'{self.delay_slider.value()}ms'))
        self.delay_lb.clicked.connect(
            lambda: self.delay_slider.setValue(self.delay_slider.value() - 10))
        self.delay_rb.clicked.connect(
            lambda: self.delay_slider.setValue(self.delay_slider.value() + 10))
        # Auto Start
        self.autostart_button.toggled.connect(self.auto_start_signal)
        # History
        self.history_button.toggled.connect(self.history_signal)
        self.history_scrollbar = \
            self.history_ui.history_list.verticalScrollBar()
        # Exclude recent music (erm)
        self.erm_slider.valueChanged.connect(self.erm_signal)
        # System tray
        self.tray_button.toggled.connect(self.tray_signal)
        # Favorite
        self.favorite_edit.clicked.connect(self.favorite_ui.show)

    def filter_signal(self):
        
        # BUTTON TUNES
        self.cb_4b.toggled.connect(lambda: self.is_checked(self.bt_list, self.cb_4b, '4B'))
        self.cb_5b.toggled.connect(lambda: self.is_checked(self.bt_list, self.cb_5b, '5B'))
        self.cb_6b.toggled.connect(lambda: self.is_checked(self.bt_list, self.cb_6b, '6B'))
        self.cb_8b.toggled.connect(lambda: self.is_checked(self.bt_list, self.cb_8b, '8B'))
        # DIFFICULTY
        self.lvl_min.valueChanged.connect(lambda: self.is_value_changed(self.lvl_min))
        self.lvl_max.valueChanged.connect(lambda: self.is_value_changed(self.lvl_max))
        self.cb_nm.toggled.connect(lambda: self.is_checked(self.st_list, self.cb_nm, 'NM'))
        self.cb_hd.toggled.connect(lambda: self.is_checked(self.st_list, self.cb_hd, 'HD'))
        self.cb_mx.toggled.connect(lambda: self.is_checked(self.st_list, self.cb_mx, 'MX'))
        self.cb_sc.toggled.connect(lambda: self.is_checked(self.st_list, self.cb_sc, 'SC'))
        self.cb_bgn.toggled.connect(self.is_prefer_checked)
        self.cb_mst.toggled.connect(self.is_prefer_checked)
        # MODE
        self.cb_freestyle.toggled.connect(self.is_fs_checked)
        # CATEGORIES
        self.cb_rp.toggled.connect(lambda: self.is_checked(self.sr_list, self.cb_rp, 'RP'))
        self.cb_p1.toggled.connect(lambda: self.is_checked(self.sr_list, self.cb_p1, 'P1'))
        self.cb_p2.toggled.connect(lambda: self.is_checked(self.sr_list, self.cb_p2, 'P2'))
        self.cb_p3.toggled.connect(lambda: self.is_checked(self.sr_list, self.cb_p3, 'P3'))
        self.cb_tr.toggled.connect(lambda: self.is_checked(self.sr_list, self.cb_tr, 'TR'))
        self.cb_ce.toggled.connect(lambda: self.is_checked(self.sr_list, self.cb_ce, 'CE'))
        self.cb_bs.toggled.connect(lambda: self.is_checked(self.sr_list, self.cb_bs, 'BS'))
        self.cb_ve.toggled.connect(lambda: self.is_checked(self.sr_list, self.cb_ve, 'VE'))
        self.cb_es.toggled.connect(lambda: self.is_checked(self.sr_list, self.cb_es, 'ES'))
        self.cb_t1.toggled.connect(lambda: self.is_checked(self.sr_list, self.cb_t1, 'T1'))
        self.cb_t2.toggled.connect(lambda: self.is_checked(self.sr_list, self.cb_t2, 'T2'))
        self.cb_t3.toggled.connect(lambda: self.is_checked(self.sr_list, self.cb_t3, 'T3'))
        self.cb_p3.toggled.connect(lambda: self.is_checked(self.sr_list, self.cb_p3, 'P3'))
        self.cb_gg.toggled.connect(lambda: self.is_checked(self.sr_list, self.cb_gg, 'GG'))
        self.cb_gc.toggled.connect(lambda: self.is_checked(self.sr_list, self.cb_gc, 'GC'))
        self.cb_dm.toggled.connect(lambda: self.is_checked(self.sr_list, self.cb_dm, 'DM'))
        self.cb_cy.toggled.connect(lambda: self.is_checked(self.sr_list, self.cb_cy, 'CY'))
        self.cb_gf.toggled.connect(lambda: self.is_checked(self.sr_list, self.cb_gf, 'GF'))
        self.cb_chu.toggled.connect(lambda: self.is_checked(self.sr_list, self.cb_chu, 'CHU'))
        self.cb_esti.toggled.connect(lambda: self.is_checked(self.sr_list, self.cb_esti, 'ESTI'))
        # ADVANCED
        self.delay_slider.valueChanged.connect(self.is_delay_changed)
        self.favorite_button.toggled.connect(self.favorite_signal)

    def lvl_signal(self, lvl):

        indicators = [None, # <-- remember me, index[0]
            self.d1, self.d2, self.d3, self.d4, self.d5,
            self.d6, self.d7, self.d8, self.d9, self.d10,
            self.d11, self.d12, self.d13, self.d14, self.d15
            ]
        d = lvl.value()
        if lvl == self.lvl_min:
            for i in range(1, d):
                indicators[i].setChecked(False)
            for i in range(d, self.max+1):
                indicators[i].setChecked(True)
            self.lvl_max.setMinimum(d)
        else:
            for i in range(15, d, -1):
                indicators[i].setChecked(False)
            for i in range(d, self.min-1, -1):
                indicators[i].setChecked(True)
            self.lvl_min.setMaximum(d)

    def tab_signal(self, checked):

        if checked:
            self.tabWidget.setCurrentIndex(0)
            self.current_tab.setText('FILTER')
        else:
            self.tabWidget.setCurrentIndex(1)
            self.current_tab.setText('ADVANCED')

    @dmrs.filtering
    def collab_signal(self, checked):

        self.is_init = True
        if checked:
            for i in self.collab_children:
                i.setChecked(True)
            self.collab_frame.setStyleSheet('QFrame{\n	background-color: #1e1e1e;\n}')
        else:
            for i in self.collab_children:
                i.setChecked(False)
            self.collab_frame.setStyleSheet('QFrame{\n	background-color: rgba(0, 0, 0, 87);\n}')
        self.is_init = False

    def collab_child_signal(self, child):

        if child.isChecked():
            self.cb_collab.setChecked(True)
            self.collab_frame.setStyleSheet('QFrame{\n	background-color: #1e1e1e;\n}')
        else:
            check = {cb.isChecked() for cb in self.collab_children if cb.isEnabled()}
            if True not in check:
                self.cb_collab.setChecked(False)
                self.collab_frame.setStyleSheet('QFrame{\n	background-color: rgba(0, 0, 0, 87);\n}')

    def history_signal(self, checked):

        if checked:
            self.history_ui.show()
            self.history_button.setText('ON')
        else:
            self.history_ui.close()
            self.history_button.setText('OFF')

    def minimize_signal(self):

        if self.is_tray:
            self.hide()
            self.tray.show()
        else:
            self.showMinimized()

    def tray_signal(self, checked):

        if checked:
            self.is_tray = True
            self.tray_button.setText('ON')
        else:
            self.is_tray = False
            self.tray_button.setText('OFF')

    def auto_start_signal(self, checked):

        if checked:
            self.auto_start = True
            self.autostart_button.setText('ON')
        else:
            self.auto_start = False
            self.autostart_button.setText('OFF')
    
    @dmrs.filtering
    def favorite_signal(self, checked):

        if checked:
            self.is_favor = True
            self.favorite_button.setText('ON')
        else:
            self.is_favor = False
            self.favorite_button.setText('OFF')

    @dmrs.filtering
    def is_checked(self, list_, obj, value):

        if obj.isChecked():
            list_.add(value)
        else:
            list_.discard(value)

    @dmrs.filtering
    def is_value_changed(self, obj):

        if obj == self.lvl_min:
            self.min = obj.value()
        else:
            self.max = obj.value()

    @dmrs.filtering
    def is_fs_checked(self, checked):

        self.is_freestyle = checked
    
    def is_delay_changed(self, value):

        self.input_delay = value / 1000

    def is_prefer_checked(self):

        if self.cb_bgn.isChecked():
            self.prefer = 'beginner'
        elif self.cb_mst.isChecked():
            self.prefer = 'master'
        else:
            self.prefer = None
    
    def erm_signal(self, value):

        self.erm_num.setText(f'{value}')

        erm = self.erm_slider
        max_ = erm.maximum()

        if self.pre_cnt <= max_:
            self.pre_cnt = value
        else:
            if value == max_:
                pass
            else:
                self.pre_cnt = value


    def update_previous(self, title=None):

        value = self.erm_slider.value()
        if title:
            self.previous.append(title)
        while len(self.previous) > value:
            self.previous.popleft()
        self.pre_cnt = value
        print(self.pre_cnt, self.previous)


    def closeEvent(self, _):
        dmrs.export_config(self, self.config)

    def mousePressEvent(self, event):
        self.drag_pos = event.globalPos()




if __name__ == '__main__':
    app = QApplication(sys.argv)
    selector = SelectorUi()
    selector.show()
    sys.exit(app.exec_())
