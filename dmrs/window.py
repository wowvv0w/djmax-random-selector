from PyQt5 import uic
from PyQt5.QtWidgets import QCheckBox, QDialog, QSizePolicy, QSpacerItem, QVBoxLayout
from PyQt5.QtCore import Qt
from .data import edit_data, read_data, generate_title_list, update_database

SETTING_UI = './ui/setting.ui'
HISTORY_UI = './ui/history.ui'
FAVORITE_UI = './ui/favorite.ui'

class SettingUi(QDialog):
    """
    SETTING Window
    """

    def __init__(self, parent):

        super().__init__(parent)
        uic.loadUi(SETTING_UI, self)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setWindowModality(Qt.ApplicationModal)
        self.apply_button.clicked.connect(lambda: self.modify_data(parent))
        self.cancel_button.clicked.connect(lambda: self.cancel(parent))

        self.current_ver, self.lastest_ver = parent.db_curr_ver, parent.db_last_ver
        self.current_label.setText(f'Current: {self.current_ver}')
        self.lastest_label.setText(f'Lastest: {self.lastest_ver}')
        if self.current_ver < self.lastest_ver:
            self.lastest_label.setStyleSheet('color: #ffbe00;\nfont: 15px')
        else:
            self.lastest_label.setStyleSheet('color: #dddddd;\nfont: 15px')

        self.yd_values = ['P3', 'TR', 'CE', 'BS', 'VE',
                          'ES', 'T1', 'T2', 'T3', 'GC',
                          'DM', 'CY', 'GF', 'CHU']
        self.yd_checkboxes = [self.yd_cb_p3, self.yd_cb_tr, self.yd_cb_ce, self.yd_cb_bs, self.yd_cb_ve,
                              self.yd_cb_es, self.yd_cb_t1, self.yd_cb_t2, self.yd_cb_t3, self.yd_cb_gc,
                              self.yd_cb_dm, self.yd_cb_cy, self.yd_cb_gf, self.yd_cb_chu]

    def show_setting_ui(self, parent):
        """
        Shows 'SETTING' window.
        """

        parent.lock_all.move(0, 0)

        modify_data_check = set(parent.yourdata['Series'].values)

        for i, j in zip(self.yd_values, self.yd_checkboxes):
            j.setChecked(i in modify_data_check)

        self.show()

    def modify_data(self, parent):
        """
        Modifies data.
        """

        if self.current_ver < self.lastest_ver:
            update_database()

        fil_yd_sr = set(val for val, cb in zip(self.yd_values, self.yd_checkboxes) if cb.isChecked())
        fil_yd_sr.update(['RP', 'P1', 'P2', 'GG'])
        edit_data(fil_yd_sr, parent.IS_TEST)
        parent.yourdata = read_data(parent.IS_TEST)

        enabled_check = set(parent.yourdata['Series'].values)
        for val, cb, lck in zip(parent.values[9:], parent.checkboxes[9:], parent.locks[9:]):
            try:
                if val in enabled_check:
                    cb.setEnabled(True)
                    if lck in parent.locks_left_check:
                        lck.move(-20, lck.y())
                    else:
                        lck.move(300, lck.y())

                else:
                    cb.setEnabled(False)
                    if lck in parent.locks_left_check:
                        lck.move(70, lck.y())
                    else:
                        lck.move(210, lck.y())
            except AttributeError:
                pass

        parent.lock_all.move(0, -540)
        parent.filtering()
        parent.erm_initialize()
        self.close()

    def cancel(self, parent):
        """
        Cancels modifying and closes window.
        """

        parent.lock_all.move(0, -540)
        self.close()




class HistoryUi(QDialog):
    """
    History Window
    """

    def __init__(self, parent):

        super().__init__(parent)
        uic.loadUi(HISTORY_UI, self)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.clear_button.clicked.connect(self.history_list.clear)
        self.close_button.clicked.connect(lambda: parent.history_button.setChecked(False))
        self.aot_button.toggled.connect(self.always_on_top)

        def move_window(event):
            if event.buttons() == Qt.LeftButton:
                self.move(self.pos() + event.globalPos() - self.drag_pos)
                self.drag_pos = event.globalPos()
                event.accept()
        self.title_bar.mouseMoveEvent = move_window

    def mousePressEvent(self, event):
        self.drag_pos = event.globalPos()

    def always_on_top(self):
        """
        Sets window staying on top or not.
        """

        if self.aot_button.isChecked():
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
            self.show()
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
            self.show()




class FavoriteUi(QDialog):
    """
    Favorite Window
    """

    def __init__(self, parent):
        super().__init__(parent)
        uic.loadUi(FAVORITE_UI, self)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setWindowModality(Qt.ApplicationModal)
        self.apply_button.clicked.connect(lambda: self.apply(parent))
        self.cancel_button.clicked.connect(lambda: self.cancel(parent))
        self.favor_search.textChanged.connect(self.update_display)
        self.favor_all.clicked.connect(self.update_abled)
        self.favor_ena.clicked.connect(self.update_abled)
        self.favor_dis.clicked.connect(self.update_abled)

        self.controls_layout = QVBoxLayout()
        all_track_title = generate_title_list()
        self.widgets = []

        self.show_enabled = True
        self.show_disabled = True

        for name in all_track_title:
            item = QCheckBox(text=name)
            self.controls_layout.addWidget(item)
            self.widgets.append(item)
        
        spacer = QSpacerItem(1, 1, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.controls_layout.addItem(spacer)
        self.favor_list.setLayout(self.controls_layout)

    
    def show_favorite_ui(self, parent):
        """
        Shows 'FAVORITE' window.
        """

        parent.lock_all.move(0, 0)
        
        for widget in self.widgets:
            widget.setChecked(widget.text() in parent.favorite)
        self.favor_black.setChecked(parent.is_favor_black)
        self.update_display(self.favor_search.text())

        self.show()

    def update_display(self, text):
        """
        Shows search results.
        """

        for widget in self.widgets:
            check = (widget.isChecked() and self.show_enabled) \
                or (not widget.isChecked() and self.show_disabled)
            if check:
                title = widget.text()
                if text.lower() in title.lower():
                    widget.setVisible(True)
                else:
                    widget.setVisible(False)
            else:
                widget.setVisible(False)
            
            
    def update_abled(self):
        """
        Applies on/off filter.
        """

        if self.favor_all.isChecked():
            self.show_enabled, self.show_disabled = True, True
        else:
            self.show_enabled = self.favor_ena.isChecked()
            self.show_disabled = self.favor_dis.isChecked()
        self.update_display(self.favor_search.text())
        
    
    def apply(self, parent):
        """

        """
       
        parent.favorite = {widget.text() for widget in self.widgets if widget.isChecked()}
        parent.is_favor_black = self.favor_black.isChecked()
        print(parent.favorite)
        parent.lock_all.move(0, -540)
        parent.filtering()
        parent.erm_initialize()
        self.close()

    def cancel(self, parent):
        """
        Cancels editing and closes window.
        """

        parent.lock_all.move(0, -540)
        self.close()
