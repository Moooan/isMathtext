import re
import html

def clean_tables_and_images(text):
    """
    在 mwparser 清洗后的基础上进一步删除残留的表格、图片、thumb 之类内容
    适用于 fasttext 清洗阶段，纯文本层面
    """

    # 删除残留的图片标记 [[File:...]] / [[Image:...]] / [[文件:...]]
    text = re.sub(r'\[\[\s*(File|Image|文件):[^\]]+\]\]', '', text, flags=re.IGNORECASE)

    # 删除残留的缩略图/图片说明（如包含thumb|caption）
    text = re.sub(r'thumb\|[^\|\]]*(\|[^\|\]]*)*', '', text, flags=re.IGNORECASE)

    # 删除残留的表格结构或代码块标志
    # 表格起始标记（不完整残留）
    text = re.sub(r'\{\|.*?\n', '', text)       # 开始标记
    text = re.sub(r'\n\|\}|\|\}$', '', text)    # 结束标记
    text = re.sub(r'\|\-[^\n]*', '', text)      # 行分隔符
    text = re.sub(r'\|\s*[^\n]*', '', text)     # 表格单元格（如 | 内容）
    text = re.sub(r'!\s*[^\n]*', '', text)      # 表头单元格（如 ! 内容）

    # 删除包含残留多行表格结构的大块
    text = re.sub(r'^\{\|[\s\S]*?\|\}$', '', text, flags=re.MULTILINE)

    # 清理 [[]] 空链接
    text = re.sub(r'\[\[[^\[\]]*\|?\s*\]\]', '', text)

    # 再清一次 HTML 注释残留
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)

    # 清理空行与多余空格
    lines = text.splitlines()
    cleaned = [line.strip() for line in lines if line.strip()]
    return '\n'.join(cleaned)

