# model.py
import fasttext

def train_fasttext_model(model_path, train_file, epoch=25, lr=0.5, wordNgrams=2):
    model = fasttext.train_supervised(
        input=train_file,
        epoch=epoch,
        lr=lr,
        wordNgrams=wordNgrams,
        verbose=2,
        minCount=1,
        loss='softmax'
    )
    model.save_model(model_path)
    return model

def test_fasttext_model(model_path, test_file):
    model = fasttext.load_model(model_path)
    result = model.test(test_file)
    print(f"Test samples: {result[0]}")
    print(f"Precision@1: {result[1]:.4f}")
    print(f"Recall@1: {result[2]:.4f}")
    return result

def predict_file(model_path: str, input_path: str, output_path: str):
    model = fasttext.load_model(model_path)


    with open(input_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    with open(output_path, "w", encoding="utf-8") as f:
        for i, line in enumerate(lines):
            label, prob = model.predict(line)
            f.write(f"{label[0]}\t{prob[0]:.4f}\t{line}\n")

    print(f"预测结果已保存至：{output_path}")