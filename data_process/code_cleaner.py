import re

def is_code_line(line):
    """判断一行是不是可能是代码（支持Python/C/伪代码）"""
    line = line.strip()
    if not line:
        return False
    # 注释行
    if line.startswith("#") or line.startswith("//") or line.startswith("/*") or line.startswith("*") or line.endswith("*/"):
        return True
    # 典型关键字
    if re.match(r"^(int|float|double|char|bool|void|if|else|for|while|switch|case|return|struct|typedef)\b", line):
        return True
    if re.match(r"^(def|class|import|from|print|with|try|except|finally|async|await|lambda|yield)\b", line):
        return True
    # 符号密集（代码一般含有很多符号）
    symbols = "{}();=:+-*/<>\[\]\.,\"\'\\"
    if sum(c in symbols for c in line) / max(1, len(line)) > 0.3:
        return True
    # 明显缩进
    if line.startswith("    ") or line.startswith("\t"):
        return True
    return False

def clean_code_text(text, add_placeholder=True):
    """
    清除整体代码块和单行代码行
    :param text: 输入原始文本
    :param add_placeholder: 是否添加占位符<COD_BLOCK>
    """
    lines = text.splitlines()
    cleaned_lines = []
    in_code_block = False
    temp_block = []

    for line in lines:
        stripped = line.strip()

        # 检测 ``` 开关代码块（支持 ```python、```c、```）
        if stripped.startswith("```"):
            if in_code_block and add_placeholder:
                cleaned_lines.append("<CODE_BLOCK>")
            in_code_block = not in_code_block
            continue

        # 处于代码块中
        if in_code_block:
            continue

        # 单行代码判断
        if is_code_line(stripped):
            if add_placeholder:
                cleaned_lines.append("<CODE_INLINE>")
            continue

        # 正常文字行
        cleaned_lines.append(line)

    # 标准化：去除首尾空行
    final_lines = [l.strip() for l in cleaned_lines if l.strip()]
    return "\n".join(final_lines)