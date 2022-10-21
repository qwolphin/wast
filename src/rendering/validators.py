import keyword


def validate_identifier(instance, attribute, value):
    if keyword.iskeyword(value):
        raise ValueError(f"{value} is a Python keyword")

    if value == "*":
        #import alias special case
        return

    if not value.isidentifier():
        raise ValueError(f"{value} is not a valid Python identifier")
