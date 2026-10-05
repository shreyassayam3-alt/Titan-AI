import importlib.util
import os
import sys

print('cwd', os.getcwd())
print('root on path', os.getcwd() in sys.path)
for name in ['core', 'core.memory', 'agents', 'agents.research']:
    spec = importlib.util.find_spec(name)
    print(name, '->', spec.origin if spec else None)
