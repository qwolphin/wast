import json
import asdl

root = asdl.parse('Python.asdl')

with open('asdl.json') as f:
    data = json.load(f)

for x in data['dfns']:
    assert set(x.keys()) == {'name', 'value'}

    assert isinstance(x['name'], str)
    assert (
        set(x['value'].keys()) == {'types', 'attributes'}
        or set(x['value'].keys()) == {'fields', 'attributes'}
    ), x

def parse_type(v):
    if isinstance(v, asdl.SumType):
        return {
            Constructor(
                group=v.name,
                name=t.name,
                fields={parse_field(x) for x in v['fields']},
            ) for t in v[']fields

    elif isinstance(v, asdl.Product):
        return LeafType(v)
    elif isinstance(v, asdl.Field):
        if v.seq:
            return SeqField(v)
        else:
            return SimpleField(v)
    else:
        assert False, v.__class__.__name__

def parse_field(f):
    assert isinstance(f, asdl.Field), f






@define
class Constructor:
    group: str
    name: str
    fields: list

@define
class Field:
    name: str
    type: str

@define
class Structure:
    name: str
    fields: list

@define
class SimpleField(Field):
    is_required: bool

@define
class SeqField(Field):
    pass

