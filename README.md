# PyQt Calculator Suite

一个使用 PyQt5 编写的多模式桌面计算器，逐步复刻 Windows 计算器的常用能力，并加入绘图、高等数学和实时汇率转换等扩展功能。

## 功能

- 标准计算器：基础四则运算、括号、百分号、乘方、历史记录。
- 科学计算器：三角函数、反三角函数、对数、平方根、阶乘、倒数、角度/弧度切换。
- 绘图计算器：输入 `x` 的函数并绘图，支持多函数、显示/隐藏曲线、颜色标识、滚轮缩放、拖拽平移、悬停坐标提示和公式预览。
- 高等数学：求导、偏导、高阶导数、积分、定积分、极限、左右极限、Taylor 展开、方程求解和化简，支持格式化公式显示和独立历史记录。
- 程序员计算器：HEX/DEC/OCT/BIN 进制转换，QWORD/DWORD/WORD/BYTE 字长，signed/unsigned，位视图，AND/OR/XOR/NOT、移位和整数运算。
- 汇率转换：联网获取最新汇率并转换常见货币，支持转换记录。

## 环境要求

- Python 3.10+
- PyQt5
- SymPy
- 访问汇率转换功能时需要网络

如果使用当前项目里的 conda 环境，可以运行：

```bash
/Users/windyh/miniconda3/envs/pyqt_app/bin/python main.py
```

如需重新安装依赖：

```bash
python -m pip install PyQt5 sympy
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

科学模式中可通过 `角度` 菜单切换 `DEG/RAD`。

## 文件结构

- `main.py`：应用入口。
- `calculator_ui.py`：主窗口、菜单、标准/科学模式和历史面板。
- `calculator_core.py`：安全表达式计算核心。
- `graphing_widget.py`：绘图模式界面和画布。
- `advanced_math_core.py`：高等数学符号计算核心。
- `advanced_math_widget.py`：高等数学模式界面。
- `formula_formatter.py`：公式格式化显示工具。
- `currency_core.py`：汇率 API 访问。
- `currency_widget.py`：汇率转换界面。
- `programmer_core.py`：程序员计算核心。
- `programmer_widget.py`：程序员模式界面。

## 汇率数据说明

汇率转换使用 Frankfurter API 获取最新公开参考汇率。它不是外汇交易终端的秒级报价，而是 API 当前发布的最新汇率数据。

## 开发备注

项目当前不是 git 仓库。修改前建议先初始化 git，方便回滚和比较：

```bash
git init
git add .
git commit -m "Initial calculator suite"
```
