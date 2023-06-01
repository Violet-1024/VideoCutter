import datetime
import opencc
import os

import srt
import torch
import whisper
from Cut import utils, dbconnect
from Cut.globalvariable import GlobalVariable
from tqdm import tqdm

import warnings
warnings.simplefilter("ignore")


class Transcribe:
    def __init__(self, filename):
        self.whisper_model = None
        self.sampling_rate = 16000
        self.is_force = False
        self.detect_speech = None

        # 要修改成一个能循环的,重点是filename的导入和循环导入
        self.filename = filename
        self.globalvariable = GlobalVariable(self.filename)


    def run(self):
        # 拼接的时候需要元组，所以需要使用name，_
        name, _ = os.path.splitext(self.filename)

        # 加载视频/音频
        video = whisper.load_audio(self.filename, sr=self.sampling_rate)

        voice_timestamp = self.detectVoiceActivity(video)

        result = self.doTranscribe(video, voice_timestamp)

        output_srt = name + ".srt"
        self.saveSRT(output_srt, result)
        output_md = name + ".md"
        self.saveMarkDown(output_md, output_srt)


    def runWithDb(self):
        # 拼接的时候需要元组，所以需要使用name，_
        name, _ = os.path.splitext(self.filename)

        # 加载视频/音频
        video = whisper.load_audio(self.filename, sr=self.sampling_rate)

        voice_timestamp = self.detectVoiceActivity(video)

        result = self.doTranscribe(video, voice_timestamp)

        output_srt = name + ".srt"
        self.saveSRT(output_srt, result)
        output_md = name + ".md"
        self.saveMarkDownUseDb(output_md)


    def runForSubtitle(self):
        # 拼接的时候需要元组，所以需要使用name，_
        name, _ = os.path.splitext(self.filename)

        # 加载视频/音频
        video = whisper.load_audio(self.filename, sr=self.sampling_rate)

        voice_timestamp = self.detectVoiceActivity(video)

        result = self.doTranscribe(video, voice_timestamp)

        output_srt = name + ".srt"
        self.saveSRT(output_srt, result)

    def detectVoiceActivity(self, audio):
        if self.detect_speech is None:
            torch.hub._validate_not_a_forked_repo = lambda a, b, c: True
            vad_model, funcs = torch.hub.load(
                repo_or_dir="Needed\\model\\snakers4_silero-vad_master\\", model="silero_vad", trust_repo=True, source='local'
            )

            self.detect_speech = funcs[0]

        speeches = self.detect_speech(
            audio, vad_model, sampling_rate=self.sampling_rate
        )

        # 去除太短的语段
        speeches = utils.removeShortSegments(speeches, 1.0 * self.sampling_rate)

        # 拓展语段长度使其连贯
        speeches = utils.expandSegments(
            speeches, 0.2 * self.sampling_rate, 0.0 * self.sampling_rate, audio.shape[0]
        )

        # 合并近的语段
        speeches = utils.mergeAdjacentSegments(speeches, 0.5 * self.sampling_rate)

        return speeches if len(speeches) > 1 else [{"start": 0, "end": len(audio)}]


    # 转录语音
    def doTranscribe(self, video, voice_timestamp):

        # 加载模型
        # self.whisper_model = whisper.load_model(globalvariable.choose_whisperModel, device=globalvariable.choose_whisperDevice)
        self.whisper_model = whisper.load_model(self.globalvariable.choose_whisperModel, self.globalvariable.choose_whisperDevice)

        transcribe_result = []
        for seg in (
            voice_timestamp
            if len(voice_timestamp) == 1
            else tqdm(voice_timestamp)
        ):
            r = self.whisper_model.transcribe(video[int(seg["start"]): int(seg["end"])], task="transcribe")
            r["origin_timestamp"] = seg
            transcribe_result.append(r)
        return transcribe_result


    # 保存为srt字幕文件的函数
    def saveSRT(self, output_srt, result):

        # 使用opencc繁转简
        cc = opencc.OpenCC('t2s')

        subtitle = []

        # 添加时间和文字的函数
        def AddSubtitle(start, end, text):
            subtitle.append(
                srt.Subtitle(
                    index=0,
                    # 获得时间差值，去除text空格
                    start=datetime.timedelta(seconds=start),
                    end=datetime.timedelta(seconds=end),
                    content=cc.convert(text.strip()),
                )
            )

        prev_end = 0
        for r in result:
            origin = r["origin_timestamp"]
            for s in r["segments"]:
                start = s["start"] + origin["start"] / self.sampling_rate
                end = min(
                    s["end"] + origin["start"] / self.sampling_rate,
                    origin["end"] / self.sampling_rate
                )
                if start > end:
                    continue

                # 标记超过1s的空白段
                if start > prev_end + 1.0:
                    AddSubtitle(prev_end, start, "<<--   NULL   -->>")
                AddSubtitle(start, end, s["text"])

                prev_end = end

        with open(output_srt, "wb") as f:
            f.write(srt.compose(subtitle).encode("utf-8", "replace"))


    # 转成可编辑的markdown文件
    def saveMarkDown(self, output_md, output_srt):
        with open(output_srt, encoding="utf-8") as f:
            sub = list(srt.parse(f.read()))
        if self.globalvariable.keepBlank:
            unique_id_list = utils.removeDuplicateKeepBlank(sub)
        else:
            unique_id_list = utils.removeDuplicate(sub)

        markdown = utils.MarkDown(output_md)
        # markdown.addVideo(os.path.basename(self.filename))
        # markdown.add(f"\nThis MarkDown file generated from [{os.path.basename(output_srt)}]({os.path.basename(output_srt)}).")
        markdown.addFinishEditing(True)

        for s in sub:
            if s.index in unique_id_list:
                second = s.start.seconds
                pre = f"[{s.index},{second // 60:02d}:{second % 60:02d}]"
                markdown.addTask(True, f"{pre:12} {s.content.strip()}"+'  ')
            else:
                second = s.start.seconds
                pre = f"[{s.index},{second // 60:02d}:{second % 60:02d}]"
                markdown.addTask(False, f"{pre:12} {s.content.strip()}"+'  ')

        markdown.write()

    # 转成可编辑的markdown文件
    def saveMarkDownUseDb(self, output_md):
        # 初始化数据库
        db = dbconnect.DatabaseConnector(self.filename)
        db.initDb()
        sub = db.selectAllAttribute()
        if self.globalvariable.keepBlank:
            unique_id_list = db.removeSentenceDuplicateKeepBlank()
        else:
            unique_id_list = db.removeSentenceDuplicate()

        name, _ = os.path.splitext(self.filename)
        output_srt = name + ".srt"
        markdown = utils.MarkDown(output_md)
        # markdown.addVideo(os.path.basename(self.filename))
        # markdown.add(
        #   f"\nThis MarkDown file generated from [{os.path.basename(output_srt)}]({os.path.basename(output_srt)}).")
        markdown.addFinishEditing(True)

        for index, starttime, content in sub:
            if index in unique_id_list:
                pre = f"[{index},{starttime}]"
                markdown.addTask(True, f"{pre:12} {content.strip()}"+'  ')
            else:
                pre = f"[{index},{starttime}]"
                markdown.addTask(False, f"{pre:12} {content.strip()}"+'  ')

        markdown.write()

if __name__ == "__main__":
    Transcribe(filename=r'D:\python_dev\pycharm\VideoCutSoftware\TestForProject\111.avi').run()
