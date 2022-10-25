def __call__(self, *attrs):
    ret = self
    for name in reversed(attrs):
        ret = Attribute(value=ret, attr=name)

    return BoundUnderscore(ret)
