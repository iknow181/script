# 批量识别文件类型并修改扩展名工具

## 项目简介

本项目提供了一个基于Python和Tkinter的图形界面工具，用于批量检测指定文件夹内文件的真实MIME类型，并根据检测结果自动修改文件扩展名。
 支持多种常见文件类型（PDF、图片、Office文档、压缩包等），解决文件扩展名错误导致无法正常打开的问题。

------

## 功能特点

- 递归扫描指定文件夹内所有文件
- 使用libmagic（python-magic）检测文件真实MIME类型
- 自动根据MIME类型推荐并修改文件扩展名
- 跳过已正确扩展名的文件，避免重复改名
- 处理过程中实时日志显示，记录成功、跳过及失败的文件数
- 处理完成后显示各MIME类型统计和整体处理结果
- 友好的图形界面，支持目录选择和进度显示

------

## 依赖环境

- Python 3.6及以上
- [python-magic](https://github.com/ahupp/python-magic) 库（用于文件类型检测）
- Tkinter（Python标准GUI库，通常默认安装）

### 安装依赖示例

```
pip install python-magic
```

**注意：**

- Windows用户安装python-magic时可能需要额外安装[libmagic](https://github.com/julian-r/python-magic#windows)二进制支持。
- Linux/macOS用户一般直接安装python-magic即可。

------

## 使用说明

1. 运行 `python your_script.py` 启动图形界面。
2. 点击“浏览”按钮选择目标文件夹。
3. 点击“开始识别并改名”按钮，程序开始递归扫描文件并修改扩展名。
4. 进度条显示当前处理进度，文本框显示详细日志。
5. 处理完成后会弹出总结对话框，显示文件总数、成功改名数、跳过数、失败数及耗时。
6. 下方另有文件类型统计展示。

------

## 文件类型与扩展名映射（部分）

| MIME类型                                                     | 扩展名 |
| ------------------------------------------------------------ | ------ |
| application/pdf                                              | .pdf   |
| image/png                                                    | .png   |
| image/jpeg                                                   | .jpg   |
| text/plain                                                   | .txt   |
| application/zip                                              | .zip   |
| application/msword                                           | .doc   |
| application/vnd.openxmlformats-officedocument.wordprocessingml.document | .docx  |
| application/vnd.ms-excel                                     | .xls   |
| application/vnd.openxmlformats-officedocument.spreadsheetml.sheet | .xlsx  |
| application/octet-stream                                     | .bin   |



------

## 代码结构简述

- `detect_and_rename_file(filepath, text_widget)`：检测单个文件类型并尝试重命名。
- `process_folder(folder_path, text_widget, root_widget)`：遍历文件夹并处理所有文件。
- Tkinter部分实现文件夹选择、日志显示、进度条等UI组件。

------

## 常见问题

- **文件无法识别或扩展名错误？**
   可能是该文件类型不在预设映射表中，可自行扩展`MIME_TO_EXT`字典。
- **Windows下python-magic使用问题？**
   请参考python-magic官方文档安装相应依赖。
- **大文件夹处理慢？**
   处理过程中程序为单线程，如需加速可以考虑多线程或多进程改造。

------

## 许可证

本项目采用MIT许可证，欢迎自由使用与修改。