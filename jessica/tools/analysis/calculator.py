import ast
import operator

OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
}


def safe_eval(expr: str):
    def eval_node(node):
        if isinstance(node, ast.Num):
            return node.n
        if isinstance(node, ast.BinOp):
            return OPERATORS[type(node.op)](
                eval_node(node.left),
                eval_node(node.right),
            )
        raise ValueError("Unsupported expression")

    tree = ast.parse(expr, mode="eval")
    return eval_node(tree.body)
