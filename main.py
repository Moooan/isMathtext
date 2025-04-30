from data_process.data_cleaner import save_fasttext_file
from model import train_fasttext_model, test_fasttext_model, predict_file
from pathlib import Path
import random


if __name__ == "__main__":
    # 输入输出路径
    input_fineweb = "data/fineweb_5000_train.txt"
    input_openwebmath = "data/openwebmath_5000_train.txt"
    input_question = "output/fineweb_5000_question.txt"

    cleaned_fineweb = "data/fineweb_5000_train_cleaned.txt"
    cleaned_openwebmath = "data/openwebmath_5000_train_cleaned.txt"
    cleaned_question = "output/fineweb_5000_question_cleaned.txt"

    # 模型路径
    model_file = "output/fasttext_model.bin"

    output_answer = "fineweb_5000_answer.txt"
    # 步骤 1: 清洗各数据源
    save_fasttext_file(input_fineweb, cleaned_fineweb)
    save_fasttext_file(input_openwebmath, cleaned_openwebmath)
    save_fasttext_file(input_question, cleaned_question, True)

    # 步骤 2: 合并训练集、划分数据集并随机打乱
    with open(cleaned_fineweb, "r", encoding="utf-8") as f1, \
         open(cleaned_openwebmath, "r", encoding="utf-8") as f2:
        all_lines = f1.readlines() + f2.readlines()
        random.shuffle(all_lines)

    # 划分训练集和测试集（比如 90% 训练，10% 测试）
    split_ratio = 0.9
    split_index = int(len(all_lines) * split_ratio)
    train_lines = all_lines[:split_index]
    test_lines = all_lines[split_index:]

    # 保存到不同文件
    Path("data").mkdir(exist_ok=True)

    train_file = "data/merged_5000_train.txt"
    test_file = "data/merged_5000_test.txt"

    with open(train_file, "w", encoding="utf-8") as f_train:
        f_train.writelines(train_lines)

    with open(test_file, "w", encoding="utf-8") as f_test:
        f_test.writelines(test_lines)

    # 步骤 3: 训练模型
    train_fasttext_model(model_file, train_file)

    # 步骤 4: 测试模型
    test_fasttext_model(model_file, test_file)

    # 步骤 5: 生成答案
    predict_file(model_file, cleaned_question, output_answer)