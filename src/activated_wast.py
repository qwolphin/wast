import os

if "DEV" in os.environ:
    import dev as wast
    from dev import n
    from dev.helpers import _
else:
    import stable as wast
    from stable import n
    from stable.helpers import _
