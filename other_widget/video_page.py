# encoding: utf-8

"""
@version: 1.0
@author: WangNing
@license: GUN 
@contact: yogehaoren@gmail.com
@site: 
@software: PyCharm
@file: video_page.py
@time: 2019/3/4 18:46
@describe: 播放器界面
"""
import re
import os
import sys

from os.path import join

sys.path.append(os.path.abspath(os.getcwd()))
os.environ['PATH'] += ';' + r'D:\VLC'
import vlc
import requests
from urllib.parse import urljoin
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QApplication, QFrame, QStyle
from other_widget.common_widget import QUnFrameWindow, VideoSlider, MyQButton, MyQLabel
from PyQt5.QtGui import QPalette, QColor, QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from moviepy.editor import VideoFileClip

from tools.VideoConfigParser import VideoConfigParserClass
from tools.download_m3u8 import create_download_message, start_download
from tools.video_api import get_movie_download_message


class ParseVideoThread(QThread):
    """
        解析m3u8 线程
    """
    parse_message = pyqtSignal(dict)

    def __init__(self, url, video_id):
        super().__init__()
        self.url = url
        self.video_id = video_id

    def run(self):
        result = create_download_message(self.url, None, self.video_id)
        self.parse_message.emit(result)


class VideoJoinThread(QThread):
    """
    合并文件线程
    """
    config = VideoConfigParserClass().get_m3u8_download_setting()
    playable = pyqtSignal(str)
    video_duration = pyqtSignal(int)
    flag = True
    video_dir = './video/'
    proxies = None

    def __init__(self, url, video_message, is_finish):

        super().__init__()
        if self.config[0]:
            self.proxies = {'http': 'socks5://%s:%s' % (self.config[1], self.config[2]),
                            'https': 'socks5://%s:%s' % (self.config[1], self.config[2])}
        self.url = url
        self.video_message = video_message
        self.is_finish = is_finish
        self.video_path = ""

    def check_flag(self):
        while True:
            if self.flag is False:
                self.sleep(0.1)
            else:
                break

    @staticmethod
    def get_video_duration(video_path):
        clip = VideoFileClip(video_path)
        return int(clip.duration)

    def check_file(self, start_url, num):
        file = join(self.video_message["dir_path"], '%s%d.ts' % (start_url, num))
        temp_file = join(self.video_message["dir_path"], '%s%d.ts.aria2' % (start_url, num))
        if os.path.exists(file) and not os.path.exists(temp_file):
            return True
        else:
            return False

    def run(self):
        if not self.is_finish:
            self.sleep(10)
        pattern = re.compile('.*/(.*)\.m3u8')
        start_url = pattern.findall(self.url)[0]
        video_path = join(self.video_message["dir_path"], "temp.ts")
        self.video_path = video_path
        n = 0
        last_num = 0
        with open(video_path, "wb") as file:
            for i in range(self.video_message["file_length"]):
                self.check_flag()
                for num in range(3):
                    if self.check_file(start_url, i):
                        break
                    else:
                        print('wait ', i, num)
                        if i - last_num < 5:
                            if i > 10:
                                self.sleep(5)
                            else:
                                self.sleep(15)
                        else:
                            self.sleep(2)
                        last_num = i
                else:
                    try:
                        url = urljoin(self.url, '%s%d.ts' % (start_url, i))
                        print('get ', url)
                        if self.config[0]:
                            result = requests.get(url, proxies=self.proxies)
                        else:
                            result = requests.get(url)
                        if result.status_code == 200:
                            print("get sucess")
                            file.write(result.content)
                    except:
                        pass
                    continue
                try:
                    with open(join(self.video_message["dir_path"], '%s%d.ts' % (start_url, i)), 'rb') as f:
                        n += 1
                        while True:
                            block = f.read(10240)
                            if block:
                                file.write(block)
                            else:
                                break
                except:
                    pass
                if n % 10 == 0:
                    file.flush()
                    if not self.is_finish:
                        if n == 20:
                            self.playable.emit(self.video_path)
        self.playable.emit(self.video_path)
        self.video_duration.emit(self.get_video_duration(self.video_path))


