import sys

from PyQt5.QtCore import Qt, QSize, QUrl
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel, QHBoxLayout, QFileDialog, QSizePolicy
from qfluentwidgets import (FluentIcon, PushButton, Slider, ToolButton)

from Cut import globalvariable

class VideoShowWidget(QFrame):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("VideoPlayer")
        self.setWindowIcon(QIcon(':/gallery/images/logo.png'))
        self.setObjectName("VideoShowWidget")

        self.gv = globalvariable.GlobalVariable(filename=None)

        self.add_button = ToolButton(FluentIcon.ADD)
        self.add_button.setFixedSize(60, 40)
        self.add_button.clicked.connect(self.choose_file)

        self.pause_button = PushButton(self.tr("暂停"))
        self.pause_button.setEnabled(False)
        self.pause_button.setFixedWidth(80)
        self.pause_button.clicked.connect(self.pause_video)

        self.show_label = QLabel(self)
        self.show_label.setAlignment(Qt.AlignCenter)

        self.video_show_widget = QVideoWidget(self)
        self.media_player = QMediaPlayer(self)
        self.media_player.setVideoOutput(self.video_show_widget)
        self.media_player.positionChanged.connect(self.update_slider)
        self.media_player.durationChanged.connect(self.set_duration)
        self.media_player.stateChanged.connect(self.media_state_changed)

        self.slider = Slider(Qt.Horizontal, self)
        self.slider.sliderPressed.connect(self.slider_pressed)
        self.slider.sliderReleased.connect(self.slider_released)
        self.slider.mousePressEvent = self.mouse_press_event

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.video_show_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.video_show_widget.setMinimumSize(400, 130)
        self.video_show_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.slider.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.setAcceptDrops(True)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.pause_button)
        button_layout.addWidget(self.slider)
        # button_layout.addStretch()

        video_layout = QVBoxLayout()
        video_layout.addWidget(self.add_button)
        video_layout.addWidget(self.show_label)
        video_layout.addWidget(self.video_show_widget)
        # video_layout.addStretch()
        video_layout.addLayout(button_layout)
        video_layout.update()

        self.setLayout(video_layout)

        # 设置VideoShowWidget的最小宽度和高度
        self.setMinimumSize(800, 600)

        # 调整布局和控件的大小策略
        video_layout.setContentsMargins(0, 0, 0, 0)
        video_layout.setSpacing(0)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(0)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.video_show_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


    def choose_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "选择视频", "", "视频文件 (*.mp4 *.avi)")
        if file_name:
            # self.show_label.setText(file_name)
            self.gv = globalvariable.GlobalVariable(file_name)
            self.show_label.setText(self.gv.filename)
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(file_name)))
            self.media_player.play()
            self.slider.setValue(0)
            self.slider.setEnabled(True)
            self.pause_button.setEnabled(True)
        self.pause_button.setText("暂停")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.isLocalFile() and url.toString().lower().endswith(('.mp4', '.avi')):
                    event.accept()
                    break

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_name = url.toLocalFile()
            self.gv = globalvariable.GlobalVariable(file_name)
            # self.show_label.setText(file_name)
            self.show_label.setText(self.gv.filename)

            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(file_name)))
            self.media_player.play()
            self.slider.setValue(0)
            self.slider.setEnabled(True)
            self.pause_button.setEnabled(True)
        self.pause_button.setText("暂停")

    def pause_video(self):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
            self.pause_button.setText("播放")
        else:
            self.media_player.play()
            self.pause_button.setText("暂停")

    def update_slider(self, position):
        if not self.slider.isSliderDown():
            self.slider.setValue(position)

    def slider_pressed(self):
        self.media_player.pause()

    def slider_released(self):
        self.media_player.setPosition(self.slider.value())
        self.media_player.play()

    def mouse_press_event(self, event):
        self.media_player.setPosition(self.slider.minimum() + (self.slider.maximum() - self.slider.minimum()) * event.pos().x() // self.slider.width())
        self.media_player.play()

    def set_duration(self, duration):
        self.slider.setRange(0, duration)

    def media_state_changed(self, state):
        if state == QMediaPlayer.StoppedState:
            self.media_player.setPosition(0)
            self.slider.setValue(0)
            self.pause_button.setText("暂停")
            self.pause_button.setEnabled(False)
            self.pause_button.setText("暂停")

    def sizeHint(self):
        return QSize(1000, 1000)

    def closeEvent(self, event):
        if self.gv.filename is not None:
            self.media_player.stop()
            self.media_player.deleteLater()
        event.accept()

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = VideoShowWidget()
#     window.show()
#     app.exec_()
#     # sys.exit(app.exec_())