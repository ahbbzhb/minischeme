"""内置过程：Scheme 标准函数库"""

from parser import Symbol
import operator
import functools

class Procedure:
    """用户定义的过程（闭包）"""
    def __init__(self, params, body, env):
        self.params = params
        self.body = body
        self.env = env

    def __repr__(self):
        return "#<procedure>"

# 点对类
class Pair:
    """Scheme 点对"""
    def __init__(self, car, cdr):
        self.car = car
        self.cdr = cdr

    def __repr__(self):
        return f"({pair_to_string(self)})"

    def __eq__(self, other):
        if not isinstance(other, Pair):
            return False
        return equal_impl(self.car, other.car) and equal_impl(self.cdr, other.cdr)

def pair_to_string(pair):
    """将点对转换为字符串"""
    if pair.cdr == nil:
        return scheme_to_string(pair.car)
    elif isinstance(pair.cdr, Pair):
        return scheme_to_string(pair.car) + " " + pair_to_string(pair.cdr)
    else:
        return scheme_to_string(pair.car) + " . " + scheme_to_string(pair.cdr)

# 空表
class Nil:
    def __repr__(self):
        return "()"
    def __eq__(self, other):
        return isinstance(other, Nil)

nil = Nil()

def scheme_to_string(val):
    """将 Scheme 值转换为字符串"""
    if val is True:
        return "#t"
    elif val is False:
        return "#f"
    elif val is nil:
        return "()"
    elif isinstance(val, Symbol):
        # Symbol 必须在 str 之前检查，因为 Symbol 继承自 str
        return str(val)
    elif isinstance(val, str):
        # 字符串需要转义
        s = val.replace('\\', '\\\\')
        s = s.replace('"', '\\"')
        s = s.replace('\n', '\\n')
        s = s.replace('\t', '\\t')
        return f'"{s}"'
    elif isinstance(val, Pair):
        return repr(val)
    elif isinstance(val, Procedure):
        return "#<procedure>"
    elif callable(val):
        return "#<procedure>"
    elif isinstance(val, float):
        return str(val)
    elif isinstance(val, int):
        return str(val)
    else:
        return str(val)

# 算术运算
def scheme_add(*args):
    return sum(args) if args else 0

def scheme_subtract(*args):
    if len(args) == 0:
        raise TypeError("- requires at least 1 argument")
    elif len(args) == 1:
        return -args[0]
    else:
        return args[0] - sum(args[1:])

def scheme_multiply(*args):
    return functools.reduce(operator.mul, args, 1)

def scheme_divide(*args):
    if len(args) == 0:
        raise TypeError("/ requires at least 1 argument")
    elif len(args) == 1:
        return 1.0 / args[0]
    else:
        result = args[0]
        for arg in args[1:]:
            result = int(result / arg) if isinstance(result, int) and isinstance(arg, int) else result / arg
        return result

def scheme_modulo(a, b):
    return a % b

def scheme_quotient(a, b):
    return int(a / b)

def scheme_expt(base, exp):
    return base ** exp

def scheme_abs(x):
    return abs(x)

# 比较运算
def make_comparison(op):
    def compare(*args):
        if len(args) < 2:
            return True
        for i in range(len(args) - 1):
            if not op(args[i], args[i + 1]):
                return False
        return True
    return compare

# 列表操作
def scheme_cons(car, cdr):
    return Pair(car, cdr)

def scheme_car(pair):
    if not isinstance(pair, Pair):
        raise TypeError("car: argument must be a pair")
    return pair.car

def scheme_cdr(pair):
    if not isinstance(pair, Pair):
        raise TypeError("cdr: argument must be a pair")
    return pair.cdr

def scheme_list(*args):
    result = nil
    for arg in reversed(args):
        result = Pair(arg, result)
    return result

def scheme_length(lst):
    count = 0
    while lst != nil:
        if not isinstance(lst, Pair):
            raise TypeError("length: argument must be a list")
        count += 1
        lst = lst.cdr
    return count

