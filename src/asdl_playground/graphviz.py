
import graphviz
dot = graphviz.Digraph(comment='Python ASDL', engine='sfdp')
dot.node('string')
dot.node('identifier')
dot.node('int')
dot.node('constant')
for t in dfns:
    dot.node(t.name)
    if isinstance(t.value, asdl.Product):
        for f in t.value.fields:
            dot.edge(t.name, f.type)
    elif isinstance(t.value, asdl.Sum):
        for s in t.value.types:
            dot.node(s.name)
            dot.edge(t.name, s.name)
            for f in s.fields:
                dot.edge(s.name, f.type)
    else:
        assert False

dot.render('asdl_graph')
