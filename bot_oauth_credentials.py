"""Load application OAuth configuration without copying secrets into source."""
import ast
import os
from pathlib import Path

def get_client_credential(platform, name):
    env = 'BP3_' + platform.upper() + '_' + name.removeprefix('DEFAULT_')
    if os.environ.get(env): return os.environ[env]
    source = Path(__file__).resolve().parent.parent / 'broadcast playroom dev' / (platform + '_oauth.py')
    try:
        tree = ast.parse(source.read_text(encoding='utf-8'))
        for node in tree.body:
            if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
                value = ast.literal_eval(node.value)
                return value if isinstance(value, str) else ''
    except (OSError, SyntaxError, ValueError): pass
    return ''
