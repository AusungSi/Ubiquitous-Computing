import numpy as np

def calculate_accuracy(pred_levels, ground_truth):
    """
    计算 L4 报警的准确率
    """
    correct = 0
    total = len(pred_levels)
    for p, g in zip(pred_levels, ground_truth):
        if p == g:
            correct += 1
    return correct / total