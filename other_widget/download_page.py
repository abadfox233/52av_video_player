# encoding: utf-8

"""
@version: 1.0
@author: WangNing
@license: GUN 
@contact: yogehaoren@gmail.com
@site: 
@software: PyCharm
@file: download_page.py
@time: 2019/1/26 14:26下载界面
@describe: 
"""
import sys

from PyQt5.QtWidgets import QWidget, QAction, QPushButton, QLabel, QVBoxLayout, \
    QHBoxLayout, QApplication, QMenu, QScrollArea, QProgressBar, QTextBrowser
from PyQt5.QtCore import QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QCursor, QIcon
import psutil

from tools.video_api import *
from tools import download_m3u8
from tools.VideoConfigParser import VideoConfigParserClass

start_image_path = VideoConfigParserClass.static_get_image_path()


class DownloadWidget(QWidget):

    update_history_signal = pyqtSignal(int)
    scroll = None
    clear_history_button = None
    main_layout = None
    movie_list_widget = None
    download_movie_list = []
    movie_item_widget = []

    def __init__(self, parent):
        super().__init__(parent)
        self.setStyleSheet("""QWidget
                                            {
                                                background-color:#313034;
                                                color:#2c2f34;
                                                font-size:12px;
                                                border:0px solid #423f48;
                                                font: "Tlwg Typo";
                                                margin:0px;
                                            }
                                        """)
        self.setWindowIcon(QIcon(r'.\images\download.png'))
        self.setWindowTitle("download")
        self.init_ui()
        self.update_history()

    def update_history(self, id = 0):
        state = self.isVisible()
        self.setVisible(False)
        for widget in self.movie_item_widget:
            widget.close()
        self.movie_item_widget.clear()
        self.download_movie_list = list(get_download_video())
        self.movie_list_widget.setFixedSize(355, 100*len(self.download_movie_list))
        for i in range(len(self.download_movie_list)):
            widget = DownloadItemWidget(self.movie_list_widget,
                                        self.download_movie_list[i],
                                        self.update_history_signal,
                                        i)
            self.movie_item_widget.append(widget)
            widget.move(0, i*90)
        self.setVisible(state)

    def add_download_movie(self, movie_message):
        state = self.isVisible()
        self.setVisible(False)
        self.download_movie_list.append(movie_message)
        widget = DownloadItemWidget(self.movie_list_widget,
                                    movie_message,
                                    self.update_history_signal,
                                    len(self.download_movie_list) - 1)
        widget.move(0, (len(self.download_movie_list)-1) * 90)
        self.movie_list_widget.setFixedSize(355, 100 * len(self.download_movie_list))
        self.movie_item_widget.append(widget)
        self.setVisible(state)

    def delete_download_movie(self, id):
        state = self.isVisible()
        self.setVisible(False)
        k = 0
        self.movie_item_widget[id].close()
        self.movie_item_widget[id] = None
        for i in range(len(self.download_movie_list)):
            if self.movie_item_widget[i]:
                self.movie_item_widget[i].move(0, k * 90)
                k += 1
        self.movie_list_widget.setFixedSize(355, 100 * k)
        self.setVisible(state)

    def init_ui(self):
        self.main_layout = QVBoxLayout()
        self.scroll = QScrollArea()
        self.main_layout.addWidget(self.scroll)

        self.movie_list_widget = QWidget()

        self.scroll.setWidget(self.movie_list_widget)
        hboxlayout = QHBoxLayout()
        self.clear_history_button = QPushButton("清除历史记录")
        hboxlayout.addWidget(self.clear_history_button, 0, Qt.AlignRight)
        self.main_layout.addLayout(hboxlayout)
        self.setLayout(self.main_layout)
        self.setFixedWidth(400)
        self.setMinimumHeight(550)
        self.update_history_signal.connect(self.update_history)

    def closeEvent(self, QCloseEvent):
        self.setVisible(False)


