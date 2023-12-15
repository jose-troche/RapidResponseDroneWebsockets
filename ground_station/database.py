from multiprocessing.managers import DictProxy

# Database keys
VIDEO_FRAME = 'VIDEO_FRAME'
RECOGNIZED_OBJECTS = 'RECOGNIZED_OBJECTS'
SEARCHED_OBJECTS = 'SEARCHED_OBJECTS'
FIRE_LASER = 'FIRE_LASER'
VOICE_COMMAND = 'VOICE_COMMAND'
DRONE_TELEMETRY = 'DRONE_TELEMETRY'
DRONE_COMMAND = 'DRONE_COMMAND'


def db_initialize(db: DictProxy):
    db[VIDEO_FRAME] = None
    db[RECOGNIZED_OBJECTS] = []
    db[SEARCHED_OBJECTS] = set(['laptop', 'f35'])
    db[FIRE_LASER] = False
    db[VOICE_COMMAND] = None
    db[DRONE_TELEMETRY] = {'bat': '100'}

