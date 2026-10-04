"""语法分析器：将 token 列表转换为抽象语法树"""

class Symbol(str):
    """符号类型，用于区分符号和字符串"""
    pass

def parse(tokens):
    """将 token 列表解析为表达式"""
    if len(tokens) == 0:
        raise SyntaxError('unexpected EOF')

    token = tokens.pop(0)

    if token == '(':
        # 解析列表
        expr = []
        while tokens[0] != ')':
            expr.append(parse(tokens))
        tokens.pop(0)  # 移除 ')'
        return expr
    elif token == ')':
        raise SyntaxError('unexpected )')
    else:
        # 解析原子
        return parse_atom(token)

def parse_atom(token):
    """将 token 转换为原子值"""
    # 布尔值
    if token == '#t':
        return True
    elif token == '#f':
        return False
    # 数字
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            pass
    # 字符串
    if token.startswith('"') and token.endswith('"'):
        # 处理转义字符
        s = token[1:-1]
        s = s.replace('\\n', '\n')
        s = s.replace('\\t', '\t')
        s = s.replace('\\"', '"')
        s = s.replace('\\\\', '\\')
        return s
    # 符号
    return Symbol(token)

def parse_program(text):
    """解析整个程序，返回表达式列表"""
    from lexer import tokenize
    tokens = tokenize(text)
    expressions = []
    while tokens:
        expressions.append(parse(tokens))
    return expressions