def scheme_append(*lists):
    if len(lists) == 0:
        return nil

    def list_to_python(lst):
        result = []
        while lst != nil:
            result.append(lst.car)
            lst = lst.cdr
        return result

    all_elements = []
    for lst in lists:
        all_elements.extend(list_to_python(lst))

    return scheme_list(*all_elements)

# 谓词
def scheme_null(val):
    return val == nil

def scheme_pair(val):
    return isinstance(val, Pair)

def scheme_list_p(val):
    """检查是否为真列表"""
    current = val
    while current != nil:
        if not isinstance(current, Pair):
            return False
        current = current.cdr
    return True

def scheme_number(val):
    return isinstance(val, (int, float)) and not isinstance(val, bool)

def scheme_boolean(val):
    return isinstance(val, bool)

def scheme_symbol(val):
    return isinstance(val, Symbol)

def scheme_string(val):
    return isinstance(val, str) and not isinstance(val, Symbol)

def scheme_procedure(val):
    return isinstance(val, Procedure) or callable(val)

def scheme_zero(val):
    return val == 0

def scheme_even(val):
    return val % 2 == 0

def scheme_odd(val):
    return val % 2 != 0

def scheme_not(val):
    return val is False

def eq_impl(a, b):
    """eq? 实现：符号、数字、布尔按值比较，列表等按同一性比较"""
    # 对于符号、数字、布尔，按值比较
    if isinstance(a, (Symbol, int, float, bool, type(nil))):
        return a == b
    # 对于复合数据，按同一性比较
    return a is b

def equal_impl(a, b):
    """equal? 实现：结构相等"""
    # 先检查类型
    if type(a) != type(b):
        return False

    if isinstance(a, Pair):
        return equal_impl(a.car, b.car) and equal_impl(a.cdr, b.cdr)
    else:
        return a == b

# 输出
def scheme_display(val):
    """打印值，字符串不带引号"""
    if isinstance(val, str):
        print(val, end='')
    else:
        print(scheme_to_string(val), end='')
    return None

def scheme_newline():
    """输出换行"""
    print()
    return None

def create_global_environment():
    """创建包含所有内置过程的全局环境"""
    from environment import Environment

    env = Environment()

    # 算术
    env.define(Symbol('+'), scheme_add)
    env.define(Symbol('-'), scheme_subtract)
    env.define(Symbol('*'), scheme_multiply)
    env.define(Symbol('/'), scheme_divide)
    env.define(Symbol('modulo'), scheme_modulo)
    env.define(Symbol('quotient'), scheme_quotient)
    env.define(Symbol('expt'), scheme_expt)
    env.define(Symbol('abs'), scheme_abs)

    # 比较
    env.define(Symbol('='), make_comparison(operator.eq))
    env.define(Symbol('<'), make_comparison(operator.lt))
    env.define(Symbol('>'), make_comparison(operator.gt))
    env.define(Symbol('<='), make_comparison(operator.le))
    env.define(Symbol('>='), make_comparison(operator.ge))

    # 布尔
    env.define(Symbol('not'), scheme_not)

    # 列表
    env.define(Symbol('cons'), scheme_cons)
    env.define(Symbol('car'), scheme_car)
    env.define(Symbol('cdr'), scheme_cdr)
    env.define(Symbol('list'), scheme_list)
    env.define(Symbol('length'), scheme_length)
    env.define(Symbol('append'), scheme_append)

    # 谓词
    env.define(Symbol('null?'), scheme_null)
    env.define(Symbol('pair?'), scheme_pair)
    env.define(Symbol('list?'), scheme_list_p)
    env.define(Symbol('number?'), scheme_number)
    env.define(Symbol('boolean?'), scheme_boolean)
    env.define(Symbol('symbol?'), scheme_symbol)
    env.define(Symbol('string?'), scheme_string)
    env.define(Symbol('procedure?'), scheme_procedure)
    env.define(Symbol('zero?'), scheme_zero)
    env.define(Symbol('even?'), scheme_even)
    env.define(Symbol('odd?'), scheme_odd)
    env.define(Symbol('eq?'), eq_impl)
    env.define(Symbol('equal?'), equal_impl)

    # 输出
    env.define(Symbol('display'), scheme_display)
    env.define(Symbol('newline'), scheme_newline)

    return env
