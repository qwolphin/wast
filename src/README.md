# Crossimport prevention

Generated package modules should complete intialisation in the following order:

- `validators.py`
- `wast.py`
- `helpers.py`
- `utils.py`
- `__init__.py`
