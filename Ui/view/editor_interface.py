
from PyQt5.QtWidgets import QWidget, QHBoxLayout
from PyQt5.QtCore import Qt
from qfluentwidgets import (FluentIcon, ToolButton, PushButton, InfoBar, InfoBarPosition, LineEdit, ToggleButton)

from .gallery_interface import GalleryInterface
from .VideoShowWidget import VideoShowWidget
from Cut import utils
from .MarkdownEditorWidget import MarkdownEditor

class EditorInterface(GalleryInterface):
    def __init__(self, parent=None):
        super().__init__(
            title='编辑',
            subtitle='编辑转录出的srt字幕文件和markdown文件',
            parent=parent
        )

        self.filename = ''
        self.path = ''

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

        self.srt_button = PushButton(self.tr("打开srt文件"))
        self.srt_button.setFixedSize(150, 40)
        self.addExampleCard("编辑srt文件", self.srt_button, "")
        self.srt_button.clicked.connect(self.open_srtfile)

        self.markdown_button = PushButton(self.tr("打开markdown文件"))
        self.markdown_button.setFixedSize(150, 40)
        self.addExampleCard("编辑markdown文件", self.markdown_button, "")
        self.markdown_button.clicked.connect(self.open_markdownfile)

    def open_videoplayer(self):
        self.video_widget.show()

    def open_srtfile(self):
        self.path = utils.changeExt(self.filename, "srt")
        if not utils.checkExist(self.path, None):
            self.createErrorInfoBar()
        else:
            self.markdown_editor = MarkdownEditor(self.path)
            self.markdown_editor.show()

    def open_markdownfile(self):
        self.path = utils.changeExt(self.filename, "md")
        if not utils.checkExist(self.path, None):
            self.createErrorInfoBar()
        else:
            self.markdown_editor = MarkdownEditor(self.path)
            self.markdown_editor.show()

    def getFilenameFromVideo(self):
        self.gv = self.video_widget.gv
        if self.gv.filename is not None:
            self.filename = self.gv.choose_filename
            self.show_line.setText(self.filename)
        else:
            self.createErrorInfoBar()

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






