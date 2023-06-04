import threading
import time

from qfluentwidgets import (InfoBar, ComboBox, SwitchButton, PushButton, InfoBarPosition, LineEdit, ToolButton,
                            FluentIcon)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QWidget, QHBoxLayout
from Cut import cutbackend
from .gallery_interface import GalleryInterface
from .VideoShowWidget import VideoShowWidget

class TranscribeInterface(GalleryInterface):
    def __init__(self, parent=None):
        super().__init__(
            title='转录',
            subtitle='使用whisper模型对视频进行语音识别',
            parent=parent
        )

        self.filename = ''

        self.add_button = ToolButton(FluentIcon.ADD)
        self.add_button.setFixedSize(70, 40)
        self.addExampleCard("视频导入", self.add_button, "")
        self.add_button.clicked.connect(self.open_videoplayer)

        self.video_widget = VideoShowWidget()
        self.gv = self.video_widget.gv

        self.video_widget = VideoShowWidget()
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

        self.model = ComboBox()
        self.model.setObjectName("model")
        self.model.addItems(["tiny", "base", "small", "medium", "large"])
        self.model.setCurrentIndex(2)
        self.model.currentIndexChanged.connect(self.changeModel)
        self.model.setMinimumWidth(210)
        self.addExampleCard(
            self.tr('模型大小'),
            self.model,
            ''
        )

        self.device = ComboBox()
        self.device.setObjectName("device")
        self.device.addItems(["CPU", "GPU"])
        self.device.setCurrentIndex(1)
        self.device.currentIndexChanged.connect(self.changeDevice)
        self.device.setMinimumWidth(210)
        self.addExampleCard(
            self.tr('使用硬件'),
            self.device,
            ''
        )

        self.switchButton = SwitchButton(self.tr('否'))
        self.switchButton.checkedChanged.connect(self.onSwitchCheckedChanged)
        self.addExampleCard(
            self.tr('保存到数据库中'),
            self.switchButton,
            ''
        )

        self.pushbutton = PushButton(self.tr("转录"))
        self.pushbutton.clicked.connect(self.transcribeFunc)
        self.addExampleCard(
            self.tr("开始转录"),
            self.pushbutton,
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

    def onSwitchCheckedChanged(self, isChecked):
        self.gv = self.getFilenameFromVideo()
        if self.gv is None:
            self.createErrorInfoBar()
        if isChecked:
            self.gv.useDb = True
            self.switchButton.setText(self.tr('是'))
        else:
            self.gv.useDb = False
            self.switchButton.setText(self.tr('否'))

    def changeModel(self):
        self.gv = self.getFilenameFromVideo()
        self.gv.whisperModel = self.findChild(ComboBox, "model").currentText()

    def changeDevice(self):
        self.gv = self.getFilenameFromVideo()
        self.gv.whisperDevice = self.findChild(ComboBox, "device").currentText()

    def transcribeFunc(self):
        self.gv = self.getFilenameFromVideo()
        file = self.gv.filename
        # 监听函数运行
        self.createRunningInfoBar()
        thread = threading.Thread(target=cutbackend.CutBackend(file).transcribe)
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
            content=self.tr("未选择文件或文件不存在,请先获取文件地址"),
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=-1,  # won't disappear automatically
            parent=self
        )

    def createRunningInfoBar(self):
        InfoBar.info(
            title=self.tr('正在转录'),
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
            content=self.tr("转录完成"),
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=-1,
            parent=self
        )



