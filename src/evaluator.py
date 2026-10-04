"""求值器：表达式求值的核心逻辑"""

from parser import Symbol
from environment import Environment
from primitives import Procedure, nil, Pair, scheme_list

def evaluate(expr, env):
    """求值表达式"""
    # 自求值：数字、布尔、字符串
    if isinstance(expr, (int, float, str)) and not isinstance(expr, Symbol):
        return expr
    if isinstance(expr, bool):
        return expr

    # 符号：变量引用
    if isinstance(expr, Symbol):
        return env.get(expr)

    # 列表：特殊形式或函数调用
    if isinstance(expr, list):
        if len(expr) == 0:
            raise SyntaxError("cannot evaluate empty list")

        # 特殊形式
        first = expr[0]

        # quote
        if first == Symbol('quote'):
            if len(expr) != 2:
                raise SyntaxError("quote requires exactly 1 argument")
            return quote_to_scheme(expr[1])

        # if
        if first == Symbol('if'):
            if len(expr) < 3 or len(expr) > 4:
                raise SyntaxError("if requires 2 or 3 arguments")
            test = evaluate(expr[1], env)
            if test is not False:
                return evaluate(expr[2], env)
            elif len(expr) == 4:
                return evaluate(expr[3], env)
            else:
                return None

        # cond
        if first == Symbol('cond'):
            for clause in expr[1:]:
                if not isinstance(clause, list) or len(clause) < 1:
                    raise SyntaxError("cond clause must be a list")
                test_expr = clause[0]
                if test_expr == Symbol('else'):
                    # else 子句
                    return eval_begin(clause[1:], env)
                test_val = evaluate(test_expr, env)
                if test_val is not False:
                    if len(clause) == 1:
                        return test_val
                    else:
                        return eval_begin(clause[1:], env)
            return None

        # and
        if first == Symbol('and'):
            result = True
            for arg in expr[1:]:
                result = evaluate(arg, env)
                if result is False:
                    return False
            return result

        # or
        if first == Symbol('or'):
            for arg in expr[1:]:
                result = evaluate(arg, env)
                if result is not False:
                    return result
            return False

        # define
        if first == Symbol('define'):
            if len(expr) < 3:
                raise SyntaxError("define requires at least 2 arguments")

            # 函数定义简写：(define (name params...) body...)
            if isinstance(expr[1], list):
                if len(expr[1]) < 1:
                    raise SyntaxError("define: function name required")
                name = expr[1][0]
                params = expr[1][1:]
                body = expr[2:]
                value = Procedure(params, body, env)
                env.define(name, value)
                return name

            # 普通定义：(define name value)
            else:
                if len(expr) != 3:
                    raise SyntaxError("define requires exactly 2 arguments")
                name = expr[1]
                if not isinstance(name, Symbol):
                    raise SyntaxError("define: first argument must be a symbol")
                value = evaluate(expr[2], env)
                env.define(name, value)
                return name

        # lambda
        if first == Symbol('lambda'):
            if len(expr) < 3:
                raise SyntaxError("lambda requires at least 2 arguments")
            params = expr[1]
            if not isinstance(params, list):
                raise SyntaxError("lambda: parameters must be a list")
            body = expr[2:]
            return Procedure(params, body, env)

        # let
        if first == Symbol('let'):
            if len(expr) < 3:
                raise SyntaxError("let requires at least 2 arguments")
            bindings = expr[1]
            body = expr[2:]

            if not isinstance(bindings, list):
                raise SyntaxError("let: bindings must be a list")

            # 并行绑定：先在外层环境求值所有绑定表达式
            names = []
            values = []
            for binding in bindings:
                if not isinstance(binding, list) or len(binding) != 2:
                    raise SyntaxError("let: each binding must be a list of 2 elements")
                name, val_expr = binding
                if not isinstance(name, Symbol):
                    raise SyntaxError("let: binding name must be a symbol")
                names.append(name)
                values.append(evaluate(val_expr, env))

            # 创建新环境
            new_env = Environment(parent=env)
            for name, value in zip(names, values):
                new_env.define(name, value)

            # 在新环境中求值 body
            return eval_begin(body, new_env)

        # begin
        if first == Symbol('begin'):
            return eval_begin(expr[1:], env)

        # 函数调用
        proc = evaluate(first, env)
        args = [evaluate(arg, env) for arg in expr[1:]]
        return apply_procedure(proc, args)

    raise SyntaxError(f"cannot evaluate: {expr}")

def eval_begin(exprs, env):
    """按顺序求值多个表达式，返回最后一个的结果"""
    if len(exprs) == 0:
        return None
    result = None
    for expr in exprs:
        result = evaluate(expr, env)
    return result

def apply_procedure(proc, args):
    """调用过程"""
    # 内置过程
    if callable(proc) and not isinstance(proc, Procedure):
        return proc(*args)

    # 用户定义的过程
    if isinstance(proc, Procedure):
        if len(args) != len(proc.params):
            raise TypeError(f"procedure expects {len(proc.params)} arguments, got {len(args)}")

        # 创建新环境，绑定参数
        new_env = Environment(parent=proc.env)
        for param, arg in zip(proc.params, args):
            new_env.define(param, arg)

        # 求值函数体
        return eval_begin(proc.body, new_env)

    raise TypeError(f"cannot call non-procedure: {proc}")

def quote_to_scheme(data):
    """将 Python 列表转换为 Scheme 点对链"""
    if isinstance(data, list):
        if len(data) == 0:
            return nil
        result = nil
        for item in reversed(data):
            result = Pair(quote_to_scheme(item), result)
        return result
    else:
        return data
