import requests

url = "http://127.0.0.1:8999/api/tts"
params = {
    "text": "Somchai พูดว่า สวัสดีครับสตรีมเมอร์",
    "gender": "female",
    "rate": "+0%",
    "pitch": "+0Hz"
}
try:
    r = requests.get(url, params=params)
    print("Status:", r.status_code, "Len:", len(r.content), "Content-Type:", r.headers.get('content-type'))
except Exception as e:
    print("Error:", e)
