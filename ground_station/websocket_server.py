#!/usr/bin/env python

import asyncio
import json
import websockets
import functools
from multiprocessing.managers import DictProxy
from drone_commander import send_command_to_drone
from database import db_initialize

async def handler(websocket, db: DictProxy):
    last_command = None

    async for message in websocket:
        event = json.loads(message)

        if event['type'] == 'drone_command' and 'command' in event:
            if not last_command == event['command']:
                last_command = event['command']
                print(f"Drone command: {last_command}")
                send_command_to_drone(last_command)
            else:
                send_command_to_drone('stop')

async def start_websocket_server(db: DictProxy):
    PORT = 5678
    async with websockets.serve(functools.partial(handler, db=db), '', PORT):
        await asyncio.Future()  # run forever

def websocket_server(db: DictProxy):
    asyncio.run(start_websocket_server(db))

if __name__ == "__main__":
    import multiprocessing
    import time

    with multiprocessing.Manager() as manager:
        db = manager.dict()
        db_initialize(db)

        multiprocessing.Process(
            target=websocket_server, args=(db, ), daemon=True).start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print('Shutting down')