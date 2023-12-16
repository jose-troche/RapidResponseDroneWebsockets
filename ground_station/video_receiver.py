#!/usr/bin/env python3

import cv2
from database import VIDEO_FRAME
from multiprocessing.managers import DictProxy

# Captures video frames from the drone and publishes them to the db
# so other processes can grab them.
def video_receiver(db: DictProxy):
    VIDEO_URL = 'udp://0.0.0.0:11111'
    is_frame_captured = False
    
    try:
        while True:
            if not is_frame_captured:
                print('Trying to acquire video feed ...')
                db[VIDEO_FRAME] = None
                capture = cv2.VideoCapture(VIDEO_URL)
            else:
                db[VIDEO_FRAME] = frame

            is_frame_captured, frame = capture.read()
    except KeyboardInterrupt:
        pass
    finally:
        print('Video Receiver stopped')
        if capture:
            capture.release()
        cv2.destroyAllWindows()
