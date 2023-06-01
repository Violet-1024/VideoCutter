from Cut import transcribe
from Cut import subtitle
from Cut import cut
from Cut import dbconnect
from Cut import globalvariable

class CutBackend:

    def __init__(self, filename):
        self.filename = filename

    # 自动化的流程
    def autoCut(self):
        tra = transcribe.Transcribe(self.filename)
        cutter = cut.Cutter(self.filename)
        if globalvariable.useDb:
            tra.runWithDb()
            cutter.run()
            dbc = dbconnect.DatabaseConnector(self.filename)
            dbc.initDb()
            # 创建好了数据库，可以根据查到的数据库的内容进行配音等操作
        else:
            tra.run()
            cutter.run()
            # 只生成了文件，后序操作需要读文件

    # 每个步骤的函数
    def transcribe(self):
        tra = transcribe.Transcribe(self.filename)
        if globalvariable.useDb:
            tra.runWithDb()
        else:
            tra.run()

    def cut(self):
        cutter = cut.Cutter(self.filename)
        cutter.onlyCut()


    def subtitle(self):
        if globalvariable.useDb:
            sub = subtitle.Subtitle(self.filename)
            sub.onlySubtitle()
            dbc = dbconnect.DatabaseConnector(self.filename)
            dbc.initDb()
        else:
            sub = subtitle.Subtitle(self.filename)
            sub.onlySubtitle()







if __name__ == "__main__":
    CutBackend(filename="D:\python_dev\pycharm\VideoCutSoftware\TestForProject\测试一下.mp4").autoCut()
