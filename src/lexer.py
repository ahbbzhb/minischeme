"""词法分析器：将程序文本转换为 token 列表"""

import re

def tokenize(text):
    """将 Scheme 代码文本转换为 token 列表"""
    # 移除注释
    text = re.sub(r';.*', '', text)

    # 使用正则表达式匹配 token
    # 匹配：字符串、括号、引号、或其他 token
    pattern = r'''
        ("(?:[^"\\]|\\.)*")   # 字符串字面量
        |(\()                  # 左括号
        |(\))                  # 右括号
        |(')                   # 引号
        |([^\s()"']+)          # 其他 token
    '''

    tokens = []
    i = 0
    matches = list(re.finditer(pattern, text, re.VERBOSE))

    while i < len(matches):
        match = matches[i]
        token = match.group(0)

        if token == "'":
            # 将 'x 转换为 (quote x)
            tokens.append('(')
            tokens.append('quote')
            # 读取下一个 token
            i += 1
            if i < len(matches):
                next_token = matches[i].group(0)
                if next_token == '(':
                    # 'LIST 形式，需要找到匹配的 )
                    tokens.append('(')
                    paren_count = 1
                    i += 1
                    while i < len(matches) and paren_count > 0:
                        t = matches[i].group(0)
                        tokens.append(t)
                        if t == '(':
                            paren_count += 1
                        elif t == ')':
                            paren_count -= 1
                        i += 1
                    i -= 1  # 回退一步，因为外层循环会 +1
                else:
                    # 'atom 形式
                    tokens.append(next_token)
                tokens.append(')')
        else:
            tokens.append(token)

        i += 1

    return tokens
