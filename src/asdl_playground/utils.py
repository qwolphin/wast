import ast

class ExprTransformer(ast.NodeTransformer):
    def visit_Expr(self, node):
        if isinstance(node.expr, ast.Name):


def load_expr(filename):
    with open(filename) as f:
        tree = parse(
