import asyncio
import json
import base64
import websockets
import functools
from multiprocessing.managers import DictProxy
from video_frame_utilities import to_jpg
from drone_commander import send_command_to_drone
from database import (VOICE_COMMAND, DRONE_COMMAND, VIDEO_FRAME,
                      FIRE_LASER, LAST_DRONE_COMMAND, SEARCHED_OBJECTS,
                      DRONE_TELEMETRY, RECOGNIZED_OBJECTS)


async def handler(websocket, db: DictProxy):
    await asyncio.gather(
        receiver_handler(websocket, db),
        sender_handler(websocket, db)
    )

async def receiver_handler(websocket, db: DictProxy):
    while True:
        try:
            message = await websocket.recv()
        except websockets.ConnectionClosedOK:
            break

        event = json.loads(message)

        if DRONE_COMMAND in event:
            drone_command = event[DRONE_COMMAND]
            if db[LAST_DRONE_COMMAND] != drone_command:
                db[LAST_DRONE_COMMAND] = drone_command
                print(f'Drone command: {drone_command}')
                send_command_to_drone(drone_command)
            else:
                send_command_to_drone('stop')

        if SEARCHED_OBJECTS in event:
            db[SEARCHED_OBJECTS] = set([i.lower().strip() for i in event[SEARCHED_OBJECTS]])
            print(f'Set searched objects to: {db[SEARCHED_OBJECTS]}')

async def sender_handler(websocket, db: DictProxy):
    while True:
        event = {}


        # Send telemetry. Empty {} if not able to read from drone
        event[DRONE_TELEMETRY] = db[DRONE_TELEMETRY]

        if db[VIDEO_FRAME] is not None:
            jpg = to_jpg(db[VIDEO_FRAME])
            img_src = 'data:image/jpg;base64,' + base64.b64encode(jpg).decode()
            event[VIDEO_FRAME] = img_src

        if db[RECOGNIZED_OBJECTS]:
            event[RECOGNIZED_OBJECTS] = db[RECOGNIZED_OBJECTS]
            # db[RECOGNIZED_OBJECTS] = []

        if db[FIRE_LASER]:
            event[FIRE_LASER] = db[FIRE_LASER]
            db[FIRE_LASER] = False

        if db[VOICE_COMMAND]:
            event[VOICE_COMMAND] = db[VOICE_COMMAND]
            db[VOICE_COMMAND] = None

        if db[SEARCHED_OBJECTS]:
            event[SEARCHED_OBJECTS] = list(db[SEARCHED_OBJECTS])

        try:
            await websocket.send(json.dumps(event))
        except websockets.ConnectionClosedOK:
            break

        await asyncio.sleep(0.0333)

async def start_websocket_server(db: DictProxy):
    PORT = 5678
    async with websockets.serve(functools.partial(handler, db=db), '', PORT):
        await asyncio.Future()  # run forever

def websocket_server(db: DictProxy):
    try:
        asyncio.run(start_websocket_server(db))
    except KeyboardInterrupt:
        print("Websocket Server stopped")
