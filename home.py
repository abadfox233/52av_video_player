# encoding: utf-8

"""
@version: 1.0
@author: WangNing
@license: GUN 
@contact: yogehaoren@gmail.com
@site: 
@software: PyCharm
@file: home.py
@time: 2019/1/25 18:07
@describe:播放器首页
"""
import subprocess
import random
import sys
from os.path import join

from PyQt5.QtWidgets import QMainWindow, QWidget, QAction, QPushButton, QLabel, QGridLayout, QVBoxLayout, \
    QHBoxLayout, QMessageBox, QApplication, QMenu, QLineEdit
from PyQt5.QtCore import QMimeData, QPoint
from PyQt5.QtGui import QIntValidator, QCursor, QIcon

from tools.video_api import *
from other_widget.download_page import DownloadWidget, DownloadButton
from other_widget.config_page import ConfigButton
from other_widget.update_page import UpdateButton
start_image_path = VideoConfigParserClass.static_get_image_path()

button_css = """
                QPushButton{
                            color:#ffffff;
                            background:#08bb06;
                            border-radius:5px;
                            width:60px;
                            height:15px;
                            font-family:microsoft yahei ui,microsoft yahei;
                            font-size:12px;
                        }
                QPushButton:disabled{color:#FFFFFF}
                QPushButton:pressed{background:#d4ebd4;}
            """
label_css = 'QLabel{font-family:\"Microsoft YaHei\";font-size:12px;background:transparent;color:#FFFFFF;}'

download_widget = None


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
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
        self.setWindowTitle("video")
        self.setGeometry(250, 50, 795, 600)
        self.setCentralWidget(HomeWidget())
        self.setFixedWidth(795)
        self.setWindowIcon(QIcon(r'.\images\video.png'))


