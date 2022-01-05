import ast, result

tree = ast.parse('a = 1')
val = result.from_built_in(tree)
print(val)
