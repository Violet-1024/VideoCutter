import os
import markdown2
from PyQt5.QtGui import QIcon

from PyQt5.QtWidgets import QWidget,  QVBoxLayout
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from qfluentwidgets import MessageBox, TextEdit


class CheckFileWorker(QObject):
    update = pyqtSignal(str)

    def __init__(self, path):
        super().__init__()

        self.path = path
        self.stop_checking = False

    def run(self):
        old_text = self.read_markdown_file()

        while not self.stop_checking:
            new_text = self.read_markdown_file()
            if not old_text == new_text:
                self.update.emit(new_text)
                old_text = new_text

    def read_markdown_file(self):
        with open(self.path, "r", encoding="utf-8") as file:
            return file.read()

    def stop(self):
        self.stop_checking = True


class MarkdownEditor(QWidget):
    def __init__(self, path, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.path = path
        self.setWindowTitle("Markdown Editor")
        self.setWindowIcon(QIcon(':/gallery/images/logo.png'))
        self.setObjectName("MarkdownEditorWidget")

        self.setLayout(QVBoxLayout())

        # self.input_editor = QTextEdit(self,
        #                               placeholderText="write here",
        #                               lineWrapColumnOrWidth=100,
        #                               readOnly=False,
        #                               acceptRichText=False)
        self.input_editor = TextEdit(self)
        self.input_editor.setHtml(self.read_markdown_file())

        self.layout().addWidget(self.input_editor)

        self.init_thread()

    def init_thread(self):
        self.thread = QThread()
        self.worker = CheckFileWorker(self.path)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)

        self.worker.update.connect(self.update_markdown)

        self.thread.start()

    def closeEvent(self, event):

        title = self.tr("关闭MarkdownEditor")
        content = self.tr('是否保存文件')
        w = MessageBox(title, content, self.window())
        w.show()
        if w.exec_():
            self.savefile()
            self.worker.stop()
            self.worker.deleteLater()

            self.thread.quit()
            self.thread.deleteLater()
        else:
            self.worker.stop()
            self.worker.deleteLater()

            self.thread.quit()
            self.thread.deleteLater()

        event.accept()

    def read_markdown_file(self):
        newline = os.linesep
        with open(self.path, "r", newline=newline, encoding="utf-8") as file:
            return self.markdown_to_html(file.read())

    def update_markdown(self, md_text):
        self.input_editor.setHtml(self.markdown_to_html(md_text))

    def markdown_to_html(self, text: str) -> str:
        text = markdown2.markdown(text, extras=["break-on-newline"])
        return text

    def savefile(self):
        newline = os.linesep
        with open(self.path, 'w', newline=newline, encoding='utf-8') as f:
            # f.write(self.input_editor.setHtml(text))
            f.write(self.input_editor.toPlainText())


# if __name__ == '__main__':
#     PATH = "D:\python_dev\pycharm\VideoCutSoftware\TestForProject\体验大疆无人机.srt"
#
#     app = QApplication(sys.argv)
#
#     markdown_previewer_dialog = MarkdownEditor(PATH)
#     markdown_previewer_dialog.show()
#
#     sys.exit(app.exec_())