class DownloadItemWidget(QWidget):

    message_widget = None
    image_label = None
    title_label = None
    statue = None
    process_bar = None
    main_layout = None
    download_process = None
    # 0 -> 未开始下载 1 -> 下载准备 2 -> 下载中 3 -> 下载完成 4 -> 下载错误
    flag = 0
    large = None
    process_timer = None
    menu = None
    parent = None
    # 下载信息 由 download_m3u8.py create_download_message() 生成
    download_message = None
    # 合并线程
    join_thread = None
    # 下载 m3u8 文件
    download_thread = None
    last_num = 0

    def __init__(self, parent, movie_message, update_history_signal, video_id):
        super().__init__(parent)
        self.parent = parent
        self.movie_message = movie_message
        self.init_ui(update_history_signal, video_id)
        self.bind_movie()
        self.process_timer = QTimer(self)
        self.process_timer.timeout.connect(self.get_message)  # 计时结束调用operate()方法
        self.process_timer.stop()
        self.first_count()

    def get_message(self):
        """
        获取下载信息
        :return:
        """
        if self.flag == 1:
            if self.download_process is None:
                self.first_count()
                self.flag = 0
                return
            if self.download_process.poll() is None:
                self.large = self.download_message['file_length'] + 3
                self.flag = 2
        elif self.flag == 2:
            if self.download_process.poll() is None:
                self.count_process()
            else:
                self.flag = 3
        elif self.flag == 3:
            if self.join_thread is None:
                self.statue.setText("开始合并文件")
                self.join_thread = JoinTempFileThread(self.movie_message[2],
                                                      self.large, self.movie_message[1],
                                                      self.movie_message[0])
                self.join_thread.start()
            elif self.join_thread.isFinished():
                update_download_message(self.movie_message[0], 1)
                self.statue.setText("下载完成")
                self.process_bar.setValue(99)
                self.process_timer.stop()

    def count_process(self):
        """
        :return: 计算下载进度
        """
        start = 0
        now = len(os.listdir('./video/' + self.movie_message[0]))
        end = self.large

        # 测试网速
        download_start_byte = 0
        net_speed_message = "%.1f B/秒"
        net_message = psutil.net_io_counters()
        if net_message:
            download_start_byte = net_message.bytes_recv
        net_speed = download_start_byte - self.last_num
        self.last_num = download_start_byte
        if net_speed < 1024:
            net_speed_message = net_speed_message % net_speed
        elif net_speed < 1024 * 1024:
            net_speed_message = "%.1f KB/秒" % (net_speed / 1024)
        else:
            net_speed_message = "%.1f MB/秒" % (net_speed / 1048576)

        percentage = ((now - start) / (end - start))
        self.process_bar.setValue(int(percentage*100))
        s1 = '%d/%d    %d%%    %s' % (now, self.large, int(percentage * 100), net_speed_message)
        self.statue.setText(s1)

    def create_message_widget(self):
        """
        创建文件下载信息界面
        :return:
        """
        if self.message_widget:
            if self.message_widget.isEnabled():
                self.message_widget.show()
                return
        self.message_widget = DownloadMessageWidget(None, self.movie_message)
        self.message_widget.show()

    def init_ui(self, update_history_signal, video_id):
        """
        初始化界面
        :return:
        """

        self.menu = self.DownloadItemMenu(self, self.movie_message, update_history_signal, video_id)
        label_css = 'QLabel{font-family:\"Microsoft YaHei\";font-size:12px;background:transparent;color:#FFFFFF;}'
        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)
        self.image_label = QLabel()
        self.title_label = QLabel()
        self.statue = QLabel()
        self.title_label.setStyleSheet(label_css)
        self.statue.setStyleSheet(label_css)
        self.process_bar = QProgressBar()
        self.process_bar.setFixedHeight(6)
        self.process_bar.setTextVisible(False)
        self.statue.setAlignment(Qt.AlignRight)
        right_layout = QVBoxLayout()
        self.main_layout.addWidget(self.image_label, 0, Qt.AlignLeft)
        right_layout.addWidget(self.title_label)
        right_layout.addWidget(self.statue)
        right_layout.addWidget(self.process_bar)
        self.main_layout.addLayout(right_layout, 2)
        self.setFixedSize(353, 100)

    def bind_movie(self):
        """
            绑定影片
            :return:
        """
        add_x = lambda x: x[0:20]+"\n"+x[20:40]+"\n"+x[40:60]
        title = add_x(self.movie_message[1])
        self.title_label.setText(title)
        pix_image = change_image_size(os.path.join(start_image_path, self.movie_message[5]), 100, 80)
        self.image_label.setPixmap(pix_image)
        self.image_label.resize(pix_image.width(), pix_image.height())
        if self.movie_message[4] == 1:
            self.flag = 3
            self.statue.setText("下载完成")
            self.process_bar.setValue(99)
        else:
            self.flag = 0
            self.statue.setText("开始下载")
            self.process_bar.setValue(0)

    def mousePressEvent(self, QMouseEvent):
        if QMouseEvent.buttons() == Qt.RightButton:
            self.menu.my_custom_context_menu()
        elif QMouseEvent.buttons() == Qt.LeftButton:
            self.process_download()

    def first_count(self):
        try:
            if self.flag == 0:
                now = len(os.listdir('./video/' + self.movie_message[0]))
                if now > 0:
                    self.statue.setText("%d/未知    开始下载" % now)
                    self.process_bar.setValue(30)
        except FileNotFoundError:
            pass

    def start_download(self, message):
        self.download_message = message
        if self.download_message['result']:
            if not message['finish']:
                self.process_timer.start(2000)
                self.download_process = download_m3u8.start_download(self.download_message)
                update_download_large(self.movie_message[0], self.download_message['file_length'])
            else:
                if self.join_thread is None:
                    self.process_timer.start(2000)
                    self.flag = 3
                    self.statue.setText("开始合并文件")
                    self.join_thread = JoinTempFileThread(self.movie_message[2],
                                                          self.download_message['file_length'], self.movie_message[1],
                                                          self.movie_message[0])
                    self.join_thread.start()
        else:
            if 'code' in message:
                self.statue.setText("下载失败 错误代码 %s" % str(message['code']))
            self.flag = 0

    def process_download(self):
        """
        处理下载
        :return:
        """
        if self.flag == 0:
            self.flag = 1
            self.statue.setText('正在下载....')
            if self.download_process:
                self.download_process.terminate()
                self.download_process = None
            self.download_thread = GetDownloadMessageThread(self.movie_message[2],
                                                            self.movie_message[1],
                                                            self.movie_message[0])
            self.download_thread.download_message.connect(self.start_download)
            self.download_thread.start()
        elif self.flag == 2 or self.flag == 1:
            self.process_timer.stop()
            self.flag = 0
            self.statue.setText("已暂停")
            if self.download_process:
                self.download_process.terminate()
                self.download_process = None

    class DownloadItemMenu(QMenu):
        """
        下载封面右键菜单
        """

        def __init__(self, parent, movie_message, update_history_signal, video_id):
            super().__init__()
            self.video_id = video_id
            self.parent = parent
            self.movie_message = movie_message
            self.update_history_signal = update_history_signal
            self.addAction(QAction(u'删除记录', self))
            self.addAction(QAction(u'删除记录及文件', self))
            self.addAction(QAction(u'查看文件信息', self))
            self.addAction(QAction(u'打开下载目录', self))
            self.triggered[QAction].connect(self.processtrigger)

        # 右键按钮事件
        def processtrigger(self, q):
            text = q.text()
            if text == '删除记录':
                delete_download_message(self.movie_message[0])
                self.update_history_signal.emit(self.video_id)
            elif text == '删除记录及文件':
                try:
                    for file in os.listdir('./video/' + self.movie_message[0]):
                        os.remove('./video/%s/%s' % (self.movie_message[0], file))
                    os.removedirs('./video/' + self.movie_message[0])
                except FileNotFoundError as e:
                    pass
                delete_download_message(self.movie_message[0])
                self.update_history_signal.emit(self.video_id)
            elif text == '查看文件信息':
                self.parent.create_message_widget()
            elif text == '打开下载目录':
                try:
                    path = os.path.abspath('./video/%s' % self.movie_message[0])
                    os.startfile(path)
                except FileNotFoundError:
                    pass

        def my_custom_context_menu(self):
            self.exec_(QCursor.pos())


