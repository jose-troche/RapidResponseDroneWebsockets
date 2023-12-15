#!/usr/bin/env python3

import multiprocessing
import time
import sys
from video_receiver import video_receiver
from object_recognizer import object_recognizer
from speech_recognizer import speech_recognizer
from drone_commander import drone_telemetry_listener
from websocket_server import websocket_server
from database import db_initialize

if __name__ == '__main__':

    all_processes = [
        drone_telemetry_listener,
        websocket_server,
        video_receiver,
        object_recognizer,
        speech_recognizer
    ]

    all_processes_count = len(all_processes)

    with multiprocessing.Manager() as manager:
        db = manager.dict()
        db_initialize(db)

        if len(sys.argv) == 1:
            targets = all_processes
        else:
            targets = []
            for arg in sys.argv[1:]:
                if str.isdigit(arg):
                    idx = int(arg)
                    if idx < all_processes_count:
                        targets.append(all_processes[idx])

        processes = []
        for target in targets:
            print(f'Starting process: {target.__name__}')
            processes.append(multiprocessing.Process(target=target, args=(db, )))

        for p in processes:
            p.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print('\nMain process stopping ...')

            # Wait for them to finish
            for p in processes:
                p.join()

            print('Shutdown complete!')
