#!/usr/bin/env python3

import threading
import time
import asyncio
from database import FIRE_LASER, LASER_CONNECTED
from multiprocessing.managers import DictProxy
from bleak import BleakClient, BleakScanner


def listen_laser_commander_events(db: DictProxy):
    UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
    UART_TX_CHAR_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"

    loop = asyncio.new_event_loop()

    def handle_disconnect(_: BleakClient):
        print("Laser device was disconnected. Cancelling all tasks in the asyncio loop")
        db[FIRE_LASER] = False
        db[LASER_CONNECTED] = False
        for task in asyncio.all_tasks(loop):
            task.cancel()

    try:
        device = None
        while device is None:
            print("Scanning to find a LASER device ...")
            device = loop.run_until_complete(BleakScanner.find_device_by_name('LASER'))

        client = BleakClient(device, disconnected_callback=handle_disconnect)
        loop.run_until_complete(client.connect())
        print("Connected to LASER device")
        db[LASER_CONNECTED] = True

        uart = client.services.get_service(UART_SERVICE_UUID)
        tx_characteristic = uart.get_characteristic(UART_TX_CHAR_UUID)

        while client:
            if db[FIRE_LASER]:
                # Send a fire command to the laser: 'on' followed by the number of on/off cycles
                print("LASER ON")
                repeat = 5
                loop.run_until_complete(
                    client.write_gatt_char(tx_characteristic, f'on {repeat}'.encode(), response=False))
                time.sleep(repeat*0.3)
                db[FIRE_LASER] = False

    except asyncio.CancelledError:
        pass
    finally:
        loop.close()
        print("Laser Commander stopped")


def laser_commander(db: DictProxy):
    laser_commander_thread: threading.Thread = None
    try:
        while True:
            if laser_commander_thread is None or not laser_commander_thread.is_alive():
                laser_commander_thread = threading.Thread(
                    target=listen_laser_commander_events, args=(db,), daemon=True)
                laser_commander_thread.start()
            time.sleep(1)

    except KeyboardInterrupt:
        time.sleep(0.5)
        print('Laser Commander stopped')

if __name__ == '__main__':
    import multiprocessing
    from database import db_initialize

    with multiprocessing.Manager() as manager:
        db = manager.dict()
        db_initialize(db)

        p = multiprocessing.Process(target=laser_commander, args=(db, ))
        p.start()

        db[FIRE_LASER] = True

        try:
            while db[FIRE_LASER]:
                print(f'On: {time.monotonic()}')
                time.sleep(0.5)

            print(f'Off: {time.monotonic()}')
            p.terminate()
        except KeyboardInterrupt:
            pass
        finally:
            p.join()
            print('Shutting down')
