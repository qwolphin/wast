import os

if "DEV" in os.environ:
    from dev import n
    import dev as wast
    from dev.helpers import _
else:
    import stable.wast as n
    import stable.wast as wast
    from stable.wast import _

    # from stable.utils import transformer
