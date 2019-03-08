# encoding: utf-8

"""
@version: 1.0
@author: WangNing
@license: GUN 
@contact: yogehaoren@gmail.com
@site: 
@software: PyCharm
@file: common_widget.py
@time: 2019/3/1 19:13
@describe: 通用自定义组件
"""
from PyQt5.QtWidgets import QLineEdit, QPushButton, QLabel, QApplication, QWidget, QVBoxLayout,\
                            QHBoxLayout, QSlider
from PyQt5.QtCore import Qt, QSize, QPoint, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QFont

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
label_css = 'QLabel{font-family:\"Microsoft YaHei\";font-size:12px;background:transparent;color:#000000;}'
q_css = """
            QLineEdit { border:1px solid #ddd;border-radius:3px;padding:0px 7px;font-size:12px;width:250px;}
        """


class MyQLineEdit(QLineEdit):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(q_css)


class MyQLabel(QLabel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(label_css)


class MyQButton(QPushButton):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(button_css)


class QTitleLabel(QLabel):
    """
    新建标题栏标签类
    """
    def __init__(self, parent, function):
        super(QTitleLabel, self).__init__(parent)
        self.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.function = function
        self.setFixedHeight(30)
        self.setStyleSheet("QTitleLabel{ background-color: Gainsboro; font: 100 10pt; }")

    def mouseDoubleClickEvent(self, *args, **kwargs):
        self.function()
        return super().mouseDoubleClickEvent(*args, **kwargs)


class QTitleButton(QPushButton):
    """
    新建标题栏按钮类
    """
    def __init__(self, *args):
        super(QTitleButton, self).__init__(*args)
        # 特殊字体以不借助图片实现最小化最大化和关闭按钮
        self.setFont(QFont("Webdings"))
        self.setFixedWidth(40)
        self.setStyleSheet("""QTitleButton{
                                background-color: rgba(255, 255, 255, 0);
                                color: black;
                                border: 0px;
                                font: 100 10pt;
                            }
                            QTitleButton#MinMaxButton:hover{
                                    background-color: #D0D0D1;
                                    border: 0px;
                                    font: 100 10pt;
                            }
                            QTitleButton#CloseButton:hover{
                                    background-color: #D32424;
                                    color: white;
                                    border: 0px;
                                    font: 100 10pt;
                            }""")


class QUnFrameWindow(QWidget):
    """
    无边框窗口类
    """
    content_widget = None
    _move_drag = False
    _corner_drag = False
    _bottom_drag = False
    _right_drag = False
    _TitleLabel = None
    _MainLayout = None
    _CloseButton = None
    _MaximumButton = None
    _MinimumButton = None
    _right_rect = None
    _bottom_rect = None
    move_DragPosition = None
    _corner_rect = None

    def __init__(self):
        # 设置为顶级窗口，无边框
        super(QUnFrameWindow, self).__init__(None, Qt.FramelessWindowHint)
        # 设置边界宽度为5
        self._padding = 5
        # 安放标题栏标签
        self.init_title_label()
        # 用装饰器将设置WindowTitle名字函数共享到标题栏标签上
        self.setWindowTitle = self._setTitleText(self.setWindowTitle)
        self.setWindowTitle("UnFrameWindow")
        # 设置框架布局
        self.init_layout()
        self.setMinimumWidth(250)
        # 设置widget鼠标跟踪
        self.setMouseTracking(True)
        # 设置鼠标跟踪判断默认值
        self.init_drag()

    def init_drag(self):
        # 设置鼠标跟踪判断扳机默认值
        self._move_drag = False
        self._corner_drag = False
        self._bottom_drag = False
        self._right_drag = False

    def init_title_label(self):
        # 安放标题栏标签
        self._TitleLabel = QTitleLabel(self, self.change_windows)
        # 设置标题栏标签鼠标跟踪（如不设，则标题栏内在widget上层，无法实现跟踪）
        self._TitleLabel.setMouseTracking(True)
        self._TitleLabel.setIndent(10)
        # 设置标题栏文本缩进
        self._TitleLabel.move(0, 0)
        # 标题栏安放到左上角

    def init_layout(self):
        # 设置框架布局
        self.content_widget = QWidget(self)
        self.content_widget.move(2,  32)
        self.content_widget.setMouseTracking(True)

    def _setTitleText(self, func):
        # 设置标题栏标签的装饰器函数
        def wrapper(*args):
            self._TitleLabel.setText(*args)
            return func(*args)
        return wrapper

    def setTitleAlignment(self, alignment):
        # 给widget定义一个setTitleAlignment函数，以实现标题栏标签的对齐方式设定
        self._TitleLabel.setAlignment(alignment | Qt.AlignVCenter)

    def setCloseButton(self, bool):
        # 给widget定义一个setCloseButton函数，为True时设置一个关闭按钮
        if bool:
            self._CloseButton = QTitleButton(b'\xef\x81\xb2'.decode("utf-8"), self)
            self._CloseButton.setObjectName("CloseButton")
            # 设置按钮的ObjectName以在qss样式表内定义不同的按钮样式
            self._CloseButton.setToolTip("关闭窗口")
            self._CloseButton.setMouseTracking(True)
            # 设置按钮鼠标跟踪（如不设，则按钮在widget上层，无法实现跟踪）
            self._CloseButton.setFixedHeight(self._TitleLabel.height())
            # 设置按钮高度为标题栏高度
            self._CloseButton.clicked.connect(self.close)
            # 按钮信号连接到关闭窗口的槽函数

    def setMinMaxButtons(self, bool):
        # 给widget定义一个setMinMaxButtons函数，为True时设置一组最小化最大化按钮
        if bool:
            self._MinimumButton = QTitleButton(b'\xef\x80\xb0'.decode("utf-8"), self)
            self._MinimumButton.setObjectName("MinMaxButton")
            # 设置按钮的ObjectName以在qss样式表内定义不同的按钮样式
            self._MinimumButton.setToolTip("最小化")
            self._MinimumButton.setMouseTracking(True)
            # 设置按钮鼠标跟踪（如不设，则按钮在widget上层，无法实现跟踪）
            self._MinimumButton.setFixedHeight(self._TitleLabel.height())
            # 设置按钮高度为标题栏高度
            self._MinimumButton.clicked.connect(self.showMinimized)
            # 按钮信号连接到最小化窗口的槽函数
            self._MaximumButton = QTitleButton(b'\xef\x80\xb1'.decode("utf-8"), self)
            self._MaximumButton.setObjectName("MinMaxButton")
            # 设置按钮的ObjectName以在qss样式表内定义不同的按钮样式
            self._MaximumButton.setToolTip("最大化")
            self._MaximumButton.setMouseTracking(True)
            # 设置按钮鼠标跟踪（如不设，则按钮在widget上层，无法实现跟踪）
            self._MaximumButton.setFixedHeight(self._TitleLabel.height())
            # 设置按钮高度为标题栏高度
            self._MaximumButton.clicked.connect(self._changeNormalButton)
            # 按钮信号连接切换到恢复窗口大小按钮函数

    def change_windows(self):
        if self._MaximumButton.toolTip() == "最大化":
            self._changeNormalButton()
        else:
            self._changeMaxButton()

    def _changeNormalButton(self):
        # 切换到恢复窗口大小按钮
        try:
            self.showMaximized()
            # 先实现窗口最大化
            self._MaximumButton.setText(b'\xef\x80\xb2'.decode("utf-8"))
            # 更改按钮文本
            self._MaximumButton.setToolTip("恢复")
            # 更改按钮提示
            self._MaximumButton.disconnect()
            # 断开原本的信号槽连接
            self._MaximumButton.clicked.connect(self._changeMaxButton)
            # 重新连接信号和槽
        except:
            pass

    def _changeMaxButton(self):
        # 切换到最大化按钮
        try:
            self.showNormal()
            self._MaximumButton.setText(b'\xef\x80\xb1'.decode("utf-8"))
            self._MaximumButton.setToolTip("最大化")
            self._MaximumButton.disconnect()
            self._MaximumButton.clicked.connect(self._changeNormalButton)
        except:
            pass

    def resizeEvent(self, QResizeEvent):
        # 自定义窗口调整大小事件
        self._TitleLabel.setFixedWidth(self.width())
        self.content_widget.setFixedWidth(self.width()-4)
        self.content_widget.setFixedHeight(self.height()-35)
        # 将标题标签始终设为窗口宽度
        # 分别移动三个按钮到正确的位置
        try:
            self._CloseButton.move(self.width() - self._CloseButton.width(), 0)
        except:
            pass
        try:
            self._MinimumButton.move(self.width() - (self._CloseButton.width() + 1) * 3 + 1, 0)
        except:
            pass
        try:
            self._MaximumButton.move(self.width() - (self._CloseButton.width() + 1) * 2 + 1, 0)
        except:
            pass
        # 重新调整边界范围以备实现鼠标拖放缩放窗口大小，采用三个列表生成式生成三个列表
        self._right_rect = [QPoint(x, y) for x in range(self.width() - self._padding, self.width() + 1)
                           for y in range(1, self.height() - self._padding)]
        self._bottom_rect = [QPoint(x, y) for x in range(1, self.width() - self._padding)
                         for y in range(self.height() - self._padding, self.height() + 1)]
        self._corner_rect = [QPoint(x, y) for x in range(self.width() - self._padding, self.width() + 1)
                                    for y in range(self.height() - self._padding, self.height() + 1)]

    def mousePressEvent(self, event):
        # 重写鼠标点击的事件
        if (event.button() == Qt.LeftButton) and (event.pos() in self._corner_rect):
            # 鼠标左键点击右下角边界区域
            self._corner_drag = True
            event.accept()
        elif (event.button() == Qt.LeftButton) and (event.pos() in self._right_rect):
            # 鼠标左键点击右侧边界区域
            self._right_drag = True
            event.accept()
        elif (event.button() == Qt.LeftButton) and (event.pos() in self._bottom_rect):
            # 鼠标左键点击下侧边界区域
            self._bottom_drag = True
            event.accept()
        elif (event.button() == Qt.LeftButton) and (event.y() < self._TitleLabel.height()):
            # 鼠标左键点击标题栏区域
            self._move_drag = True
            self.move_DragPosition = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, QMouseEvent):
        # 判断鼠标位置切换鼠标手势
        if QMouseEvent.pos() in self._corner_rect:
            self.setCursor(Qt.SizeFDiagCursor)
        elif QMouseEvent.pos() in self._bottom_rect:
            self.setCursor(Qt.SizeVerCursor)
        elif QMouseEvent.pos() in self._right_rect:
            self.setCursor(Qt.SizeHorCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
        # 当鼠标左键点击不放及满足点击区域的要求后，分别实现不同的窗口调整
        # 没有定义左方和上方相关的5个方向，主要是因为实现起来不难，但是效果很差，拖放的时候窗口闪烁，再研究研究是否有更好的实现
        if Qt.LeftButton and self._right_drag:
            # 右侧调整窗口宽度
            self.resize(QMouseEvent.pos().x(), self.height())
            QMouseEvent.accept()
        elif Qt.LeftButton and self._bottom_drag:
            # 下侧调整窗口高度
            self.resize(self.width(), QMouseEvent.pos().y())
            QMouseEvent.accept()
        elif Qt.LeftButton and self._corner_drag:
            # 右下角同时调整高度和宽度
            self.resize(QMouseEvent.pos().x(), QMouseEvent.pos().y())
            QMouseEvent.accept()
        elif Qt.LeftButton and self._move_drag:
            # 标题栏拖放窗口位置
            self.move(QMouseEvent.globalPos() - self.move_DragPosition)
            QMouseEvent.accept()

    def mouseReleaseEvent(self, QMouseEvent):
        # 鼠标释放后，各扳机复位
        self._move_drag = False
        self._corner_drag = False
        self._bottom_drag = False
        self._right_drag = False


class VideoSlider(QSlider):

    set_position_value = pyqtSignal(int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFocusPolicy(Qt.NoFocus)
        self.setMouseTracking(True)

        self.setStyleSheet("  \
             QSlider::add-page:Horizontal\
             {     \
                background-color: rgb(87, 97, 106);\
                height:4px;\
             }\
             QSlider::sub-page:Horizontal \
            {\
                background-color:qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(231,80,229, 255), stop:1 rgba(7,208,255, 255));\
                height:4px;\
             }\
            QSlider::groove:Horizontal \
            {\
                background:transparent;\
                height:6px;\
            }\
            QSlider::handle:Horizontal \
            {\
                height: 30px;\
                width:8px;\
                border-image: url(:/images/ic_music_thumb.png);\
                margin: -8 0px; \
            }\
            ")

    def mousePressEvent(self, QMouseEvent):
        if QMouseEvent.button() == Qt.LeftButton:
            if self.orientation() == Qt.Vertical:
                self.set_position_value.emit(self.minimum() + ((self.maximum() - self.minimum()) * (self.height() - QMouseEvent.y())) / self.height())
            else:
                self.set_position_value.emit(self.minimum() + ((self.maximum() - self.minimum()) * QMouseEvent.x()) / self.width())
        return super().mousePressEvent(QMouseEvent)

    def keyPressEvent(self, *args, **kwargs):
        return super().keyPressEvent(*args, **kwargs)


if __name__ == '__main__':
    pass
