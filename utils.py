import os
import subprocess
import re

from automaton import ThompsonConstruction

from IPython.display import Image, display

def infix2postfix(infix, priority=None):
    """Infix to postfix conversion."""
    if priority is None:
        priority = {'*': 3, '.': 2, '+': 1}
    postfix, op_stack = [], []
    operators = list(priority.keys())
    priority['('] = min(priority.values())-1
    for l in list(infix):
        if l == ' ': continue
        elif l == '(':
            op_stack.append(l)
        elif l == ')':
            top = op_stack.pop()
            while op_stack and top != '(':
                postfix.append(top)
                top = op_stack.pop()
        elif l in operators:
            # operators with higher priority appear towards the top of the stack
            while op_stack and priority[op_stack[-1]] >= priority[l]:
                postfix.append(op_stack.pop())
            op_stack.append(l)
        else: postfix.append(l)

    while op_stack: postfix.append(op_stack.pop())

    return ''.join(postfix)

def postfix_eval(postfix, op_apply):
    """Evaluate a postfix expression."""
    var_stack, operators = [], ['*', '+']
    for l in postfix:
        if l in operators:
            x = var_stack.pop()
            y = var_stack.pop()
            var_stack.append(op_apply(l, x, y))
        else:
            var_stack.append(l)

    if len(var_stack) > 1:
        raise ValueError('Multi-letter variables not allowed.')

    return var_stack[0]

# use of lookahead assertion (?=...) prevents consuming the second pattern
pattern1 = re.compile(r'([a-zA-Z])(?=[a-zA-Z])')
pattern2 = re.compile(r'([a-zA-Z])(\()')
pattern3 = re.compile(r'(\))([a-zA-Z])')
pattern3 = re.compile(r'(\))(\()')
pattern4 = re.compile(r'(\*)([a-zA-Z])')
def add_explicit_concatenation(infix):
    """Add explicit concatenation operator to an infix format.

    The concatenation of two letters 'a' and 'b'
    could be specified using 'ab' or 'a.b'. Transforming
    the former one to postfix format is not possible so
    we have to use the latter. This function adds an explicit
    '.' whenever necessary.

    Example
    --------
    add_explicit_concatenation('a(a|b)*a.bb') -> 'a.(a|b)*.a.b.b'
    """
    infix = re.sub(pattern1, r'\1.', infix)
    infix = re.sub(pattern2, r'\1.\2', infix)
    infix = re.sub(pattern3, r'\1.\2', infix)
    infix = re.sub(pattern4, r'\1.\2', infix)

    return infix

# class ExpressionTree():
# def __init__(self):
# self.root = None
# self.thompson = ThompsonConstruction()

class Node():
    """Node of an expression tree."""
    def __init__(self, value=None, left=None, right=None):
        self.value, self.left, self.right = value, left, right

    def _get_postfix(self, p):
        if self.left is not None:
            self.left._get_postfix(p)
        if self.right is not None:
            self.right._get_postfix(p)
        p.append(self.value)

    def get_postfix(self):
        """Return postfix form of the expression (postorder walk)."""
        p = []; self._get_postfix(p)
        return ''.join(p)

    def get_nodes(self):
        """Return a list of nodes in the (sub-)tree."""
        nodes = set([self])
        if self.left is not None:
            nodes = nodes.union(self.left.get_nodes())

        if self.right is not None:
            nodes = nodes.union(self.right.get_nodes())

        return nodes

    def show_dot(self, filename=None, rankdir='TB'):
        """Display the dot diagram."""
        if filename is None:
            filename = '_pet.png'
        tmp_name, extension = os.path.splitext(os.path.basename(filename))
        extension = extension[1:]

        with open(tmp_name + '.dot', 'w') as h:
            h.write(self.to_dot(rankdir))

        subprocess.call(['dot',
                         '-T{}'.format(extension),
                         tmp_name + '.dot',
                         '-o',
                         filename])
        subprocess.call(['rm', tmp_name + '.dot'])
        display(Image(filename))

    def to_dot(self, rankdir='TB', dpi=100):
        """Visualize with graphviz dot."""
        dot_str = 'digraph FA {\n'
        dot_str += 'graph [dpi={}]\n'.format(dpi)
        dot_str += 'edge [arrowhead="empty"]\n'
        dot_str += 'rankdir={}\n'.format(rankdir)

        node_names = dict()
        nodes = self.get_nodes()
        for node in nodes:
            node_names[node] = '{}'.format(len(node_names))
            dot_str += '"{}"[label="{}", shape=circle]\n'.format(node_names[node],
                                                                 node.value)

        for node in nodes:
            if node.left is not None:
                dot_str += '"{}" -> "{}"\n'.format(node_names[node], node_names[node.left])

            if node.right is not None:
                dot_str += '"{}" -> "{}"\n'.format(node_names[node], node_names[node.right])

        dot_str += '}\n'

        return dot_str

    def __repr__(self):
        return '[{}] \n l: {}, r: {}'.format(self.value,
                                             self.left,
                                             self.right)

def postfix2tree(postfix, token_type=None):
    """Return the root of a parse tree for postfix.

    Parameters
    -----------
    postfix : :obj:`str`
        Expression in postfix format

    token_type : :obj:`callable`
        Function that specifies whether the current letter corresponds to
        a unary operator, a binary operator or a variable.
    """
    if token_type is None:
        token_type = lambda x: 'binary' if x in ['*', '+'] else False

    stack = []
    for l in postfix:
        kind = token_type(l)
        if kind == 'unary':
            v1 = stack.pop()
            stack.append(Node(l, v1))
        elif kind == 'binary':
            v2, v1 = stack.pop(), stack.pop()
            stack.append(Node(l, v1, v2))
        else: stack.append(Node(l))

    if len(stack) > 1:
        raise ValueError('Multi-letter variables not allowed.')

    return stack[0]
