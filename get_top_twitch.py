import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
import requests

# Query top streams in Just Chatting or Games
query = """
query {
  streams(first: 10, options: {sort: VIEWER_COUNT}) {
    edges {
      node {
        broadcaster {
          login
          displayName
        }
        viewersCount
      }
    }
  }
}
"""
r = requests.post(
    'https://gql.twitch.tv/gql',
    json={'query': query},
    headers={'Client-ID': 'kimne78kx3ncx6brgo4mv6wki5h1ko'},
    timeout=5
)
data = r.json()
try:
    edges = data['data']['streams']['edges']
    for e in edges:
        n = e['node']
        print(f"Channel: {n['broadcaster']['login']} ({n['broadcaster']['displayName']}) - Viewers: {n['viewersCount']}")
except Exception as ex:
    print("Error:", ex, data)
