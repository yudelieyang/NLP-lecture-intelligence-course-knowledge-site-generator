# Local-first Lecture Knowledge App 中文 Demo 说明书

本文档用于说明 `EC508 NLP Demo` 如何在本地运行。它面向普通用户，不要求理解 Python 代码。

## 1. 这个 Demo 是什么

这是一个本地优先的课程知识库生成工具。你把课程 PDF、Markdown 或 Word 文件放入 `input_materials/` 文件夹，然后通过浏览器里的本地 Dashboard 点击生成，系统会在 `output_sites/` 中创建一个新的 HTML 知识站点。

整个流程在本机完成。它不是云服务，不需要登录，也不会把课件上传到外部服务器。

## 2. 支持哪些文件

当前支持：

- PDF：`.pdf`
- Markdown：`.md`、`.markdown`
- Word：`.docx`

暂未支持，但后续计划支持：

- PowerPoint：`.pptx`
- Jupyter Notebook：`.ipynb`
- OCR 扫描件识别

## 3. 准备材料

把需要生成笔记的课件文件放到项目根目录下的：

```text
input_materials/
```

建议文件名中包含 Lecture 编号，例如：

```text
Lecture 10 -- Supervised ML.pdf
Lecture 18 -- Intro to Transformers.pdf
Lecture 21 -- GPT and T5.pdf
```

如果文件名不包含 Lecture 编号，系统会按普通学习单元处理，例如 `Lecture Unit 01`。

## 4. 启动本地 Web Dashboard

双击项目根目录中的：

```text
run_app.bat
```

程序会自动：

1. 检查 Python。
2. 创建或复用 `.venv` 虚拟环境。
3. 安装依赖。
4. 启动本地 FastAPI 服务。
5. 打开浏览器页面：

```text
http://127.0.0.1:7860
```

注意：命令行窗口必须保持打开。关闭窗口后，本地 Web Dashboard 会停止工作。

## 5. Dashboard 页面说明

Dashboard 包含几个主要区域。

### Input Materials

这里显示 `input_materials/` 文件夹中检测到的文件。

你可以看到：

- 文件名
- 文件类型
- 文件大小
- 是否支持
- 当前状态

状态含义：

- `supported`：当前可以处理。
- `roadmap`：未来计划支持，例如 `.pptx`、`.ipynb`。
- `unsupported`：当前不支持。

如果列表为空，请把 PDF / MD / DOCX 文件放入 `input_materials/` 后点击 `Refresh file list`。

### Project Settings

这里配置生成项目的基本信息。

- `Project name`：项目名称，会影响输出版本名。
- `Min content chars`：最小提取文本长度。内容太少时会阻止生成，避免空站点。
- `Language`：默认 `zh`。
- `Preserve English terms`：默认勾选，用于保留 NLP / ML / DL 英文术语。
- `Enable LLM`：是否启用外部或本地大模型增强总结。

如果不启用 LLM，系统仍然可以生成基础知识站点。

### LLM Settings

只有勾选 `Enable LLM` 后才需要关注。

支持：

- `openai_compatible`
- `ollama`

需要填写：

- Endpoint
- Model
- API key environment variable，例如 `OPENAI_API_KEY`

建议把真实 API key 写入项目根目录的 `.env` 文件，而不是直接写在网页里。

示例：

```text
OPENAI_API_KEY=your_key_here
```

安全提醒：不要提交 `.env`，不要把本地 Dashboard 暴露到公网。

### Generate

点击：

```text
Generate New Site
```

系统会读取 `input_materials/` 中的支持文件，并生成新的版本化知识站点。

生成完成后会显示：

- runId
- output path
- Open generated site
- Open output folder

每次生成都会创建新的版本目录，不会覆盖旧版本。

### Generated Versions

这里显示历史生成记录，来源是：

```text
output_sites/runs.json
```

每个版本可以打开：

- 生成后的 `index.html`
- 对应的输出文件夹

### Status / Logs

这里显示最近一次生成日志，例如：

```text
Checking input_materials...
Processed: Lecture 10 -- Supervised ML.pdf -> lecture-10
Output site: ...
Processed files: 1
Failed files: 0
```

如果出现错误，Dashboard 会尽量显示人类可读的错误信息。

## 6. 生成结果在哪里

生成结果位于：

```text
output_sites/<run_id>/
```

常见文件包括：

```text
index.html
style.css
script.js
metadata.json
search-index.json
assets/
```

打开 `index.html` 即可阅读生成的知识站点。

## 7. 生成出的知识站点包含什么

生成站点通常包含：

- 左侧目录
- 右侧 lecture 内容
- 搜索功能
- 术语 tooltip
- Source-grounded Notes
- Creative Extension
- Source-grounded Practice
- Creative Extension Practice
- MathJax 公式支持

其中：

- `Source-grounded Notes`：基于本地输入材料。
- `Creative Extension`：基于材料启发的拓展内容，不能当作原始课件引用。

## 8. 常见问题

### 双击 run_app.bat 后窗口不要关闭吗？

不要关闭。这个窗口正在运行本地 Web server。关闭后，浏览器里的 Dashboard 会无法访问。

### 为什么浏览器显示打不开？

确认命令行窗口仍在运行，并访问：

```text
http://127.0.0.1:7860
```

如果端口被占用，关闭其他同类窗口后重新双击 `run_app.bat`。

### 为什么没有检测到文件？

请确认文件确实放在：

```text
input_materials/
```

并且格式是 `.pdf`、`.md`、`.markdown` 或 `.docx`。

### 为什么没有 API key 也能生成？

这是正常现象。没有 LLM 时，系统会使用本地提取文本和模板生成基础知识站点。

### 扫描版 PDF 为什么内容很少？

当前版本没有 OCR。扫描版 PDF 可能没有可提取文本，需要后续 OCR 功能支持。

### 历史版本会被覆盖吗？

不会。每次生成都会创建新的 `output_sites/<run_id>/`。

## 9. 安全与版权说明

本 Demo 是本地工具：

- 只绑定 `127.0.0.1`。
- 不提供公网访问。
- 不提供用户登录。
- 不上传课件。
- 不使用数据库。
- 不打包 EXE。

请只处理你有权使用的课程材料。不要把课程 PDF、生成笔记或含版权内容的站点公开分发，除非你拥有相应授权。

## 10. 推荐 Demo 操作流程

1. 准备 1 到 3 个 PDF / MD / DOCX 课件。
2. 放入 `input_materials/`。
3. 双击 `run_app.bat`。
4. 浏览器打开 Dashboard。
5. 查看 Input Materials 是否检测成功。
6. 填写 Project name。
7. 不启用 LLM，先点击 `Generate New Site` 测试基础流程。
8. 生成成功后点击 `Open generated site`。
9. 查看搜索、目录、笔记和练习题功能。
10. 再次点击生成，确认历史版本不会被覆盖。
