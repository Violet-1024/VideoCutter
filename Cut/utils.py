import os
import re



class MarkDown:
    def __init__(self, filename):
        self.lines = []
        self.filename = filename
        self.finish_mark = "<--  Mark if you have finished editing"

        if filename is not None:
            self.loadFile()


    def loadFile(self):
        if os.path.exists(self.filename):
            with open(self.filename, encoding="utf-8") as f:
                self.lines = f.readlines()


    def write(self):
        with open(self.filename, "wb") as f:
            f.write("\n".join(self.lines).encode("utf-8", "replace"))


    # 判断某一行line是否是可编辑若不是返回(None,line)
    def parseTask(self, line):
        m = re.match(r"- +\[([ x])\] +(.*)", line)
        if not m:
            return None, line
        return m.groups()[0].lower() == "x", m.groups()[1]

    # 获得上述函数的结果集
    def task(self):
        task_res = []
        for l in self.lines:
            mark, task = self.parseTask(l)
            if mark is not None:
                task_res.append((mark, task))
        return task_res


    def finishEditing(self):
        for m, t in self.task():
            if m and self.finish_mark in t:
                return True
        return False


    # 负责给markdown添加的一些函数
    def add(self, line):
        self.lines.append(line)

    def addVideo(self, video_filename):
        self.add(f'\n<video controls="true" allowfullscreen="true"> <source src="{video_filename}"> </video>\n')

    def addTask(self, mark, content):
        text = f'- [{"x" if mark else " "}] {content.strip()}'
        self.add(text+'  ')

    def addFinishEditing(self, mark):
        self.addTask(mark, self.finish_mark)


def checkExist(output, force):
    if os.path.exists(output):
        if not force:
            return True
    return False


def checkIsVideo(filename):
    _, ext = os.path.splitext(filename)
    return ext in [".mp4", ".avi", ".mov", ".mkv"]


def changeExt(filename, new_ext):
    base, _ = os.path.splitext(filename)
    if not new_ext.startswith("."):
        new_ext = "." + new_ext
    return base + new_ext

# 拓展语段长度使其连贯
def expandSegments(segments, expand_head, expand_tail, total_length):
    results = []
    for i in range(len(segments)):
        t = segments[i]
        start = max(t["start"] - expand_head, segments[i - 1]["end"] if i > 0 else 0)
        end = min(
            t["end"] + expand_tail,
            segments[i + 1]["start"] if i < len(segments) - 1 else total_length,
        )
        results.append({"start": start, "end": end})
    return results

 # 去除太短的语段
def removeShortSegments(segments, threshold):
    return [s for s in segments if s["end"] - s["start"] > threshold]

# 合并近的语段
def mergeAdjacentSegments(segments, threshold):
    results = []
    i = 0
    while i < len(segments):
        s = segments[i]
        for j in range(i + 1, len(segments)):
            if segments[j]["start"] < s["end"] + threshold:
                s["end"] = segments[j]["end"]
                i = j
            else:
                break
        i += 1
        results.append(s)
    return results


# 添加已剪辑后缀
def addCutMark(filename):
    base, ext = os.path.splitext(filename)
    if base.endswith("_cut"):
        base = base[:-4] + "_" + base[-4:]
    else:
        base = base + "_cut"
    return base + ext

# 添加加字幕后缀
def addSubtitleMark(filename):
    base, ext = os.path.splitext(filename)
    if base.endswith("_sub"):
        base = base[:-4] + "_" + base[-4:]
    else:
        base = base + "_sub"
    return base + ext

#不利用数据库去重
def removeDuplicate(text):

    for t in text:
        # 去除重复，保留后面的
        t.content = re.sub(r'\b(\w+)(?:\W+\1\b)+', r'\1', t.content, flags=re.IGNORECASE)
        text[t.index-1].content = t.content

    unique_sentences = {}  # 用字典保存去重后的句子和对应的id
    for t in text:
        if t.content != "<<--   NULL   -->>":
            if t.content not in unique_sentences:
                unique_sentences[t.content] = t.index
            else:
                # 已存在重复内容，保留后面的部分
                unique_sentences[t.content[-100:]] = t.index

    # 将去重后的结果转换为列表，并同时返回id列表
    unique_id_list = list(unique_sentences.values())
    return unique_id_list

# 保留空白
def removeDuplicateKeepBlank(text):

    for t in text:
        # 去除重复，保留后面的
        t.content = re.sub(r'\b(\w+)(?:\W+\1\b)+', r'\1', t.content, flags=re.IGNORECASE)
        text[t.index-1].content = t.content

    unique_sentences = {}  # 用字典保存去重后的句子和对应的id
    list_for_null = []
    for t in text:
        if t.content != "<<--   NULL   -->>":
            if t.content not in unique_sentences:
                unique_sentences[t.content] = t.index
            else:
                # 已存在重复内容，保留后面的部分
                unique_sentences[t.content[-100:]] = t.index
        else:
            list_for_null.append(t.index)

    # 将去重后的结果转换为列表，并同时返回id列表
    unique_id_list = list(unique_sentences.values())+list_for_null
    return unique_id_list



