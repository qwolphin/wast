import os

if "DEV" in os.environ:
    import dev.wast as w
    from dev.wast import _
    from dev.utils import transformer
else:
    import stable.wast as w
    from stable.wast import _

    # from stable.utils import transformer
