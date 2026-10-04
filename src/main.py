#!/usr/bin/env python3
"""mini-Scheme 解释器入口"""

import sys
import os

# 添加当前目录到 sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parser import parse_program
from evaluator import evaluate
from primitives import create_global_environment, scheme_to_string

def run_file(filename, env):
    """运行一个 Scheme 文件"""
    with open(filename, 'r') as f:
        text = f.read()
    run_text(text, env)

def run_text(text, env):
    """运行 Scheme 代码文本"""
    expressions = parse_program(text)
    for expr in expressions:
        result = evaluate(expr, env)
        # None 不打印（如 display、newline 的结果）
        if result is not None:
            print(scheme_to_string(result))

def main():
    """主函数"""
    env = create_global_environment()

    if len(sys.argv) > 1:
        # 从文件读取
        for filename in sys.argv[1:]:
            run_file(filename, env)
    else:
        # 从标准输入读取
        text = sys.stdin.read()
        run_text(text, env)

if __name__ == '__main__':
    main()
