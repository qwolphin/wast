import attr
from typing import Generic, TypedDict, TypeVar

T = TypeVar('T')
D = TypeVar('D')

@attr.define()
class Converter(Generic[T, D]):
    typedict: type[D]
    return_type: type[T]

    def __call__(self, val: T | D) -> T:
        return val if isinstance(val, self.return_type) else self.return_type(**val)

class Et(TypedDict, total=True):
    status: int

@attr.define()
class E:
    status: int

def myfn(val: Et) -> E:
    return E(**val)

a = {'status': 1}

b = Converter(Et, E)(a)
c = myfn(a)
