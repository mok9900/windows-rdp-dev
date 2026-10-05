"""Reverse RDP byte relay. Only the authenticated Windows agent can attach."""
import asyncio
import os
import secrets
from aiohttp import web, WSMsgType

waiting = asyncio.Queue(maxsize=8)
peers = set()

class Peer:
    def __init__(self, ws):
        self.ws = ws
        self.writer = None
        self.done = asyncio.Event()

async def agent(request):
    if not secrets.compare_digest(request.headers.get('Authorization', ''), 'Bearer ' + os.environ['RELAY_TOKEN']):
        raise web.HTTPUnauthorized()
    ws = web.WebSocketResponse(heartbeat=20, max_msg_size=1024*1024)
    await ws.prepare(request)
    peer = Peer(ws)
    peers.add(peer)
    try:
        waiting.put_nowait(peer)
        async for message in ws:
            if message.type == WSMsgType.BINARY and peer.writer:
                peer.writer.write(message.data)
                await peer.writer.drain()
            elif message.type == WSMsgType.ERROR:
                break
    finally:
        peers.discard(peer)
        peer.done.set()
        if peer.writer:
            peer.writer.close()
        await ws.close()
    return ws

async def tcp(reader, writer):
    peer = None
    async def send():
        while data := await reader.read(65536):
            await peer.ws.send_bytes(data)
    tasks = []
    try:
        async with asyncio.timeout(15):
            while True:
                peer = await waiting.get()
                if not peer.ws.closed:
                    break
        peer.writer = writer
        await peer.ws.send_str('OPEN')
        tasks = [asyncio.create_task(send()), asyncio.create_task(peer.done.wait())]
        await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    except (TimeoutError, ConnectionError):
        pass
    finally:
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        if peer:
            await peer.ws.close()
        writer.close()
        await writer.wait_closed()

async def status(request):
    return web.json_response({'agents': len(peers), 'idle': sum(p.writer is None for p in peers)})

async def main():
    app = web.Application()
    app.router.add_get('/agent', agent)
    app.router.add_get('/health', status)
    runner = web.AppRunner(app, access_log=None)
    await runner.setup()
    await web.TCPSite(runner, '127.0.0.1', 8765).start()
    server = await asyncio.start_server(tcp, '127.0.0.1', 13389)
    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    asyncio.run(main())
