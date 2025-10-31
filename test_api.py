from nostr_sdk import *
import asyncio
from datetime import timedelta

async def test():
    keys = Keys.generate()
    signer = NostrSigner.keys(keys)
    client = Client(signer)
    await client.add_relay(RelayUrl.parse('wss://relay.damus.io'))
    await client.connect()
    f = Filter().kind(Kind(1)).limit(5)
    events = await client.fetch_events(f, timedelta(seconds=5))
    print(f"Type: {type(events)}")
    print(f"Dir: {dir(events)}")
    print(f"To list: {events.to_vec()}")
    print(f"Length: {len(events.to_vec())}")

asyncio.run(test())