class DownloadButton(QLabel):

    download_widget = None

    def __init__(self, parent):
        super().__init__(parent)

        self.setText("下\n载\n管\n理")
        self.setWordWrap(True)
        self.setAlignment(Qt.AlignTop)
        q_css = """QLabel{
                        color:#ffffff;
                        background:#08bb06;
                        border-radius:5px;
                        width:112px;
                        height:35px;
                        font-family:microsoft yahei ui,microsoft yahei;
                        font-size:13px;
                    }
               """
        self.setStyleSheet(q_css)
        self.download_widget = DownloadWidget(None)
        self.download_widget.setVisible(False)

    def mousePressEvent(self, QMouseEvent):
        if QMouseEvent.buttons() == Qt.LeftButton:
            self.download_widget.setVisible(not self.download_widget.isVisible())

    def close_download_widget(self):
        self.download_widget.close()


class DownloadMessageWidget(QWidget):
    """
    下载信息界面
    """
    def __init__(self, parent, movie_message):
        super().__init__(parent)
        self.setWindowIcon(QIcon(r'.\images\detail.png'))
        self.movie_message = movie_message
        self.init_ui()
        self.resize(750, 110)

    def init_ui(self):
        self.setWindowTitle(self.movie_message[1])
        v_layout = QVBoxLayout()
        message = QTextBrowser()
        message.append('影片名称:  ' + self.movie_message[1])
        message.setStyleSheet('''
                QTextBrowser{
                                line-height:14px;
                                font-family:microsoft yahei ui,microsoft yahei;
                                font-size:13px;
                            }''')
        path = 'None'
        try:
            path = os.path.abspath('./video/%s' % self.movie_message[0])
        except FileNotFoundError:
            pass
        message.append('文件地址:  ' + path)
        message.append('影片地址:  ' + self.movie_message[2])
        message.append('发行时间:  ' + str(self.movie_message[3]))
        v_layout.addWidget(message)
        self.setLayout(v_layout)


class JoinTempFileThread(QThread):

    def __init__(self, url, num, name, video_object_id):
        super(JoinTempFileThread, self).__init__()
        self.url = url
        self.num = num
        self.name = name
        self.video_object_id = video_object_id

    def run(self):
        download_m3u8.join_temp_file(self.url, self.num, self.name, self.video_object_id)


class GetDownloadMessageThread(QThread):
    download_message = pyqtSignal(dict)

    def __init__(self, url, title, video_id):
        super(GetDownloadMessageThread, self).__init__()
        self.url = url
        self.title = title
        self.video_id = video_id

    def run(self):
        message = download_m3u8.create_download_message(self.url, self.title, self.video_id)
        if message:
            self.download_message.emit(message)
        else:
            self.download_message.emit({"result": False})


if __name__ == '__main__':
    app = QApplication(sys.argv)
    download = DownloadWidget(None)
    download.show()
    sys.exit(app.exec_())