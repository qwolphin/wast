import os

if "DEV" in os.environ:
    from wast import *
    from wast import _
    from wast.fragments import get_fragment
else:
    from stable_wast import *
    from stable_wast import _
    from stable_wast.fragments import get_fragment
