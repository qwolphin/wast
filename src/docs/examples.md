# Examples

```{note}
`wast` codebase itself is one huge example of using `wast`

Please refer to files `src/render.py` and `src/mk_helpers.py`
```

## Defining a parametrised class

```{doctest}
>>> from wast import _, w, unparse
>>> def mk_cls(name, parent_name, inner):
...     return w.ClassDef(
...         name=name,
...         bases=[_.family._(parent_name)],
...         body=[inner],
...     )
>>> elephant = mk_cls('Elephant', 'Animal', w.Pass())
>>> boa = mk_cls('Snake', 'Reptile', elephant)
>>> print(unparse(boa)) # here is our hat!
class Snake(family.Reptile):
<BLANKLINE>
    class Elephant(family.Animal):
        pass
```

## Using a transformer


```{doctest}
>>> from wast import _, w, parse, unparse, mk_transformer
>>> @mk_transformer(type=w.Name, filter=lambda n, c: n.id.startswith('b'))
... def prefix_b_names(node, ctx):
...     return _(f'my_{node.id}')
>>> tree = parse('a = 1; b = 2; c = 3')
>>> new_tree = prefix_b_names.transform(tree)
>>> print(unparse(new_tree))
a = 1
my_b = 2
c = 3
```
