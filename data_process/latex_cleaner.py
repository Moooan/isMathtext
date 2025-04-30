import re

def is_latex_line(line):
    """判断一行是不是LaTeX公式（支持多种格式）"""
    line = line.strip()
    if not line:
        return False
    # 单行公式，比如 $...$ 或 \[...\] 或 \( ... \)
    if re.match(r"^\$.*\$$", line) or re.match(r"^\\\[.*\\\]$", line) or re.match(r"^\\\(.*\\\)$", line):
        return True
    # 单行以命令开头，如 \frac{}{}，且不是普通文字（避免误删）
    if re.match(r"^\\[a-zA-Z]+.*", line) and len(line.split()) < 15:
        return True
    # 特殊：如果一整行几乎都是符号（$ { } ^ _ \）也判为latex
    if re.match(r"^[\s\$\{\}\\\^\_\-\=\+\*\[\]\(\)a-zA-Z0-9]+$", line) and "\\" in line:
        return True
    return False

def clean_latex_text(text, add_placeholder=True):
    """
    清除跨行LaTeX块，逐行删除LaTeX公式行
    :param text: 输入原始文本
    :param add_placeholder: 是否添加占位符<LATEX_BLOCK>
    """
    lines = text.splitlines()
    cleaned_lines = []
    in_latex_block = False
    temp_block = []

    for line in lines:
        stripped = line.strip()

        # 开始跨行 latex 块
        if re.search(r"\\begin\{[^\}]*\}", stripped) or stripped.startswith("$$"):
            in_latex_block = True
            temp_block = []
            continue

        # 结束跨行 latex 块
        if re.search(r"\\end\{[^\}]*\}", stripped) or stripped.startswith("$$"):
            in_latex_block = False
            # if add_placeholder:
            #     cleaned_lines.append("<LATEX_BLOCK>")
            temp_block = []
            continue

        if in_latex_block:
            temp_block.append(line)
            continue

        # 单行公式
        if is_latex_line(stripped):
            # if add_placeholder:
            #     cleaned_lines.append("<LATEX_INLINE>")
            continue

        # 正常文字
        cleaned_lines.append(line)

    # 清除前后空行 & 空格标准化
    final_lines = [l.strip() for l in cleaned_lines if l.strip()]
    return "\n".join(final_lines)