class VideoPlayer(QUnFrameWindow):
    """
    播放器界面
    """
    video_path = ""
    video_widget = None
    video_frame = None
    video_slider = None
    play_button = None
    flash_button = None
    statue_label = None
    video_time_label = None
    parse_thread = None
    video_flag = True
    download_process = None
    join_thread = None
    media = None
    update_ui_timer = None
    all_duration = 0

    def __init__(self, video_message):
        super().__init__()
        self.setMinimumHeight(75)
        self.video_message = video_message
        self.init_ui()
        self.setFocusPolicy(Qt.StrongFocus)
        self.setWindowIcon(QIcon(r'.\images\video.png'))
        self.setWindowTitle(self.video_message[0])
        self.instance = vlc.Instance()
        self.media_player = self.instance.media_player_new()
        self.isPaused = False
        self.update_ui_timer = QTimer(self)
        self.update_ui_timer.setInterval(1000)
        self.update_ui_timer.timeout.connect(self.update_ui)
        video_path = './video/%s/%s.ts' % (self.video_message[6].replace('\'', '').replace('"', ''), self.video_message[0].replace('\'', '').replace('"', ''))
        if get_movie_download_message(self.video_message[6].replace('\'', '').replace('"', '')) == 1 and os.path.exists(video_path):
            self.start_play_video(video_path)
            self.set_video_range(VideoJoinThread.get_video_duration(video_path))
        else:
            self.parse_thread = ParseVideoThread(self.video_message[1], self.video_message[6])
            self.parse_thread.parse_message.connect(self.parse_video_complete)
            self.parse_thread.start()

    def init_ui(self):

        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.video_frame = VideoFrame(self)

        self.video_slider = VideoSlider(Qt.Horizontal, self)
        self.video_slider.set_position_value.connect(self.set_position)
        self.video_slider.setToolTip("Position")
        self.video_slider.setMaximum(1000)
        self.video_slider.sliderMoved.connect(self.set_position)

        main_layout.addWidget(self.video_frame)
        main_layout.addWidget(self.video_slider)

        bottom_layout = QHBoxLayout()
        self.play_button = MyQButton()
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_button.setMouseTracking(True)
        self.play_button.clicked.connect(self.play_or_pause)
        self.flash_button = MyQButton()
        self.flash_button.setIcon(QIcon(r'.\images\reload.png'))
        self.flash_button.clicked.connect(self.reload_video)

        self.statue_label = MyQLabel("正在解析...")
        self.statue_label.setFixedHeight(20)
        self.statue_label.setFixedWidth(150)
        self.statue_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter | Qt.AlignRight)
        self.video_time_label = MyQLabel("00:00:00/00:00:00")
        self.video_time_label.setFixedHeight(20)
        bottom_layout.addWidget(self.play_button, 0, Qt.AlignLeft)
        bottom_layout.addWidget(self.flash_button, 0, Qt.AlignLeft)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.video_time_label, 0, Qt.AlignRight)
        bottom_layout.addWidget(self.statue_label, 0, Qt.AlignRight)
        main_layout.addLayout(bottom_layout)

        self.content_widget.setLayout(main_layout)

    def reload_video(self):
        if not self.video_flag and self.parse_thread is None and self.join_thread is None:
            self.video_flag = True
            self.statue_label.setText("正在尝试重新解析")
            self.parse_thread = ParseVideoThread(self.video_message[1], self.video_message[6])
            self.parse_thread.parse_message.connect(self.parse_video_complete)
            self.parse_thread.start()

    def update_ui(self):
        """updates the user interface"""

        self.video_slider.setValue(self.media_player.get_position() * 1000)
        # self.video_slider.setValue(self.media_player.get_time()/1000)
        now = self.create_time_message(self.media_player.get_time() / 1000)
        length = self.create_time_message(self.all_duration)
        self.video_time_label.setText("%s/%s" % (now, length))
        if not self.media_player.is_playing():
            self.update_ui_timer.stop()
            if not self.isPaused:
                self.stop_video()

    def stop_video(self):
        """Stop player
        """
        self.media_player.stop()
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))

    def set_video_range(self, duration):
        self.all_duration = duration
        # print("duration is ", duration)

    def start_play_video(self, video_path):
        self.video_path = video_path
        self.statue_label.setText("播放中")
        self.media = self.instance.media_new(video_path)
        # put the media in the media player
        self.media_player.set_media(self.media)

        # parse the metadata of the file
        self.media.parse()
        self.media_player.set_hwnd(self.video_frame.winId())
        self.play_or_pause()

    def set_position(self, position):
        """Set the position
        """
        self.media_player.set_position(position / 1000.0)

    def play_or_pause(self):
        """Toggle play/pause status
        """
        if self.media_player.is_playing():
            self.media_player.pause()
            self.statue_label.setText("已暂停")
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            self.isPaused = True
        else:
            if not self.video_flag:
                return
            self.media_player.play()
            self.statue_label.setText("播放中")
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
            self.update_ui_timer.start()
            self.isPaused = False

    @staticmethod
    def create_time_message(time):
        time_str = "%02d:%02d:%02d"
        m, h = 60, 60*60
        time = int(time)
        hour = int(time / h)
        mine = int(time % h / m)
        second = int(time % h % m)
        return time_str % (hour, mine, second)

    def parse_video_complete(self, message):
        if message["result"]:
            self.video_flag = True
            self.set_video_range(int(message['file_length'] * 1.5))
            self.statue_label.setText("解析成功,正在缓冲...")
            if not message['finish']:
                self.download_process = start_download(message)
            self.join_thread = VideoJoinThread(self.video_message[1], message, message['finish'])
            self.join_thread.playable.connect(self.start_play_video)
            self.join_thread.video_duration.connect(self.set_video_range)
            self.join_thread.start()
        else:
            if 'code' in message:
                self.statue.setText("下载失败 错误代码 %s" % str(message['code']))
            else:
                self.statue_label.setText("下载失败!")
            # m3u8文件下载失败 禁止进行后续缓冲
            self.video_flag = False
            if self.parse_thread is not None:
                try:
                    self.parse_thread.terminate()
                except:
                    pass
            self.parse_thread = None

    def closeEvent(self, QCloseEvent):
        if self.download_process is not None:
            try:
                self.download_process.terminate()
                self.media_player.stop()
            except:
                pass
        QCloseEvent.accept()

    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == Qt.Key_Left:
            self.set_position(self.media_player.get_position()*1000 - 2)
        elif QKeyEvent.key() == Qt.Key_Right:
            self.set_position(self.media_player.get_position()*1000 + 2)
        elif QKeyEvent.key() == Qt.Key_Space:
            self.play_or_pause()


class VideoFrame(QFrame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(0, 0, 0))
        self.setPalette(palette)
        self.setMouseTracking(True)
        self.setAutoFillBackground(True)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    window = VideoPlayer(sys.argv[1:])
    window.resize(700, 500)
    window.setCloseButton(True)
    window.setMinMaxButtons(True)
    window.show()
    sys.exit(app.exec_())