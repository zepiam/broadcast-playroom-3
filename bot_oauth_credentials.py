"""Load application OAuth configuration without copying secrets into source."""
import ast
import os
from pathlib import Path

_BUILTIN_CREDENTIALS = {
    'twitch': {
        'DEFAULT_CLIENT_ID': 'ocom4fivxnkstug13o1jvbvfc50dup',
        'DEFAULT_CLIENT_SECRET': 'n7mswu0nk8sppc9vb41ize9hci8a5z',
    },
    'kick': {
        'DEFAULT_CLIENT_ID': '01M00PCT31WGYVBKBQBPM7Z8QQ',
        'DEFAULT_CLIENT_SECRET': '6e8c1657e99d62f82ad72096bc23295eaaa95d8c53f76a24766da0bdf049cbd4',
    }
}

def get_client_credential(platform, name):
    env = 'BP3_' + platform.upper() + '_' + name.removeprefix('DEFAULT_')
    if os.environ.get(env):
        return os.environ[env]
    source = Path(__file__).resolve().parent.parent / 'broadcast playroom dev' / (platform + '_oauth.py')
    try:
        if source.is_file():
            tree = ast.parse(source.read_text(encoding='utf-8'))
            for node in tree.body:
                if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
                    value = ast.literal_eval(node.value)
                    if isinstance(value, str) and value:
                        return value
    except (OSError, SyntaxError, ValueError):
        pass
    return _BUILTIN_CREDENTIALS.get(platform, {}).get(name, '')
