import re
import string

def remove_meaningless_lines(text: str, threshold: float = 0.5) -> str:
    """
    删除特殊字符比例超过 threshold 的行。
    threshold: 允许的最大比例（如 0.5 表示特殊字符占一半以上就删掉）
    删除冗余、无意义的短行，比如感谢、打招呼、简单反馈之类。
    """
    lines = text.splitlines()
    cleaned_lines = []
    symbols = set(string.punctuation)  # !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~
    meaningless_patterns = [
        r"^(thanks|thank you|good luck|ok|yes|no|hi|hello|welcome|good job|great|bye)[!.\s]*$",  # 简单单词
        r"^(you are right|good question|please help|nice work|sounds good)[!.\s]*$",             # 简单句子
        r"^[a-zA-Z\s]{1,10}$",   # 只有少量字母，不到10个字符
    ]

    combined_pattern = re.compile("|".join(meaningless_patterns), re.IGNORECASE)

    for line in lines:
        ''' 删除无意义内容行 '''
        stripped = line.strip()
        if not stripped:
            continue  # 空行跳过

        # 如果匹配了无意义内容，就跳过
        if combined_pattern.match(stripped):
            continue

        '''删除特殊字符比例过高的行'''
        total_chars = len(line)
        if total_chars == 0:
            continue

        special_chars = sum(1 for ch in line if ch in symbols)
        ratio = special_chars / total_chars

        if ratio <= threshold:
            cleaned_lines.append(line)
        # else: 删除这一行


    return "\n".join(cleaned_lines)
