import os

if "DEV" in os.environ:
    from dev import *
    from dev import _
    from dev.fragments import get_fragment
else:
    from stable import *
    from stable import _
    from stable.fragments import get_fragment
