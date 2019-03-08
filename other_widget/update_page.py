# encoding: utf-8

"""
@version: 1.0
@author: WangNing
@license: GUN 
@contact: yogehaoren@gmail.com
@site: 
@software: PyCharm
@file: update_page.py
@time: 2019/3/1 18:48
@describe: 更新数据库页面
"""
import os

from PyQt5.QtWidgets import QWidget, QTextBrowser, QVBoxLayout, QHBoxLayout, QApplication,QScrollBar
from other_widget.common_widget import *
from PyQt5.QtCore import Qt, QTimer, QThread
from PyQt5.QtGui import QIcon
from subprocess import Popen, STARTUPINFO, STARTF_USESHOWWINDOW


class UpdateWidget(QWidget):
    out_edit = None
    close_button = None
    start_button = None
    update_process = None
    listen_thread = None
    listen_thread_flag = False

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("更新资源")
        self.setWindowIcon(QIcon(r'.\images\update.png'))
        self.__ini_ui__()
        self.process_timer = QTimer(self)
        self.process_timer.timeout.connect(self.check_process)  # 计时结束调用operate()方法
        self.process_timer.stop()

    def __ini_ui__(self):

        main_layout = QVBoxLayout()

        self.out_edit = QTextBrowser()
        self.out_edit.setStyleSheet('''
        QTextBrowser{
                        line-height:14px;
                        font-family:microsoft yahei ui,microsoft yahei;
                        font-size:13px;
                    }''')
        self.out_edit.setVerticalScrollBar(QScrollBar())
        main_layout.addWidget(self.out_edit)

        button_layout = QHBoxLayout()
        self.start_button = MyQButton("开始")
        self.start_button.clicked.connect(self.start)
        self.close_button = MyQButton("关闭")
        self.close_button.clicked.connect(self.close_process)
        button_layout.addWidget(self.start_button, 0, Qt.AlignLeft)
        button_layout.addWidget(self.close_button, 0, Qt.AlignRight)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)
        self.resize(700, 500)

    def check_process(self):
        if self.update_process.poll() is None:
            pass
        else:
            self.close_process()

    def start(self):
        if self.update_process is not None and self.update_process.poll() is None:
            return
        file_path = r'E:\mycs\python\scrapyproject\project_av\project_av\log.txt'
        with open(file_path, 'w') as file:
            file.close()
        tools = './tools/VideoUpdate.py'
        cmd = r'E:\mycs\python\env\kivy\Scripts\python.exe ' + os.path.abspath(tools)

        dev_null = open(os.devnull, 'w')
        si = STARTUPINFO()
        si.dwFlags |= STARTF_USESHOWWINDOW
        self.update_process = Popen(cmd, stdout=dev_null, stdin=dev_null, stderr=dev_null, startupinfo=si)
        self.process_timer.start(5000)
        self.listen_thread_flag = False

        self.listen_thread = ListenOut(self.update_process, self.out_edit, self.listen_thread_flag)
        self.listen_thread.start()

    def close_process(self):
        if self.update_process is not None and self.update_process.poll() is None:
            self.update_process.kill()
            self.update_process = None
        self.listen_thread_flag = True
        self.update_process = None
        self.process_timer.stop()

    def closeEvent(self, QCloseEvent):
        """
        窗口关闭前 清理进程
        :param QCloseEvent:
        :return:
        """
        self.close_process()
        if self.listen_thread is not None and not self.listen_thread.isFinished():
            self.listen_thread.terminate()
            self.listen_thread = None
            self.listen_thread_flag = False
        self.out_edit.clear()
        return super().closeEvent(QCloseEvent)


class ListenOut(QThread):

    path = r'E:\mycs\python\scrapyproject\project_av\project_av\log.txt'

    def __init__(self, process, text_browser, flag):
        super().__init__()
        self.process = process
        self.text_browser = text_browser
        self.flag = flag

    def run(self):
        cursor = self.text_browser.textCursor()
        file_num = 0
        with open(self.path, "r", encoding='utf8') as file:
            while True:
                self.sleep(1)
                file.seek(file_num)
                s = file.readline().replace('\n', "")
                file_num = file.tell()
                if s == "":
                    if not self.flag:
                        self.sleep(2)
                        continue
                    else:
                        self.exit()
                self.text_browser.append(s)
                self.text_browser.moveCursor(cursor.End)


class UpdateButton(QLabel):
    """
    更新按钮
    """
    update_widget = None

    def __init__(self, parent):
        super().__init__(parent)

        self.setText("更\n新\n资\n源")
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
        self.update_widget = UpdateWidget(None)
        self.update_widget.setVisible(False)

    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.update_widget.setVisible(not self.update_widget.isVisible())


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    download = UpdateWidget(None)
    download.show()
    sys.exit(app.exec_())