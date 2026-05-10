# Calculator Suite

一个多模式计算器项目。当前包含 PyQt5 桌面版和 Django 网页版，后端计算逻辑独立在 `backend/`，两个前端共用同一套核心能力。

## 功能

- 标准计算器：基础四则运算、括号、百分号、乘方、历史记录。
- 科学计算器：三角函数、反三角函数、对数、平方根、阶乘、倒数、角度/弧度切换。
- 绘图计算器：输入 `x` 的函数并绘图，支持多函数、显示/隐藏曲线、颜色标识、滚轮缩放、拖拽平移、悬停坐标提示和公式预览。
- 高等数学：求导、偏导、高阶导数、积分、定积分、极限、左右极限、Taylor 展开、方程求解和化简，支持格式化公式显示和独立历史记录。
- 程序员计算器：HEX/DEC/OCT/BIN 进制转换，QWORD/DWORD/WORD/BYTE 字长，signed/unsigned，位视图，AND/OR/XOR/NOT、移位和整数运算。HEX 模式下 `A-F` 可作为数字输入，`CE` 或 `Esc` 清空。
- 汇率转换：联网获取最新汇率并转换常见货币，支持转换记录。
- 网页版入口：桌面程序中可通过 `模式 -> 打开网页版` 启动本地 Django 服务，并点击本地地址打开浏览器版本。

## 环境要求

- Python 3.10+
- PyQt5
- Django
- SymPy
- 访问汇率转换功能时需要网络

如果使用当前项目里的 conda 环境，可以运行：

```bash
/Users/windyh/miniconda3/envs/pyqt_app/bin/python main.py
```

如需重新安装依赖：

```bash
python -m pip install PyQt5 Django sympy
```

## 使用方式

启动程序：

```bash
python main.py
```

通过顶部菜单切换模式：

- `模式 -> 标准`
- `模式 -> 科学`
- `模式 -> 绘图`
- `模式 -> 高等数学`
- `模式 -> 汇率转换`
- `模式 -> 程序员`
- `模式 -> 打开网页版`

科学模式中可通过 `角度` 菜单切换 `DEG/RAD`。

选择 `打开网页版` 后，桌面界面会切换到只显示网站地址的页面，并在后台启动本地 Django 服务。默认地址：

```text
http://127.0.0.1:8765/
```

## 项目结构

- `main.py`：PyQt 桌面版入口。
- `backend/`：纯功能后端，不依赖 PyQt，后续 Django 可以直接复用。
- `backend/calculator_core.py`：标准/科学表达式计算。
- `backend/advanced_math_core.py`：高等数学符号计算。
- `backend/currency_core.py`：汇率 API 访问。
- `backend/programmer_core.py`：程序员模式整数和位运算。
- `frontends/pyqt/`：PyQt 桌面前端。
- `frontends/pyqt/calculator_ui.py`：桌面主窗口、模式菜单、标准/科学界面。
- `frontends/pyqt/graphing_widget.py`：绘图界面和画布。
- `frontends/pyqt/advanced_math_widget.py`：高等数学界面。
- `frontends/pyqt/currency_widget.py`：汇率转换界面。
- `frontends/pyqt/programmer_widget.py`：程序员界面。
- `frontends/pyqt/web_launcher_widget.py`：桌面端网页版启动页。
- `frontends/pyqt/formula_formatter.py`：PyQt 公式格式化显示工具。
- `frontends/django_web/`：Django 网页前端。
- `frontends/django_web/server.py`：桌面端后台启动 Django 服务。
- `frontends/django_web/views.py`：网页端 API，调用 `backend/` 中的核心逻辑。
- `frontends/django_web/templates/calculator.html`：网页计算器界面。
- `scripts/check_all.py`：自动检查脚本。

## 自动检查

运行语法检查和关键功能回归：

```bash
QT_QPA_PLATFORM=offscreen python scripts/check_all.py
```

当前检查覆盖：

- 标准/科学表达式计算
- 高等数学导数、积分、极限
- 程序员模式进制、位运算、字长裁剪
- 绘图表达式和公式预览
- 高等数学历史记录
- 汇率转换界面逻辑
- PyQt 主窗口模式切换和历史面板显隐

## 汇率数据说明

汇率转换使用 Frankfurter API 获取最新公开参考汇率。它不是外汇交易终端的秒级报价，而是 API 当前发布的最新汇率数据。

## 程序员模式键盘输入

- 数字/十六进制：`0-9`、`A-F`
- 运算：`+`、`-`、`*`、`/`、`%`
- 位运算：`&`、`|`、`^`、`~`
- 括号：`(`、`)`
- 计算：`Enter`
- 删除：`Backspace`
- 清空：`Esc`

## 开发备注

项目当前不是 git 仓库。修改前建议先初始化 git，方便回滚和比较：

```bash
git init
git add .
git commit -m "Initial calculator suite"
```
