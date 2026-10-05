"""Outbound HTTPS/WebSocket sessions carry local RDP bytes to the gateway."""
import asyncio
import os
import time
from aiohttp import ClientSession, ClientTimeout, WSMsgType

async def connection(session, deadline):
    while time.monotonic() < deadline:
        writer = None
        tasks = []
        try:
            async with session.ws_connect(os.environ['RELAY_URL'].rstrip('/') + '/agent', headers={'Authorization': 'Bearer ' + os.environ['RELAY_TOKEN']}, heartbeat=20, max_msg_size=1024*1024) as ws:
                first = await ws.receive()
                if first.type != WSMsgType.TEXT or first.data != 'OPEN':
                    continue
                reader, writer = await asyncio.open_connection('127.0.0.1', 3389)
                async def transmit():
                    while data := await reader.read(65536):
                        await ws.send_bytes(data)
                async def receive():
                    async for message in ws:
                        if message.type == WSMsgType.BINARY:
                            writer.write(message.data)
                            await writer.drain()
                tasks = [asyncio.create_task(transmit()), asyncio.create_task(receive())]
                await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        except Exception as exc:
            print('Relay reconnect:', type(exc).__name__, flush=True)
            await asyncio.sleep(3)
        finally:
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
            if writer:
                writer.close()
                await writer.wait_closed()

async def main():
    seconds = int(os.environ['SESSION_MINUTES']) * 60
    deadline = time.monotonic() + seconds
    async with ClientSession(timeout=ClientTimeout(total=None, sock_connect=30)) as session:
        tasks = [asyncio.create_task(connection(session, deadline)) for _ in range(4)]
        print('Development reverse RDP agent started.', flush=True)
        try:
            await asyncio.sleep(seconds)
        finally:
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)

if __name__ == '__main__':
    asyncio.run(main())
