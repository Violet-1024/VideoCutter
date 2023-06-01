import os
import re

import srt

from moviepy import editor
from Cut import utils, subtitle


class Cutter:
    def __init__(self, filename):
        # 与transcribe一样的问题，filename的循环以及参数化
        self.filename = [filename, utils.changeExt(filename, 'srt'), utils.changeExt(filename, 'md')]
        # self.filename = [("D:\python_dev\pycharm\VideoCutSoftware\TestForProject\地表最快保时捷.mp4"),
        #                  ("D:\python_dev\pycharm\VideoCutSoftware\TestForProject\地表最快保时捷.srt"),
        #                  ("D:\python_dev\pycharm\VideoCutSoftware\TestForProject\地表最快保时捷.md")]
        self.output_filename_cut = ''

    def run(self):
        files = {"srt": None, "video": None, "md": None}
        for fn in self.filename:
            ext = os.path.splitext(fn)[1][1:]
            files[ext if ext in files else "video"] = fn

        if utils.checkIsVideo(files["video"]):
            self.output_filename_cut = utils.changeExt(utils.addCutMark(files["video"]), "mp4")
            if utils.checkExist(self.output_filename_cut, None):
                return

        with open(files["srt"], encoding="utf-8") as f:
            subtitles = list(srt.parse(f.read()))
        if files["md"]:
            markdown = utils.MarkDown(files["md"])
            if not markdown.finishEditing():
                return
            index = []
            for mark, sentence in markdown.task():
                if not mark:
                    continue
                m = re.match(r"\[(\d+)", sentence.strip())
                if m:
                    index.append(int(m.groups()[0]))
            subt = [s for s in subtitles if s.index in index]
            # 避免字幕出现混乱
            subt.sort(key=lambda x:x.start)



        segment = []
        for x in subt:
            if len(segment) == 0:
                segment.append(
                    {"start": x.start.total_seconds(), "end": x.end.total_seconds()}
                )
            else:
                if x.start.total_seconds() - segment[-1]["end"] < 0.5:
                    segment[-1]["end"] = x.end.total_seconds()
                else:
                    segment.append(
                        {"start": x.start.total_seconds(), "end": x.end.total_seconds()}
                    )

        video = editor.VideoFileClip(files["video"])

        subs = subtitle.Subtitle(self.filename[0])
        text = subs.addSubtitle()

        video = editor.CompositeVideoClip([video, *text])

        clips = [video.subclip(s["start"], s["end"]) for s in segment]

        final_clip: editor.VideoClip = editor.concatenate_videoclips(clips)
        audio = final_clip.audio.set_fps(44100)
        final_clip = final_clip.without_audio().set_audio(audio)
        final_clip = final_clip.fx(editor.afx.audio_normalize)


        output_filename = utils.addSubtitleMark(self.output_filename_cut)
        final_clip.write_videofile(output_filename, audio_codec="aac", bitrate="10m")

        video.close()


    # 只进行剪辑操作，不添加字幕
    def onlyCut(self):
        files = {"srt": None, "video": None, "md": None}
        for fn in self.filename:
            ext = os.path.splitext(fn)[1][1:]
            files[ext if ext in files else "video"] = fn

        if utils.checkIsVideo(files["video"]):
            self.output_filename_cut = utils.changeExt(utils.addCutMark(files["video"]), "mp4")
            if utils.checkExist(self.output_filename_cut, None):
                return

        with open(files["srt"], encoding="utf-8") as f:
            subtitles = list(srt.parse(f.read()))
        if files["md"]:
            markdown = utils.MarkDown(files["md"])
            if not markdown.finishEditing():
                return
            index = []
            for mark, sentence in markdown.task():
                if not mark:
                    continue
                m = re.match(r"\[(\d+)", sentence.strip())
                if m:
                    index.append(int(m.groups()[0]))
            subt = [s for s in subtitles if s.index in index]
            # 避免字幕出现混乱
            subt.sort(key=lambda x:x.start)

        segment = []
        for x in subtitles:
            if len(segment) == 0:
                segment.append(
                    {"start": x.start.total_seconds(), "end": x.end.total_seconds()}
                )
            else:
                if x.start.total_seconds() - segment[-1]["end"] < 0.5:
                    segment[-1]["end"] = x.end.total_seconds()
                else:
                    segment.append(
                        {"start": x.start.total_seconds(), "end": x.end.total_seconds()}
                    )

        video = editor.VideoFileClip(files["video"])


        clips = [video.subclip(s["start"], s["end"]) for s in segment]
        final_clip: editor.VideoClip = editor.concatenate_videoclips(clips)
        audio = final_clip.audio.set_fps(44100)
        final_clip = final_clip.without_audio().set_audio(audio)
        final_clip = final_clip.fx(editor.afx.audio_normalize)

        output_filename = utils.addSubtitleMark(self.output_filename_cut)
        final_clip.write_videofile(output_filename, audio_codec="aac", bitrate="10m")

        video.close()


if __name__=="__main__":
    Cutter(r"D:\python_dev\pycharm\VideoCutSoftware\TestForProject\123.mp4").run()


