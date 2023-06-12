# VideoCutter


## 使用

- 安装必要的库和模型
- 按照流程顺序进行操作即可

- 你可以做任何使用


## 注意

- 如果想要在windows环境下正常为视频添加中文的字幕，首先需要复制字体文件到某个目录中，然后编辑moviepy库中的videoclip.py文件的第1177行，return [l.decode('UTF-8')[8:] for l in lines if l.startswith(b"  Font:")]，把其中的“utf-8”编码改为“ansi”编码

- 若遇到UnicodeDecodeError: 'utf-8' codec can't decode byte 0xb2 in position 8: invalid start byte，解决方法如上

- 若程序不能正常运行，且弹出无响应，大概率是因为文件选择冲突或没有选择恰当的文件请重新尝试

- edit中的markdown编辑器会自动删除markdown语法中的空格（已解决，使用markdown2.markdown(text, extras=["break-on-newline"]) ）

- edit中的markdown编辑器在由markdown文件转换为html视图时不能正常识别- [ ] 的 -


## 感谢

[GitHub - mli/autocut: 用文本编辑器剪视频 (github.com)](https://github.com/mli/autocut)

[GitHub - zhiyiYo/PyQt-Fluent-Widgets: A fluent design widgets library based on PyQt/PySide. (github.com)](https://github.com/zhiyiYo/PyQt-Fluent-Widgets)
