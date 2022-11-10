# single
class BoundUnderscore(object):
    def __repr__(self):
        return f"BoundUnderscore({self.__inner__})"

    def __init__(self, inner):
        assert isinstance(inner, expr)
        self.__inner__ = inner

    def __getattr__(self, name):
        return BoundUnderscore(Attribute(value=self.__inner__, attr=name))

    def __call__(self, *args, **kwargs):
        return BoundUnderscore(
            Call(
                func=self.__inner__,
                args=args,
                keywords=[keyword(value=v, arg=k) for k, v in kwargs.items()],
            )
        )

    def __getitem__(self, key):
        if isinstance(key, slice):
            key = slice(lower=key.start, upper=key.stop, step=key.step)

        return BoundUnderscore(Subscript(slice=key, value=self.__inner__))

    def __bool__(self):
        raise Exception("Chained comparasions???")

    @property
    def _(self):
        return self.__inner__

