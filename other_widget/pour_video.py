# encoding: utf-8

"""
@version: 1.0
@author: WangNing
@license: GUN 
@contact: yogehaoren@gmail.com
@site: 
@software: PyCharm
@file: pour_video.py
@time: 2019/3/6 9:17
@describe: 
"""
import os

import vlc
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QApplication, QFrame, QStyle, QWidget, QFileDialog
from other_widget.common_widget import QUnFrameWindow, VideoSlider, MyQButton, MyQLabel
from PyQt5.QtGui import QPalette, QColor, QIcon
from PyQt5.QtCore import Qt, QTimer
from moviepy.editor import VideoFileClip


class VideoPlayer(QUnFrameWindow):
    """
    播放器界面
    """
    video_path = ""
    video_widget = None
    video_frame = None
    video_slider = None
    play_button = None
    statue_label = None
    video_time_label = None
    media = None
    update_ui_timer = None
    all_duration = 0
    setting_button = None

    def __init__(self, video_path=''):
        super().__init__()
        self.video_path = video_path
        self.setMinimumHeight(75)
        self.init_ui()
        self.setFocusPolicy(Qt.StrongFocus)
        self.setWindowIcon(QIcon(r'.\images\video.png'))
        self.instance = vlc.Instance()
        self.media_player = self.instance.media_player_new()
        self.isPaused = False
        self.setWindowTitle("My Video Player")
        if video_path != '':
            self.set_video()
        self.update_ui_timer = QTimer(self)
        self.update_ui_timer.setInterval(1000)
        self.update_ui_timer.timeout.connect(self.update_ui)

    def init_ui(self):

        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.video_frame = QFrame(self)
        palette = self.video_frame.palette()
        palette.setColor(QPalette.Window, QColor(0, 0, 0))
        self.video_frame.setPalette(palette)
        self.video_frame.setMouseTracking(True)
        self.video_frame.setAutoFillBackground(True)

        self.video_slider = VideoSlider(Qt.Horizontal, self)
        self.video_slider.set_position_value.connect(self.set_position)
        self.video_slider.setToolTip("Position")
        self.video_slider.setMaximum(1000)
        self.video_slider.sliderMoved.connect(self.set_position)

        main_layout.addWidget(self.video_frame)
        main_layout.addWidget(self.video_slider)

        bottom_layout = QHBoxLayout()
        self.setting_button = MyQButton(b'\xe2\x98\xb0'.decode())
        self.setting_button.setMouseTracking(True)
        self.setting_button.clicked.connect(self.get_video)
        self.play_button = MyQButton()
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_button.setMouseTracking(True)
        self.play_button.clicked.connect(self.play_or_pause)

        self.statue_label = MyQLabel("")
        self.statue_label.setFixedHeight(20)
        self.statue_label.setFixedWidth(150)
        self.statue_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.video_time_label = MyQLabel("00:00:00/00:00:00")
        self.video_time_label.setFixedHeight(20)
        bottom_layout.addWidget(self.play_button, 0, Qt.AlignLeft)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.video_time_label, 0, Qt.AlignRight)
        bottom_layout.addWidget(self.statue_label, 0, Qt.AlignRight)
        bottom_layout.addWidget(self.setting_button, 0, Qt.AlignRight)
        main_layout.addLayout(bottom_layout)

        self.content_widget.setLayout(main_layout)

    def set_video(self):
        # create the media
        self.media = self.instance.media_new(self.video_path)
        # put the media in the media player
        self.media_player.set_media(self.media)

        # parse the metadata of the file
        self.media.parse()
        # set the title of the track as window title
        self.setWindowTitle(self.media.get_meta(0))

        self.set_video_range(self.media.get_duration()/1000)
        self.media_player.set_hwnd(self.video_frame.winId())

    def get_video(self):
        result = None
        if not self.video_path:
            result = QFileDialog.getOpenFileName(
                self,
                "Open File",
                os.path.expanduser('.')
            )

        if not result:
            return

        self.video_path = result[0]
        self.set_video()
        self.play_or_pause()

    def update_ui(self):
        """updates the user interface"""
        self.video_slider.setValue(self.media_player.get_position() * 1000)
        # self.video_slider.setValue(self.media_player.get_time()/1000)
        now = self.create_time_message(self.media_player.get_time()/1000)
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

    def set_position(self, position):
        """Set the position
        """
        self.media_player.set_position(position/1000)

    def play_or_pause(self):
        """Toggle play/pause status
        """
        if self.media_player.is_playing():
            self.media_player.pause()
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            self.isPaused = True
        else:
            if self.video_path == '':
                return
            self.media_player.play()
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
            self.update_ui_timer.start()
            self.isPaused = False

    @staticmethod
    def get_video_duration(video_path):
        clip = VideoFileClip(video_path)
        return int(clip.duration)

    @staticmethod
    def create_time_message(time):
        time_str = "%02d:%02d:%02d"
        m, h = 60, 60*60
        time = int(time)
        hour = int(time / h)
        mine = int(time % h / m)
        second = int(time % h % m)
        return time_str % (hour, mine, second)

    def closeEvent(self, QCloseEvent):
        QCloseEvent.accept()

    def keyPressEvent(self, QKeyEvent):
        print(QKeyEvent.key())
        if QKeyEvent.key() == Qt.Key_Left:
            self.set_position(self.media_player.get_position()*1000 - 2)
        elif QKeyEvent.key() == Qt.Key_Right:
            self.set_position(self.media_player.get_position()*1000 + 2)
        elif QKeyEvent.key() == Qt.Key_Space:
            self.play_or_pause()




if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = VideoPlayer('')
    window.resize(750, 450)
    window.setCloseButton(True)
    window.setMinMaxButtons(True)
    window.show()
    sys.exit(app.exec_())