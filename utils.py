def infix2postfix(infix):
    """Infix to postfix conversion."""
    priority = {'*': 2, '+': 1, '(': 0}
    postfix, op_stack, operators = [], [], ['*', '+']
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
