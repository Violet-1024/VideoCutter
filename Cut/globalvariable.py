import torch


class GlobalVariable:
    def __init__(self, filename, useDb=False, keepBlank=False, whisperModel="small", whisperDevice="cuda", subtitleSize:int = 60):
        self.useDb = useDb
        self.keepBlank = keepBlank

        # choose_filename = (r'D:\python_dev\pycharm\VideoCutSoftware\TestForProject\体验大疆无人机.mp4')
        self.filename = filename
        self.choose_filename = r"{}".format(self.filename)

        self.whisperModel = whisperModel
        # self.whisperModel = ["tiny", "base", "small", "medium", "large"]
        self.choose_whisperModel = self.whisperModel

        self.whisperDevice = whisperDevice
        # self.whisperDevice = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.choose_whisperDevice = self.whisperDevice

        self.subtitileSize = subtitleSize








