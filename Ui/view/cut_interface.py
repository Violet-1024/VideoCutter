import threading
import time

from qfluentwidgets import (PushButton, ToolTipFilter, SwitchButton, FluentIcon, ToggleButton, ToolButton,
                            LineEdit, InfoBarPosition, )
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import InfoBar
from PyQt5.QtCore import Qt, pyqtSignal, QUrl, QStandardPaths
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QWidget, QLabel, QFileDialog, QHBoxLayout

from Cut import cutbackend
from .gallery_interface import GalleryInterface
from .VideoShowWidget import VideoShowWidget

class CutInterface(GalleryInterface):
    def __init__(self, parent=None):
        super().__init__(
            title='剪辑',
            subtitle='对选择的视频进行剪辑',
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


        self.switchButton = SwitchButton(self.tr('否'))
        self.switchButton.checkedChanged.connect(self.onSwitchCheckedChanged)
        self.addExampleCard(
            self.tr('保留空白部分'),
            self.switchButton,
            ''
        )

        # tool tip
        button = PushButton(self.tr('剪辑'))
        button.installEventFilter(ToolTipFilter(button))
        button.setToolTip(self.tr('点击确认剪辑'))
        button.clicked.connect(self.cutFunc)
        self.addExampleCard(
            self.tr('按钮'),
            button,
            ''
        )


    def open_videoplayer(self):
        self.video_widget.show()

    def onSwitchCheckedChanged(self, isChecked):
        self.gv = self.getFilenameFromVideo()
        if isChecked:
            self.gv.keepBlank = True
            self.switchButton.setText(self.tr('是'))
        else:
            self.gv.keepBlank = False
            self.switchButton.setText(self.tr('否'))

    def getFilenameFromVideo(self):
        self.gv = self.video_widget.gv
        if self.gv.filename is not None:
            self.filename = self.gv.choose_filename
            self.show_line.setText(self.filename)
            return self.gv
        else:
            self.createErrorInfoBar()

    def cutFunc(self):
        file = self.filename
        # 监听函数运行
        thread = threading.Thread(target=cutbackend.CutBackend(file).cut())
        # thread = threading.Thread(target=self.test001)
        thread.start()
        self.createRunningInfoBar()
        while thread.is_alive():
            self.createRunningInfoBar()
            time.sleep(5)
        self.createFinishingInfoBar()

    # def test001(self):
    #     self.gv = self.getFilenameFromVideo()
    #     print(self.gv.keepBlank)

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
            title=self.tr('正在进行剪辑'),
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
            content=self.tr("剪辑完成"),
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=-1,
            parent=self
        )
