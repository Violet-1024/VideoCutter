import time
import threading

from PyQt5.QtWidgets import QWidget, QHBoxLayout
from PyQt5.QtCore import Qt
from qfluentwidgets import (FluentIcon, ToolButton, PushButton, InfoBar, InfoBarPosition, LineEdit,
                            ToolTipFilter, SpinBox)

from .gallery_interface import GalleryInterface
from .VideoShowWidget import VideoShowWidget
from Cut import cutbackend


class SubtitleInterface(GalleryInterface):
    def __init__(self, parent=None):
        super().__init__(
            title='字幕',
            subtitle='为选择的视频添加字幕',
            parent=parent
        )

        self.filename = ''

        self.add_button = ToolButton(FluentIcon.ADD)
        self.add_button.setFixedSize(70, 40)
        self.addExampleCard("视频导入", self.add_button, "")
        self.add_button.clicked.connect(self.open_videoplayer)

        self.video_widget = VideoShowWidget()
        self.gv = self.video_widget.gv

        self.w = QWidget(self)
        # self.show_line = QLabel(self)
        self.show_line = LineEdit(self)
        self.show_line.setClearButtonEnabled(True)
        self.show_line.setFixedSize(700, 40)
        self.show_button = PushButton(self.tr("获得视频地址"))
        self.show_button.clicked.connect(self.getFilenameFromVideo)

        wlayout = QHBoxLayout(self.w)
        wlayout.addWidget(self.show_button)
        wlayout.addStretch()
        wlayout.addWidget(self.show_line)
        self.addExampleCard("点击按钮获得视频地址", self.w, '')

        # spin box
        self.spinbox = SpinBox()
        self.addExampleCard(
            title=self.tr("选择字幕字号大小,推荐大小为60"),
            widget=self.spinbox,
            sourcePath=''
        )

        button = PushButton(self.tr('添加字幕'))
        button.setToolTip(self.tr('点击确认为视频添加字幕'))
        button.clicked.connect(self.subtitleFunc)
        self.addExampleCard(
            self.tr('按钮'),
            button,
            ''
        )

    def open_videoplayer(self):
        self.video_widget.show()

    def getFilenameFromVideo(self):
        self.gv = self.video_widget.gv
        if self.gv.filename is not None:
            self.filename = self.gv.choose_filename
            self.show_line.setText(self.filename)
            return self.gv
        else:
            self.createErrorInfoBar()

    def subtitleFunc(self):
        file = self.filename
        # 监听函数运行
        self.createRunningInfoBar()
        thread = threading.Thread(target=cutbackend.CutBackend(file).subtitle)
        thread.start()

        while thread.is_alive():
            self.createRunningInfoBar()
            time.sleep(5)
        self.createFinishingInfoBar()


    def createErrorInfoBar(self):
        InfoBar.error(
            title=self.tr('错误'),
            content=self.tr("未选择文件或文件不存在"),
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=-1,  # won't disappear automatically
            parent=self
        )

    def createRunningInfoBar(self):
        InfoBar.info(
            title=self.tr('正在添加字幕'),
            content=self.tr("请等待"),
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=5000,
            parent=self
        )

    def createFinishingInfoBar(self):
        InfoBar.success(
            title=self.tr('完成'),
            content=self.tr("添加字幕完成"),
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=-1,
            parent=self
        )



