import keyword

def validate_identifier(val):
    if keyword.iskeyword(val):
        raise ValueError(f'{val} is a Python keyword')

    if not name.isidentifier():
        raise ValueError(f'{val} is not a valid Python identifier')
