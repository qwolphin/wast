import os

if 'DEV' in os.environ:
    import dev.wast as w
    from dev.wast import _
else:
    import stable.wast as w
    from stable.wast import _
