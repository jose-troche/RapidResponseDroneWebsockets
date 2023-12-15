#!/usr/bin/env python

import asyncio
import json
import websockets
import functools
from multiprocessing.managers import DictProxy
from drone_commander import send_command_to_drone
from database import (VOICE_COMMAND, DRONE_COMMAND, VIDEO_FRAME, FIRE_LASER,
                      DRONE_TELEMETRY, SEARCHED_OBJECTS, RECOGNIZED_OBJECTS)


async def handler(websocket, db: DictProxy):
    await asyncio.gather(
        receiver_handler(websocket, db),
        sender_handler(websocket, db)
    )

async def receiver_handler(websocket, db: DictProxy):
    last_command = None

    async for message in websocket:
        event = json.loads(message)

        if DRONE_COMMAND in event:
            drone_command = event[DRONE_COMMAND]
            if last_command != drone_command:
                last_command = drone_command
                print(f'Drone command: {drone_command}')
                send_command_to_drone(drone_command)
            else:
                send_command_to_drone('stop')

        if SEARCHED_OBJECTS in event:
            db[SEARCHED_OBJECTS] = set([i.lower().strip() for i in event[SEARCHED_OBJECTS]])

async def sender_handler(websocket, db: DictProxy):
    while True:
        event = {}

        if db[DRONE_TELEMETRY]:
            event[DRONE_TELEMETRY] = db[DRONE_TELEMETRY]

        if db[VIDEO_FRAME]:
            event[VIDEO_FRAME] = db[VIDEO_FRAME]

        if db[RECOGNIZED_OBJECTS]:
            event[RECOGNIZED_OBJECTS] = db[RECOGNIZED_OBJECTS]
            db[RECOGNIZED_OBJECTS] = []

        if db[FIRE_LASER]:
            event[FIRE_LASER] = db[FIRE_LASER]
            db[FIRE_LASER] = False

        if db[VOICE_COMMAND]:
            event[VOICE_COMMAND] = db[VOICE_COMMAND]
            db[VOICE_COMMAND] = None

        await websocket.send(json.dumps(event))

        await asyncio.sleep(0.0333)

async def start_websocket_server(db: DictProxy):
    PORT = 5678
    async with websockets.serve(functools.partial(handler, db=db), '', PORT):
        await asyncio.Future()  # run forever

def websocket_server(db: DictProxy):
    try:
        asyncio.run(start_websocket_server(db))
    except KeyboardInterrupt:
        print("Websocket Server stopping ...")
