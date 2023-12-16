import time
import threading
import boto3
import video_frame_utilities
from laser_commander import fire_laser
from database import VIDEO_FRAME, RECOGNIZED_OBJECTS, SEARCHED_OBJECTS, FIRE_LASER
from multiprocessing.managers import DictProxy

# Gets the current video frame and sends it to rekognition for object/label detection
# Updates the db with the objects recognized/detected
# It also fires the laser if searched objects are found
def object_recognizer(db: DictProxy):
    rekognition = boto3.client('rekognition', region_name='us-east-2')

    try:
        while True:
            frame = db[VIDEO_FRAME]
            if not frame is None:
                cropped_frame = video_frame_utilities.crop_margin(frame, 300) # Original 960x720
                image_bytes = video_frame_utilities.to_jpg(cropped_frame)

                try:
                    response = rekognition.detect_labels(
                        Image={'Bytes': image_bytes},
                        MinConfidence = 80.0
                    )
                    recognized_objects_list = [ label['Name'].lower().strip() for label in response['Labels'] ]
                    db[RECOGNIZED_OBJECTS] = response['Labels'];
                    # print(recognized_objects_list)

                    for object in recognized_objects_list:
                        if object in db[SEARCHED_OBJECTS]:
                            # Turn on laser, since object was found
                            fire_laser()
                            db[FIRE_LASER] = True
                            break

                except Exception as e:
                    print('Error when calling AWS Rekognition', e)

            time.sleep(0.75)
    except KeyboardInterrupt:
        time.sleep(0.5)
        print('Object Recognizer stopped')
