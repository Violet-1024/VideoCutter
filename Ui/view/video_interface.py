# coding:utf-8
import time
import threading

from PyQt5.QtWidgets import QWidget, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer
from qfluentwidgets import (FluentIcon, ToolButton, PushButton, InfoBar, InfoBarPosition, LineEdit, ToggleButton)

from .gallery_interface import GalleryInterface
from .VideoShowWidget import VideoShowWidget
from Cut import cutbackend

class VideoInterface(GalleryInterface):

    def __init__(self, parent=None):
        super().__init__(
            title="自动剪辑",
            subtitle="导入视频，自动剪辑",
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

        self.autocut_button = ToggleButton(self.tr("自动剪辑"), self, FluentIcon.CUT)
        self.autocut_button.setFixedSize(150, 40)
        self.addExampleCard("自动剪辑", self.autocut_button, "")
        self.autocut_button.clicked.connect(self.autoCutFunc)


    def open_videoplayer(self):
        self.video_widget.show()

    def getFilenameFromVideo(self):
        self.gv = self.video_widget.gv
        if self.gv.filename is not None:
            self.filename = self.gv.choose_filename
            self.show_line.setText(self.filename)
        else:
            self.createErrorInfoBar()

    def autoCutFunc(self):
        file = self.filename
        # 监听函数运行
        self.createRunningInfoBar()
        thread = threading.Thread(target=cutbackend.CutBackend(file).autoCut)
        thread.start()

        self.progressTimer = QTimer()
        self.progressTimer.timeout.connect(lambda: self.updateProgress(thread, self.progressTimer))
        self.progressTimer.start(6000)

    def updateProgress(self, thread, progressTimer):
        # 更新进度
        self.createRunningInfoBar()

        if thread.is_alive():
            # 如果进程还在运行，延迟 6 秒后再次更新进度
            pass
        else:
            # 如果进程已经结束，更新完成信息
            progressTimer.stop()
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
            title=self.tr('正在自动剪辑'),
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
            content=self.tr("自动剪辑完成"),
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=-1,
            parent=self
        )



