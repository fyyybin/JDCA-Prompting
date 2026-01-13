#!/bin/bash
set -e
datasets_flash=(
    "beliefQAs1"
    # "beliefQAs2"
    # "beliefQAs3"
    # "answerabilityQA1"
    # "answerabilityQA2"
    # "answerabilityQA3"
    # "answerabilityQA4"
    # "answerabilityQA5"
    # "answerabilityQA6"
    # "answerabilityQA7"
    # "nfoAccessibilityQA1"
    # "nfoAccessibilityQA2"
    # "nfoAccessibilityQA3"
    # "nfoAccessibilityQA4"
    # "nfoAccessibilityQA5"
    # "nfoAccessibilityQA6"
    # "nfoAccessibilityQA7"
)
datasets_flash_ex=(
    # "nfoAccessibilityQA6"
    # "answerabilityQA2"
    # "answerabilityQA3"
    # "answerabilityQA5"
    "answerabilityQA6"
    "answerabilityQA7"
)
datasets_llama=(
    # "beliefQAs1"
    # "beliefQAs2"
    # "beliefQAs3"
    # "answerabilityQA1"
    # "answerabilityQA2"
    # "answerabilityQA3"
    # "answerabilityQA4"
    # "answerabilityQA5"
    # "answerabilityQA6"
    "answerabilityQA7"
    # "nfoAccessibilityQA1"
    # "nfoAccessibilityQA2"
    # "nfoAccessibilityQA3"
    # "nfoAccessibilityQA4"
    # "nfoAccessibilityQA5"
    # "nfoAccessibilityQA6"
    # "nfoAccessibilityQA7"
)
# gpt-3.5-turbo-1106, gpt-4o
# for ds in "${datasets_flash_ex[@]}"; do
#     echo "==== 开始执行 dataset: $ds meta-llama/llama-3-70b-instruct  ===="
#     python personality_eval.py --dataset "$ds" --model meta-llama/llama-3-70b-instruct --method get_eval
#     echo "==== 完成 dataset: $ds ===="
# done
# for ds in "${datasets_flash_ex[@]}"; do
#     echo "==== 开始执行 dataset: $ds meta-llama/llama-3-70b-instruct ===="
#     python personality_eval.py --dataset "$ds" --model meta-llama/llama-3-70b-instruct --method inherent
#     echo "==== 完成 dataset: $ds ===="
# done

for ds in "${datasets_flash[@]}"; do
    echo "==== 开始执行 dataset: $ds gemini-2.5-flash ===="
    python personality_eval.py --dataset "$ds" --model gemini-2.5-flash --method get_eval 
    echo "==== 完成 dataset: $ds ===="
done