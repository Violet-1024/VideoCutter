# coding:utf-8
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPixmap, QPainter, QColor, QBrush, QPainterPath
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

from qfluentwidgets import ScrollArea, isDarkTheme, FluentIcon
from ..common.config import cfg, HELP_URL, REPO_URL, EXAMPLE_URL, FEEDBACK_URL
# from ..common.icon import Icon, FluentIconBase
from ..components.link_card import LinkCardView
from ..components.sample_card import SampleCardView
from ..common.style_sheet import StyleSheet


class BannerWidget(QWidget):
    """ Banner widget """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setFixedHeight(336)
        self.vBoxLayout = QVBoxLayout(self)
        self.galleryLabel = QLabel('VideoCutter', self)
        self.banner = QPixmap(':/gallery/images/header1.png')
        self.linkCardView = LinkCardView(self)

        self.galleryLabel.setObjectName('galleryLabel')

        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(0, 20, 0, 0)
        self.vBoxLayout.addWidget(self.galleryLabel)
        self.vBoxLayout.addWidget(self.linkCardView, 1, Qt.AlignBottom)
        self.vBoxLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # self.linkCardView.addCard(
        #     ':/gallery/images/logo.png',
        #     self.tr('Getting started'),
        #     self.tr('An overview of app development options and samples.'),
        #     HELP_URL
        # )

        self.linkCardView.addCard(
            FluentIcon.GITHUB,
            self.tr('GitHub 仓库'),
            self.tr(
                '访问VideoCutter的Github仓库'),
            REPO_URL
        )

    def paintEvent(self, e):
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setRenderHints(
            QPainter.SmoothPixmapTransform | QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)

        path = QPainterPath()
        path.setFillRule(Qt.WindingFill)
        w, h = self.width(), 200
        path.addRoundedRect(QRectF(0, 0, w, h), 10, 10)
        path.addRect(QRectF(0, h-50, 50, 50))
        path.addRect(QRectF(w-50, 0, 50, 50))
        path.addRect(QRectF(w-50, h-50, 50, 50))
        path = path.simplified()

        # draw background color
        painter.fillPath(path, QColor(206, 216, 228))

        # draw banner image
        pixmap = self.banner.scaled(
            self.size(), transformMode=Qt.SmoothTransformation)
        path.addRect(QRectF(0, h, w, self.height() - h))
        painter.fillPath(path, QBrush(pixmap))


class HomeInterface(ScrollArea):
    """ Home interface """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.banner = BannerWidget(self)
        self.view = QWidget(self)
        self.vBoxLayout = QVBoxLayout(self.view)

        self.__initWidget()
        self.loadSamples()

    def __initWidget(self):
        self.view.setObjectName('view')
        StyleSheet.HOME_INTERFACE.apply(self)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidget(self.view)
        self.setWidgetResizable(True)

        self.vBoxLayout.setContentsMargins(0, 0, 0, 36)
        self.vBoxLayout.setSpacing(40)
        self.vBoxLayout.addWidget(self.banner)
        self.vBoxLayout.setAlignment(Qt.AlignTop)

    def loadSamples(self):
        """ load samples """
        # 导入视频
        importView = SampleCardView(
            self.tr("导入视频"), self.view)
        importView.addSampleCard(
            icon=FluentIcon.MOVIE,
            title="视频",
            content=self.tr(
                "选择或拖入区域以导入视频"),
            routeKey="videoInterface",
            index=0
        )
        importView.addSampleCard(
            icon=FluentIcon.MEDIA,
            title="自动剪辑",
            content=self.tr(
                "按照默认设置对视频自动剪辑，生成去重去空白的带字幕的视频"),
            routeKey="videoInterface",
            index=2
        )
        self.vBoxLayout.addWidget(importView)

        # 语音识别
        transcribeView = SampleCardView(self.tr('语音识别'), self.view)
        transcribeView.addSampleCard(
            icon=FluentIcon.MICROPHONE,
            title="语音识别",
            content=self.tr(
                "使用whisper模型识别语音并转录"),
            routeKey="transcribeInterface",
            index=0
        )
        self.vBoxLayout.addWidget(transcribeView)

        # 文件编辑
        editorView = SampleCardView(self.tr('文件编辑'), self.view)
        editorView.addSampleCard(
            icon=FluentIcon.EDIT,
            title="编辑文件",
            content=self.tr("对转录出的文件进行编辑"),
            routeKey="editorInterface",
            index=0
        )
        self.vBoxLayout.addWidget(editorView)

        # 添加字幕
        subtitleView = SampleCardView(self.tr('添加字幕'), self.view)
        subtitleView.addSampleCard(
            icon=FluentIcon.FONT,
            title="添加字幕",
            content=self.tr(
                "读srt字幕文件，给视频添加字幕"),
            routeKey="subtitleInterface",
            index=0
        )
        self.vBoxLayout.addWidget(subtitleView)

        # 视频剪辑
        cutView = SampleCardView(self.tr('视频剪辑'), self.view)
        cutView.addSampleCard(
            icon=FluentIcon.CUT,
            title="视频剪辑",
            content=self.tr(
                "读markdown文件得到要保留的line，进行视频的分片和合并"),
            routeKey="cutInterface",
            index=0
        )
        self.vBoxLayout.addWidget(cutView)



        # # 自动剪辑
        # autocutView = SampleCardView(self.tr('自动剪辑'), self.view)
        # autocutView.addSampleCard(
        #     icon=FluentIcon.MEDIA,
        #     title="自动剪辑",
        #     content=self.tr(
        #         "按照默认设置对视频自动剪辑，生成去重去空白的带字幕的视频"),
        #     routeKey="autocInterface",
        #     index=0
        # )
        # self.vBoxLayout.addWidget(autocutView)
