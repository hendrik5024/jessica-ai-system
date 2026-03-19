import ast
import operator

OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
}


def evaluate(expr: str):
    expr = expr.replace(" ", "")

    def _eval(node):
        if isinstance(node, ast.Num):
            return node.n

        if isinstance(node, ast.BinOp):
            return OPS[type(node.op)](_eval(node.left), _eval(node.right))

        raise ValueError("Unsupported expression")

    tree = ast.parse(expr, mode="eval")
    return _eval(tree.body)
