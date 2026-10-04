"""环境：变量绑定和作用域管理"""

class Environment:
    """环境类，管理变量绑定和词法作用域"""

    def __init__(self, parent=None, bindings=None):
        self.parent = parent
        self.bindings = bindings if bindings is not None else {}

    def define(self, name, value):
        """在当前环境中定义变量"""
        self.bindings[name] = value

    def get(self, name):
        """查找变量的值"""
        if name in self.bindings:
            return self.bindings[name]
        elif self.parent:
            return self.parent.get(name)
        else:
            raise NameError(f"undefined variable: {name}")

    def set(self, name, value):
        """修改变量的值（在最近的定义处）"""
        if name in self.bindings:
            self.bindings[name] = value
        elif self.parent:
            self.parent.set(name, value)
        else:
            raise NameError(f"undefined variable: {name}")
