import asyncio
import edge_tts

async def main():
    voices = await edge_tts.list_voices()
    for v in voices:
        if "th-TH" in v["Locale"]:
            print(v["ShortName"], v["Gender"], v.get("FriendlyName"))

asyncio.run(main())