def remove_emoji(text: str) -> str:
    """移除文本中的 Emoji 表情符号"""
    emoji_pattern = re.compile(
        "["
        u"\U0001F600-\U0001F64F"  # 表情符号
        u"\U0001F300-\U0001F5FF"  # 符号 & 图标
        u"\U0001F680-\U0001F6FF"  # 运输工具 & 地标
        u"\U0001F1E0-\U0001F1FF"  # 国旗
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

def remove_footer_info(text: str) -> str:
    """移除常见的页脚版权信息"""
    footer_patterns = [
        r"All rights reserved",
        r"Source: .*",
        r"Copyright .*",
        r"Terms of Service",
        r"Privacy Policy",
        r"Page generated in .* seconds",
        r"This post was updated on .*",
    ]
    combined = re.compile("|".join(footer_patterns), re.IGNORECASE)
    return combined.sub("", text)

def decode_html_entities(text: str) -> str:
    """把 HTML 实体 (如 &nbsp;, &lt;) 解码成正常字符"""
    return html.unescape(text)

def remove_inline_mentions(text: str) -> str:
    """
    将文本中的 @用户名 或 @Some.Name 删除。
    """
    # 匹配 @username、@user.name、@user_name 等形式
    return re.sub(r'@[\w\.-]+', '', text)


def clean_latex_text(text):
    # 1. 合并上下标：x_1 → x1, x^{ij} → xij
    text = re.sub(r'([a-zA-Z])[_\^]\{([^}]+)\}', r'\1\2', text)      # 花括号形式
    text = re.sub(r'([a-zA-Z])[_\^]([a-zA-Z0-9])', r'\1\2', text)    # 简单形式

    # 2. 替换常见命令为人类可读形式（可扩展）
    latex_dict = {
        r'\\mathcal\{N\}': 'normal_distribution',
        r'\\operatorname\{Bernoulli\}': 'bernoulli',
        r'\\operatorname\{Binomial\}': 'binomial',
        r'\\mu': 'mu',
        r'\\sigma': 'sigma',
        r'\\alpha': 'alpha',
        r'\\beta': 'beta',
        r'\\infty': 'infinity',
        r'\\bar\s*\{x\}': 'sample_mean',
        r'\\scriptstyle\s*\\bar\s*x': 'sample_mean',
    }
    for pattern, replacement in latex_dict.items():
        text = re.sub(pattern, replacement, text)

    # 3. 替换分式 \frac{a}{b} → (a)/(b)
    text = re.sub(r'\\frac\s*\{([^{}]+)\}\s*\{([^{}]+)\}', r'(\1)/(\2)', text)

    # 4. 删除所有 LaTeX 命令（剩下的 \xxx）
    text = re.sub(r'\\[a-zA-Z]+\*?(?:\[[^\]]*\])?(?:\{[^}]*\})?', '', text)

    # 5. 删除公式定界符（$...$、\(...\)、\[...\]）
    text = re.sub(r'\$\$.*?\$\$', '', text)
    text = re.sub(r'\$.*?\$', '', text)
    text = re.sub(r'\\\(|\\\)|\\\[|\\\]', '', text)

    # 6. 删除残余符号：{}, ^, _, ~
    text = re.sub(r'[\{\}^_~]', '', text)

    # 7. 删除多余空白
    text = re.sub(r'\s+', ' ', text).strip()

    return text
import re
import html

def final_text_cleanup(text):
    # 1. 去除 HTML 实体编码，例如 &nbsp; &ldquo;
    text = html.unescape(text)

    # 2. 删除各种常见日期表达
    text = re.sub(r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|'
                  r'Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|'
                  r'Nov(?:ember)?|Dec(?:ember)?)[\s.,\-]*\d{1,2}(st|nd|rd|th)?[\s,]*\d{4}?\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\b\d{1,2}[\-/]\d{1,2}[\-/]\d{2,4}\b', '', text)  # 12/05/2024
    text = re.sub(r'\b\d{4}[\-/\.年]?\d{1,2}[\-/\.月]?\d{0,2}\b', '', text)  # 2023-12-25、2023年12月

    # 3. 删除时间表达
    text = re.sub(r'\b\d{1,2}(:\d{2})?\s*(am|pm|a\.m\.|p\.m\.)?\b', '', text, flags=re.IGNORECASE)

    # 4. 删除金额、百分数、纯数字串
    text = re.sub(r'\$\d+([\.,]\d+)?', '', text)          # $300
    text = re.sub(r'\d+(\.\d+)?%', '', text)              # 25.5%
    text = re.sub(r'\b\d{4,}\b', '', text)                # 年份、ID、长数字串

    # 5. 删除电话、网址、邮箱
    text = re.sub(r'\b\d{3}[-.\s]??\d{3}[-.\s]??\d{4}\b', '', text)  # 电话
    text = re.sub(r'\S+@\S+', '', text)                              # 邮箱
    text = re.sub(r'http\S+|www\.\S+', '', text)                     # URL

    # 6. 删除残留特殊字符
    text = re.sub(r'[<>@#~^\\\/]', ' ', text)
    text = re.sub(r'[\(\)\[\]\{\}]', ' ', text)
    text = re.sub(r'[\*\+=_]', ' ', text)

    # 7. 删除所有非英文字母、数字、标点（只保留英文和空格）
    text = re.sub(r'[^a-zA-Z0-9.,;:!?\'\"()\[\]\-\/\s]', ' ', text)

    # 8. 去除多余空格、空行
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def clean_inline_patterns(text):
    """处理句子中出现的小块公式、链接、HTML标签、小代码等"""
    # 1. 清洗 LaTeX公式
    text =  clean_latex_text(text)
    
    # 2. 替换 URL链接
    url_pattern = re.compile(r"http[s]?://\S+|www\.\S+")
    text = url_pattern.sub("", text)
    
    # 3. 替换 HTML/XML 标签
    text = re.sub(r"<[^>]+>", "", text)
    text = decode_html_entities(text)

    # 4. 检测并替换简单的小段代码（比如赋值语句 x=1, a += b）
    text = re.sub(r"\b\w+\s*=\s*[^ ]+", "", text)
    
    # 5. 处理对话
    text = remove_inline_mentions(text)

    # # 6. 处理时间 --放到final里处理
    # text = remove_time_mentions(text)

    # 7. 清理表格和图片
    text = clean_tables_and_images(text)
    # 8. 清除页脚信息
    text = remove_footer_info(text)

    # 9. 清除emoji
    text = remove_emoji(text)
    
    text = final_text_cleanup(text)
    return text
