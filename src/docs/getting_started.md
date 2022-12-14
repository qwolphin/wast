# Getting started

Core of the package is the `wast.nodes` autogenerated module.
That's where AST nodes are defined (very similar to those from stdlib `ast` module).

By convention `wast.nodes` is imported as `w` to make accessing node classes easier.
Let's generate our very first line of code:

```{doctest}
>>> from wast import w, unparse
>>> unparse(w.Name('some_name'))  # Name is a node for things like variable name
'some_name'
```

`unparse()` is a function that turns *wast* tree into text with the code it represents (a single node also counts as a tree).
The opposite function is called `parse()`


```{doctest}
>>> from wast import _, w, unparse
>>> attrib = w.Attribute(value=w.Name('some_name'), attr='my_attr')
>>> unparse(attrib)
'some_name.my_attr'
>>> unparse(_.some_name.my_attr)
'some_name.my_attr'
```

Any language construct (assignment, class definition, subscription) can be represented using corresponding node from `wast.nodes`.
In case of most statements and very simple expressions it's totally OK to use those nodes as is
(with defaults, validation and shortcuts still being a major improvement over stdlib `ast`)

But a simple attribute access already lookes very unreadable, and here is where magic underscore comes into play.
It's just a helper for building expressions, and can express most (but not all) kinds of expressions.
The underscore is an object with some overloads to use it as "expression root"

Here is a more involved example:

```{doctest}
>>> from wast import _, unparse
>>> expr = _.my_fn(arg1=_.some_list[_.index]) + _.other_obj.user.email + _["some_string"]
>>> print(unparse(expr))
my_fn(arg1=some_list[index]) + other_obj.user.email + 'some_string'
```
