# encoding: utf-8

"""
@version: 1.0
@author: WangNing
@license: GUN 
@contact: yogehaoren@gmail.com
@site: 
@software: PyCharm
@file: config_page.py
@time: 2019/3/1 10:36
@describe: 管理配置界面
"""
from PyQt5.QtWidgets import QLabel, QWidget, QApplication, QVBoxLayout, QHBoxLayout,\
                            QGroupBox, QFormLayout, QLineEdit, QGridLayout, QCheckBox,\
                            QPushButton, QSpinBox, QFileDialog
from PyQt5.QtCore import Qt

from PyQt5.QtGui import QIntValidator, QIcon

from tools.VideoConfigParser import VideoConfigParserClass
from other_widget.common_widget import MyQLineEdit, MyQButton, MyQLabel
from tools.video_api import save_update_message


class ConfigWidget(QWidget):

    db_user_edit = None
    db_password_edit = None
    db_database_edit = None
    image_edit = None
    image_proxy = None
    proxy_ip_edit = None
    proxy_port_edit = None
    aria2c_max_download = None
    aria2c_max_link = None
    aria2c_proxy = None
    aria2c_proxy_ip = None
    aria2c_proxy_port = None
    end_page_edit = None
    start_page_edit = None

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowIcon(QIcon(r'.\images\config.png'))
        self.setWindowTitle("config")
        self.__init_ui()
        self.config = VideoConfigParserClass()
        self.reset_config_value()

    def __init_ui(self):
        """
        初始化界面
        :return:
        """
        main_layout = QVBoxLayout()
        port_validator = QIntValidator(self)
        port_validator.setRange(1, 8888)

        db_group_box = QGroupBox("数据库配置")
        db_group_box.setFlat(False)
        db_layout = QFormLayout()
        self.db_user_edit = MyQLineEdit()
        self.db_password_edit = MyQLineEdit()
        self.db_password_edit.setEchoMode(QLineEdit.Password)
        self.db_database_edit = MyQLineEdit()
        db_layout.addRow("数据库用户", self.db_user_edit)
        db_layout.addRow("数据库密码", self.db_password_edit)
        db_layout.addRow("数据库", self.db_database_edit)
        db_group_box.setLayout(db_layout)

        code_setting_box = QGroupBox("运行环境配置")
        code_layout = QGridLayout()
        image_path = MyQLabel("图片存储位置")
        image_button = MyQButton("...")
        image_button.clicked.connect(self.get_image_dir)
        image_button.setFixedWidth(25)
        self.image_edit = MyQLineEdit()
        image_path.setBuddy(self.image_edit)
        code_layout.addWidget(image_path, 0, 0, 1, 1)
        code_layout.addWidget(image_button, 0, 3, 1, 1)
        code_layout.addWidget(self.image_edit, 0, 1, 1, 2)
        self.image_proxy = QCheckBox("代理")
        self.image_proxy.stateChanged.connect(lambda: self.checkbox_event(self.image_proxy, "m"))
        code_layout.addWidget(self.image_proxy, 1, 0, 1, 1)
        code_setting_box.setLayout(code_layout)
        proxy_ip = MyQLabel("HTTP: ")
        self.proxy_ip_edit = MyQLineEdit()
        self.proxy_ip_edit.setInputMask('000.000.000.000;_')
        proxy_port = MyQLabel("PORT: ")
        self.proxy_port_edit = MyQLineEdit()
        self.proxy_port_edit.setValidator(port_validator)
        code_layout.addWidget(proxy_ip, 2, 0, 1, 1)
        code_layout.addWidget(self.proxy_ip_edit, 2, 1, 1, 3)
        code_layout.addWidget(proxy_port, 3, 0, 1, 1)
        code_layout.addWidget(self.proxy_port_edit, 3, 1, 1, 3)

        aria2c_box = QGroupBox("aria2c配置")
        aria2c_layout = QFormLayout()
        self.aria2c_max_download = QSpinBox()
        self.aria2c_max_download.setRange(1, 200)
        aria2c_layout.addRow("最大下载数", self.aria2c_max_download)
        self.aria2c_max_link = QSpinBox()
        self.aria2c_max_link.setRange(1, 16)
        aria2c_layout.addRow("最大连接数", self.aria2c_max_link)
        self.aria2c_proxy = QCheckBox()
        self.aria2c_proxy.stateChanged.connect(lambda: self.checkbox_event(self.aria2c_proxy, "a"))
        aria2c_layout.addRow("代理  ", self.aria2c_proxy)
        self.aria2c_proxy_ip = MyQLineEdit()
        self.aria2c_proxy_ip.setInputMask('000.000.000.000;_')
        aria2c_layout.addRow("代理 IP", self.aria2c_proxy_ip)
        self.aria2c_proxy_port = MyQLineEdit()
        self.aria2c_proxy_port.setValidator(port_validator)
        aria2c_layout.addRow("代理 PORT", self.aria2c_proxy_port)
        aria2c_box.setLayout(aria2c_layout)

        button_layout = QHBoxLayout()
        save_button = MyQButton("保存")
        save_button.clicked.connect(self.save_config)
        reset_button = MyQButton("重置")
        reset_button.clicked.connect(self.reset_config_value)
        button_layout.addWidget(save_button, Qt.AlignRight)
        button_layout.addWidget(reset_button, Qt.AlignRight)

        update_box = QGroupBox("aria2c配置")
        update_layout = QFormLayout()
        self.start_page_edit = QSpinBox()
        self.start_page_edit.setRange(0, 100)
        self.end_page_edit = QSpinBox()
        self.end_page_edit.setRange(1, 100)
        update_layout.addRow("开始页面", self.start_page_edit)
        update_layout.addRow("结束页面", self.end_page_edit)
        update_box.setLayout(update_layout)

        main_layout.addWidget(db_group_box)
        main_layout.addWidget(code_setting_box)
        main_layout.addWidget(aria2c_box)
        main_layout.addWidget(update_box)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        self.setFixedSize(600, 500)

    def save_config(self):
        """
        保存配置
        :return:
        """
        options_list = list()
        options_list.append(self.db_user_edit.text())
        options_list.append(self.db_password_edit.text())
        options_list.append(self.db_database_edit.text())

        options_list.append(self.image_edit.text())
        options_list.append(str(self.image_proxy.isChecked()))
        options_list.append(self.proxy_ip_edit.text())
        options_list.append(self.proxy_port_edit.text())

        options_list.append(str(self.aria2c_max_download.value()))
        options_list.append(str(self.aria2c_max_link.value()))
        options_list.append(str(self.aria2c_proxy.isChecked()))
        options_list.append(self.aria2c_proxy_ip.text())
        options_list.append(self.aria2c_proxy_port.text())

        start = str(self.start_page_edit.value())
        end = str(self.end_page_edit.value())
        options_list.append(start)
        options_list.append(end)
        self.config.save_all_options(options_list)
        save_update_message({"start": start, "end": end})

        self.close()

    def get_image_dir(self):
        """
        寻找图片文件夹事件
        :return:
        """
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.DirectoryOnly)

        if dlg.exec_():
            image_dir = dlg.selectedFiles()
            self.image_edit.setText(image_dir[0])

    def checkbox_event(self, button, button_type):
        """
        代理按钮 事件
        :param button:
        :param button_type:
        :return:
        """
        if button_type == "m":
            if button.isChecked():
                self.proxy_ip_edit.setEnabled(True)
                self.proxy_port_edit.setEnabled(True)
            else:
                self.proxy_ip_edit.setEnabled(False)
                self.proxy_port_edit.setEnabled(False)
        elif button_type == "a":
            if button.isChecked():
                self.aria2c_proxy_ip.setEnabled(True)
                self.aria2c_proxy_port.setEnabled(True)
            else:
                self.aria2c_proxy_ip.setEnabled(False)
                self.aria2c_proxy_port.setEnabled(False)

    def reset_config_value(self):
        """
        初始化配置数据
        :return:
        """
        user, password, database = self.config.get_db_setting()
        image_path = self.config.get_start_image_path()
        is_proxy, proxy_ip, proxy_port = self.config.get_m3u8_download_setting()
        max_download, max_link, aria2c_is_proxy, aria2c_ip, aria2c_port = self.config.get_aria2c_setting()
        start_page, end_page = self.config.get_update_setting()

        self.db_user_edit.setText(user)
        self.db_password_edit.setText(password)
        self.db_database_edit.setText(database)

        self.image_edit.setText(image_path)
        self.image_edit.scroll(0, 1)
        self.image_proxy.setChecked(is_proxy)
        if not is_proxy:
            self.proxy_ip_edit.setEnabled(False)
            self.proxy_port_edit.setEnabled(False)

        self.proxy_ip_edit.setText(proxy_ip)
        self.proxy_port_edit.setText(proxy_port)

        self.aria2c_max_download.setValue(max_download)
        self.aria2c_max_link.setValue(max_link)
        self.aria2c_proxy.setChecked(aria2c_is_proxy)

        if not aria2c_is_proxy:
            self.aria2c_proxy_ip.setEnabled(False)
            self.aria2c_proxy_port.setEnabled(False)

        self.aria2c_proxy_ip.setText(aria2c_ip)
        self.aria2c_proxy_port.setText(aria2c_port)

        self.start_page_edit.setValue(start_page)
        self.end_page_edit.setValue(end_page)


class ConfigButton(QLabel):
    """
    配置管理按钮
    """
    download_widget = None

    def __init__(self, parent):
        super().__init__(parent)

        self.setText("配\n置\n管\n理")
        self.setWordWrap(True)
        self.setAlignment(Qt.AlignTop)
        q_css = '''QLabel{
                        color:#ffffff;
                        background:#08bb06;
                        border-radius:5px;
                        width:112px;
                        height:35px;
                        font-family:microsoft yahei ui,microsoft yahei;
                        font-size:13px;
                    }
               '''
        self.setStyleSheet(q_css)
        self.config_widget = ConfigWidget(None)
        self.config_widget.setVisible(False)

    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.config_widget.setVisible(not self.config_widget.isVisible())


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    download = ConfigWidget(None)
    download.show()
    sys.exit(app.exec_())