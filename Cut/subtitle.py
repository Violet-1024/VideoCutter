import srt

from moviepy import editor
from moviepy.video.tools import subtitles

from Cut import transcribe
from Cut import utils
from Cut.globalvariable import GlobalVariable


#修改为magick.exe的本地路径
from moviepy.config import change_settings
change_settings({'IMAGEMAGICK_BINARY': r'D:\python_dev\pycharm\VideoCutSoftware\Needed\ImageMagick-7.1.1-Q16-HDRI\magick.exe'})

class Subtitle:
    def __init__(self, filename):
        self.filename = filename
        self.globalvariable = GlobalVariable(self.filename)

    def onlySubtitle(self):
        if not utils.checkExist(utils.changeExt(self.filename, 'srt'), None):
            tra = transcribe.Transcribe(self.filename)
            tra.runForSubtitle()

        srt_file = utils.changeExt(self.filename, "srt")
        with open(srt_file, encoding="utf-8") as f:
            sub = list(srt.parse(f.read()))

        if self.globalvariable.keepBlank:
            unique_id_list = utils.removeDuplicateKeepBlank(sub)
        else:
            unique_id_list = utils.removeDuplicate(sub)

        video_clip = editor.VideoFileClip(self.filename)

        text = []
        for s in sub:
            if s.index in unique_id_list:
                if s.content == "<<--   NULL   -->>":
                    s.content = ""
                # 遇到UnicodeDecodeError: 'utf-8' codec can't decode byte 0xb2 in position 8: invalid start byte
                # 修改VideoClip.py中的1177行， return [l.decode('UTF-8')[8:] for l in lines if l.startswith(b"  Font:")]
                # 最后的解决方法是在moviepy的config_defaults.py里手动加上magick.exe的路径,但是textclip对中文不太支持
                # 把utf-8换成ansi,并且在代码的工作目录中复制一份Windows/fonts中的能够显示中文的字体，在textclip里面加入属性
                # text_clip = editor.TextClip(s.content, font="Font\\simhei.ttf", fontsize=self.globalvariable.subtitileSize,
                #                             color='white',)
                text_clip = editor.TextClip(s.content, font=r"../Font/simsun.ttc",
                                            fontsize=self.globalvariable.subtitileSize,
                                            color='white')
                text_clip = text_clip.set_position(('center', 'bottom'))
                text_clip = text_clip.set_start(s.start.seconds)
                text_clip = text_clip.set_end(s.end.seconds)
                text.append(text_clip)

        final_clip = editor.CompositeVideoClip([video_clip, *text])
        output_filename = utils.changeExt(utils.addSubtitleMark(self.filename), "mp4")
        final_clip.write_videofile(output_filename, audio_codec="aac", bitrate="10m")


    def addSubtitle(self):
        srt_file = utils.changeExt(self.filename, "srt")
        with open(srt_file, encoding="utf-8") as f:
            sub = list(srt.parse(f.read()))

        if self.globalvariable.keepBlank:
            unique_id_list = utils.removeDuplicateKeepBlank(sub)
        else:
            unique_id_list = utils.removeDuplicate(sub)

        # video_clip = editor.VideoFileClip(self.filename)

        text = []
        for s in sub:
            if s.index in unique_id_list:
                if s.content == "<<--   NULL   -->>":
                    s.content = ""
                # 遇到UnicodeDecodeError: 'utf-8' codec can't decode byte 0xb2 in position 8: invalid start byte
                # 修改VideoClip.py中的1177行， return [l.decode('UTF-8')[8:] for l in lines if l.startswith(b"  Font:")]
                # 最后的解决方法是在moviepy的config_defaults.py里手动加上magick.exe的路径,但是textclip对中文不太支持
                # 把utf-8换成ansi,并且在代码的工作目录中复制一份Windows/fonts中的能够显示中文的字体，在textclip里面加入属性
                text_clip = editor.TextClip(s.content, font=r'../Font/simhei.ttf',
                                            fontsize=self.globalvariable.subtitileSize,
                                            color='white')
                # text_clip = editor.TextClip(s.content, font="Font\\simhei.ttf",
                #                             fontsize=self.globalvariable.subtitileSize,
                #                             color='white')
                text_clip = text_clip.set_position(('center', 'bottom'))
                text_clip = text_clip.set_start(s.start.seconds)
                text_clip = text_clip.set_end(s.end.seconds)
                text.append(text_clip)

        return text



    #使用本身自带的subtitles函数来进行，但是缺点是unicode错误更不易修改成功
    def funcForSubtitleTest(self):
        srt_file = utils.changeExt(self.filename, "srt")
        video_clip = editor.VideoFileClip(self.filename)

        sub = subtitles.SubtitlesClip(srt_file)
        sub = sub.set_position(('center', 'bottom'))

        final_clip = editor.CompositeVideoClip([video_clip, sub])
        output_filename = utils.changeExt(utils.addSubtitleMark(self.filename), "mp4")
        final_clip.write_videofile(output_filename, audio_codec="aac", bitrate="10m")

if __name__ == "__main__":
    Subtitle(r"D:\python_dev\pycharm\VideoCutSoftware\TestForProject\新闻.mp4").onlySubtitle()

