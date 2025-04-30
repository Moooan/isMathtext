from .latex_cleaner import clean_latex_text
from .code_cleaner import clean_code_text
from .inline_cleaner import clean_inline_patterns
from .lines_cleaner import remove_meaningless_lines
import re

def clean_text_to_fasttext(text: str, for_prediction: bool = False) -> list[str]:
    """
    清洗整段文本，提取每篇文章。
    - 如果 `for_prediction=True`，返回纯文本；
    - 否则返回 FastText 格式（带标签）。
    """
    article_chunks = re.split(r'(?=(?:__label__math|__label__non_math))', text)
    fasttext_lines = []

    for chunk in article_chunks:
        chunk = chunk.strip()
        if not chunk:
            continue

        label = ''
        if chunk.startswith("__label__math"):
            label = "__label__math"
            content = chunk[len("__label__math"):].strip()
        elif chunk.startswith("__label__non_math"):
            label = "__label__non_math"
            content = chunk[len("__label__non_math"):].strip()
        else:
            continue  # 跳过非法段

        # 清洗内容
        content = clean_latex_text(content, add_placeholder=True)
        content = clean_code_text(content, add_placeholder=True)
        lines = content.splitlines()
        clean_lines = [clean_inline_patterns(line) for line in lines]
        content = "\n".join(clean_lines)
        content = remove_meaningless_lines(content)
        content = re.sub(r'\s+', ' ', content).strip().lower()

        if not content:
            continue

        if for_prediction:
            fasttext_lines.append(content)
        else:
            fasttext_lines.append(f"{label} {content}")

    return fasttext_lines


def save_fasttext_file(input_path: str, output_path: str, for_prediction: bool = False):
    with open(input_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    fasttext_lines = clean_text_to_fasttext(raw_text, for_prediction=for_prediction)

    with open(output_path, "w", encoding="utf-8") as f:
        for line in fasttext_lines:
            f.write(line + "\n")

    print(f"{'预测' if for_prediction else '训练'}格式文件保存至：{output_path}")