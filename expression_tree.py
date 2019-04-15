"""Example of an expression tree."""
import os
import subprocess
from IPython.display import Image, display

class Expression:
    def description(self):
        raise NotImplementedError

    def evaluate(self):
        raise NotImplementedError

    def postfix(self):
        raise NotImplementedError

    def __add__(self, other):
        return Add(self, other)

    def __radd__(self, other):
        return Add(other, self)

    def __neg__(self):
        return Negate(self)

    def __sub__(self, other):
        return Sub(self, other)

    def __pow__(self, p):
        return Power(self, p)

    def __rsub__(self, other):
        return Sub(other, self)

    def __mul__(self, other):
        return Multiply(self, other)

    def __rmul__(self, other):
        return Multiply(other, self)

    def get_nodes(self):
        """Return a list of nodes in the tree."""
        nodes = set([self])
        if hasattr(self, 'left'):
            nodes = nodes.union(self.left.get_nodes())

        if hasattr(self, 'right'):
            nodes = nodes.union(self.right.get_nodes())
        return nodes

    def show(self, filename=None, rankdir='TB'):
        """Display a dot diagram."""
        if filename is None:
            filename = '_expr.png'
        tmp_name, extension = os.path.splitext(os.path.basename(filename))
        extension = extension[1:]

        with open(tmp_name + '.dot', 'w') as h:
            h.write(self._to_dot(rankdir))

        subprocess.call(['dot',
                         '-T{}'.format(extension),
                         tmp_name + '.dot',
                         '-o',
                         filename])
        subprocess.call(['rm', tmp_name + '.dot'])
        display(Image(filename))


    def _to_dot(self, rankdir='TB', dpi=100):
        """Generate graphviz dot diagram."""
        dot_str = 'digraph Expression {\n'
        dot_str += 'graph [dpi={}]\n'.format(dpi)
        dot_str += 'edge [arrowhead="empty"]\n'
        dot_str += 'rankdir={}\n'.format(rankdir)

        node_names = dict()
        nodes = self.get_nodes()
        for node in nodes:
            node_names[node] = '{}'.format(len(node_names))
            dot_str += '"{}"[label="{}", shape=circle]\n'.format(node_names[node],
                                                                 node.description())

        for node in nodes:
            if hasattr(node, 'left'):
                dot_str += '"{}" -> "{}"\n'.format(node_names[node],
                                                   node_names[node.left])

            if hasattr(node, 'right'):
                dot_str += '"{}" -> "{}"\n'.format(node_names[node],
                                                   node_names[node.right])

        dot_str += '}\n'

        return dot_str

class Constant(Expression):
    def __init__(self, value):
        self.value = value

    def description(self):
        return self.postfix()

    def postfix(self):
        return str(self.value) + ' '

    def evaluate(self):
        return self.value

    def get_nodes(self):
        return set([self])

    def __repr__(self):
        return self.postfix()

class Operator(Expression):
    def __repr__(self):
        return 'expr: ' + self.postfix()

class BinaryOperator(Operator):
    def __init__(self, left, right):
        self.left = handle_numeric_types(left)
        self.right = handle_numeric_types(right)

    def postfix(self):
        return self.left.postfix() + self.right.postfix() + self.description()

class UnaryOperator(Operator):
    def __init__(self, right):
        self.right = right

    def postfix(self):
        return self.right.postfix() + self.description()

class Power(UnaryOperator):
    def __init__(self, right, p):
        super().__init__(right)
        self.p = p

    def description(self):
        return '^'

    def evaluate(self):
        return self.right.evaluate() ** self.p

class Negate(UnaryOperator):
    def __init__(self, right):
        super().__init__(right)

    def description(self):
        return '~'

    def evaluate(self):
        return - self.right.evaluate()

class Multiply(BinaryOperator):
    def __init__(self, left, right):
        super().__init__(left, right)

    def description(self):
        return '*'

    def evaluate(self):
        return self.left.evaluate() * self.right.evaluate()

class Add(BinaryOperator):
    def __init__(self, left, right):
        super().__init__(left, right)

    def description(self):
        return '+'

    def evaluate(self):
        return self.left.evaluate() + self.right.evaluate()

class Sub(BinaryOperator):
    def __init__(self, left, right):
        super().__init__(left, right)

    def description(self):
        return '-'

    def evaluate(self):
        return self.left.evaluate() - self.right.evaluate()

def handle_numeric_types(x):
    if isinstance(x, (int, float)):
        return Constant(x)
    return x
