In [4]: import json
   ...: 
   ...: def get_json(obj):
   ...:   return json.loads(
   ...:     json.dumps(obj, default=lambda o: getattr(o, '__dict__', str(o)))
   ...:   )