class HomeWidget(QWidget):
    """
    首页布局
    """
    now_page = 1
    all_page_num = 0
    download_widget = None
    page_validator = None
    movie_list = None
    page_label = None
    show_movie_list = None
    search_input_edit = None
    page_edit = None
    movie_layout = None

    def __init__(self):
        super(HomeWidget, self).__init__(None)
        self.init_ui()
        self.setStyleSheet("""QWidget
                                    {
                                        background-color:#313034;
                                        color:#2c2f34;
                                        font-size:12px;
                                        border:None;
                                        font: "Tlwg Typo";
                                        margin:0px;
                                    }
                                """)

    def init_ui(self):
        """
        初始化界面
        :return:
        """

        home_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        right_layout = QGridLayout()
        bottom_layout = QHBoxLayout()
        self.download_widget = DownloadWidget(None)
        self.page_validator = QIntValidator()
        self.movie_list = search_video('')
        self.page_label = QLabel()
        self.page_label.setStyleSheet(label_css)
        self.flush_page_label()

        self.show_movie_list = self.movie_list[0:9]
        self.movie_layout = MovieLayout(self.show_movie_list)

        # 底部

        refresh_button = QPushButton("随机刷新")
        refresh_button.setStyleSheet(button_css)
        refresh_button.clicked.connect(self.refresh_movie)
        self.search_input_edit = MyQLineEdit(self)
        self.search_input_edit.setFixedWidth(300)
        self.search_input_edit.setPlaceholderText("搜索关键词")
        search_button = QPushButton("搜索")
        search_button.setStyleSheet(button_css)
        search_button.clicked.connect(self.search_movie)

        next_page_button = QPushButton("下一页")
        next_page_button.clicked.connect(self.next_page)
        pre_page_button = QPushButton("上一页")
        pre_page_button.clicked.connect(self.pre_page)
        next_page_button.setStyleSheet(button_css)
        pre_page_button.setStyleSheet(button_css)

        self.page_edit = MyQLineEdit(self)
        self.page_edit.setFixedWidth(30)
        jump_page_button = QPushButton("跳转")
        jump_page_button.setStyleSheet(button_css)
        self.page_edit.setValidator(self.page_validator)
        jump_page_button.clicked.connect(self.jump_page)

        bottom_layout.addWidget(refresh_button, 0, Qt.AlignLeft)
        bottom_layout.addWidget(self.search_input_edit, 2, Qt.AlignRight)
        bottom_layout.addWidget(search_button, 0, Qt.AlignRight)
        bottom_layout.addWidget(pre_page_button, 0, Qt.AlignRight)
        bottom_layout.addWidget(self.page_label, 0, Qt.AlignRight)
        bottom_layout.addWidget(next_page_button, 0, Qt.AlignRight)
        bottom_layout.addWidget(self.page_edit, 0, Qt.AlignRight)
        bottom_layout.addWidget(jump_page_button, 0, Qt.AlignRight)

        # 右界面
        download_widget_button = DownloadButton(self)
        download_widget_button.setAlignment(Qt.AlignVCenter)
        global download_widget
        download_widget = download_widget_button.download_widget
        config_widget_button = ConfigButton(self)
        config_widget_button.setAlignment(Qt.AlignVCenter)
        update_widget_button = UpdateButton(self)
        update_widget_button.setAlignment(Qt.AlignVCenter)
        right_layout.addWidget(download_widget_button, 0, 0, 1, 1)
        right_layout.addWidget(config_widget_button, 1, 0, 1, 1)
        right_layout.addWidget(update_widget_button, 2, 0, 1, 1)
        right_layout.addWidget(QWidget(), 3, 0, 1, 1)
        right_layout.addWidget(QWidget(), 4, 0, 1, 1)

        # 输入框回车事件绑定
        self.search_input_edit.enter_press = self.search_movie
        self.page_edit.enter_press = self.jump_page

        # 添加布局
        left_layout.addLayout(self.movie_layout)
        left_layout.addLayout(bottom_layout)
        home_layout.addLayout(left_layout, 1)
        home_layout.addLayout(right_layout)
        self.setLayout(home_layout)

    def wheelEvent(self, QWheelEvent):
        """
        滚轮事件
        :param QWheelEvent:
        :return:
        """
        if QWheelEvent.angleDelta().y() > 0:
            self.pre_page()
        else:
            self.next_page()

    def keyPressEvent(self, QKeyEvent):
        """
        监听键盘事件 支持上下翻页
        :param QKeyEvent:
        :return:
        """
        if QKeyEvent.key() == Qt.Key_Up or QKeyEvent.key() == Qt.Key_Left:
            self.pre_page()
        elif QKeyEvent.key() == Qt.Key_Down or QKeyEvent.key() == Qt.Key_Right:
            self.next_page()

    def refresh_movie(self):
        """
        随机刷新按钮事件
        :return:
        """
        temp_movie_list = get_random_movie(self.movie_list, 9)
        self.movie_layout.change_movie(temp_movie_list)

    def flush_page_label(self):
        """
        刷新页数显示 以及更改页数范围
        :return:
        """
        self.all_page_num = self.all_page(len(self.movie_list))
        self.page_label.setText("当前%d页/共%d页" % (self.now_page, self.all_page_num))
        self.page_validator.setRange(1, self.all_page_num)

    def next_page(self):
        """
        下一页按钮 事件
        :return:
        """
        if self.now_page+1 <= self.all_page_num:
            self.now_page += 1
            self.show_movie_list = self.movie_list[(self.now_page - 1) * 9:self.now_page * 9]
            self.movie_layout.change_movie(self.show_movie_list)
            self.flush_page_label()

    def pre_page(self):
        """
        上一页按钮事件
        :return:
        """
        if self.now_page > 1:
            self.now_page -= 1
            self.show_movie_list = self.movie_list[(self.now_page - 1) * 9:self.now_page * 9]
            self.movie_layout.change_movie(self.show_movie_list)
            self.flush_page_label()

    def jump_page(self):
        """
        跳转页面按钮事件
        :return:
        """
        jump_page_num = self.page_edit.text()
        if jump_page_num.isalnum():
            self.now_page = int(jump_page_num)
            self.show_movie_list = self.movie_list[(self.now_page - 1) * 9:self.now_page * 9]
            self.movie_layout.change_movie(self.show_movie_list)
            self.flush_page_label()

    def search_movie(self):
        """
        搜索按钮事件
        :return:
        """
        search_word = self.search_input_edit.text()
        temp_movie_list = search_video(search_word)
        if len(temp_movie_list):
            self.movie_list = temp_movie_list
            self.now_page = 1
            self.show_movie_list = self.movie_list[(self.now_page - 1) * 9:self.now_page * 9]
            self.movie_layout.change_movie(self.show_movie_list)
            self.flush_page_label()
        else:
            QMessageBox.warning(self, '404', '影片未找到哟！', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

    @staticmethod
    def all_page(movie_num):
        """
        计算全部页数
        :param movies:
        :return:
        """
        if movie_num % 10 > 0:
            return int(movie_num / 10 + 1)
        else:
            return int(movie_num / 10)

    def closeEvent(self, QCloseEvent):
        return super().closeEvent()


class MovieLayout(QGridLayout):
    """
    主页显示影片封面布局
    """
    def __init__(self, movie_list):
        super().__init__()
        self.movie_list = movie_list
        self.movie_widget_list = []
        self.bind_movie_list()

    def bind_movie_list(self):
        """
        绑定影片
        :return:
        """
        row = 0
        line = 0
        for movie in self.movie_list:
            if line == 3:
                line = 0
                row += 1
            movie_item_widget = MovieItemWidget(None, movie)
            self.addLayout(movie_item_widget, row, line)
            self.movie_widget_list.append(movie_item_widget)
            line += 1

    def change_movie(self, movie_list):
        """
        改变影片源
        :param movie_list:
        :return:
        """
        self.movie_list = movie_list
        for i in range(len(movie_list)):
            self.movie_widget_list[i].change_movie(self.movie_list[i])
        if len(movie_list) < 9:
            try:
                for x in range(len(movie_list), 9):
                    self.movie_widget_list[x].set_none_movie()
            except IndexError:
                pass


class MovieItemWidget(QVBoxLayout):
    """
    自定义影片封面
    """

    def __init__(self, parent, movie_item):
        super().__init__(parent)
        self.movie_message = movie_item
        self.image_label = QLabel()
        self.title_label = QLabel()
        self.issue_time_label = QLabel()
        self.title_label.setStyleSheet(label_css)
        self.issue_time_label.setStyleSheet(label_css)
        self.addWidget(self.image_label)
        self.addWidget(self.issue_time_label)
        self.addWidget(self.title_label)
        self.bind_movie()
        self.menu = self.MovieItemMenu(self)
        self.title_label.mousePressEvent = self.mousePressEvent
        self.image_label.mousePressEvent = self.mousePressEvent
        self.issue_time_label.mousePressEvent = self.mousePressEvent
        self.image_label.setContextMenuPolicy(Qt.CustomContextMenu)
        self.image_label.customContextMenuRequested[QPoint].connect(self.my_custom_context_menu)

    def my_custom_context_menu(self):
        self.menu.exec_(QCursor.pos())

    def mousePressEvent(self, QMouseEvent):
        if QMouseEvent.buttons() == Qt.RightButton:
            minme_data = QMimeData()
            minme_data.setText(self.movie_message[0])
            clipboard = QApplication.clipboard()
            clipboard.setMimeData(minme_data)
        elif QMouseEvent.buttons() == Qt.LeftButton:
            # print(self.movie_message)
            self.create_video_process()

    def create_video_process(self):
        python_path = r'E:\mycs\python\env\kivy\Scripts\python.exe '
        video_path = os.path.abspath('./other_widget/video_page.py ')
        args = ' '
        for x in self.movie_message:
            args += "\"" + str(x) + '\" '
        cmd = "%s %s %s" % (python_path, video_path, args)
        new_env = os.environ.copy()
        # si = subprocess.STARTUPINFO()
        # si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        # dev_null = open(os.devnull, 'w')
        # subprocess.Popen(cmd, stdin=dev_null, stdout=dev_null, stderr=dev_null, startupinfo=si, env=new_env)
        subprocess.Popen(cmd, env=new_env)

    def change_movie(self, movie):
        """
        修改影片源
        :param movie:
        :return:
        """
        self.movie_message = movie
        self.menu.movie_message = movie
        self.bind_movie()

    def bind_movie(self):
        """
        绑定影片
        :return:
        """
        add_x = lambda x: x[0:20] + "\n" + x[20:40]
        self.title_label.setText(add_x(self.movie_message[0]))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.issue_time_label.setText(str(self.movie_message[2]))
        self.issue_time_label.setAlignment(Qt.AlignCenter)
        pix_image = change_image_size(join(start_image_path, self.movie_message[4]), 240, 134)
        self.image_label.setPixmap(pix_image)
        self.image_label.resize(pix_image.width(), pix_image.height())

    def set_none_movie(self):
        """
        设置空影片
        :return:
        """
        self.movie_message = ['', '', './images/404.jpg']
        self.menu.movie_message = self.movie_message
        self.title_label.setText("")
        self.issue_time_label.setText('')
        pix_image = change_image_size('./images/404.jpg', 240, 134)
        self.image_label.setPixmap(pix_image)
        self.image_label.resize(pix_image.width(), pix_image.height())

    def update_download_ui(self):
        pass

    class MovieItemMenu(QMenu):
        """
        影片封面右键菜单
        """

        def __init__(self, parent):
            super().__init__()
            self.parent = parent
            self.movie_message = parent.movie_message
            self.addAction(QAction(u'收藏', self))
            self.addAction(QAction(u'下载', self))
            self.triggered[QAction].connect(self.processtrigger)

        # 右键按钮事件
        def processtrigger(self, q):
            text = q.text()
            if text == '下载':
                if self.movie_message[0] != '':
                    result = add_download_message(self.movie_message[6])
                    if result:
                        movie_message = self.movie_message
                        temp_movie_message = [movie_message[6],
                                              movie_message[0],
                                              movie_message[1],
                                              movie_message[2],
                                              0,
                                              movie_message[4]]
                        download_widget.add_download_movie(temp_movie_message)
            else:
                pass


def get_random_movie(movie_list, num):
    """
    获取随机影片
    :param movie_list:
    :param num:
    :return:
    """
    video_num = random.randint(0, len(movie_list) - num)
    movie_list = movie_list[video_num:video_num + num]
    return movie_list


class MyQLineEdit(QLineEdit):
    """
    自定义QLineEdit 目的为了防止回车事件处理两次逻辑
    """
    def __init__(self, parent):
        super().__init__(parent)
        q_css = """
            QLineEdit { border:1px solid #ddd;border-radius:3px;padding:0px 7px;font-size:12px;width:250px;color:#FFFFFF}
        """
        self.setStyleSheet(q_css)

    def keyPressEvent(self, QKeyEvent):
        """
        监听键盘事件 支持回车事件
        :param QKeyEvent:
        :return:a
        """
        if QKeyEvent.key() == Qt.Key_Return or QKeyEvent.key() == 16777221:
            self.enter_press()
        elif QKeyEvent.key() == Qt.Key_Up or QKeyEvent.key() == Qt.Key_Down:
            return self.parent().keyPressEvent(QKeyEvent)
        else:
            return super().keyPressEvent(QKeyEvent)

    def enter_press(self):
        pass


if __name__ == '__main__':
    init_env_environment(False)
    app = QApplication(sys.argv)
    main_windows = MainWindow()
    main_windows.show()
    sys.exit(app.exec_())