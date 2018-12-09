import os


#name of the window opened for webcam recognition
WINDOW_NAME = "FaceRec - preview"


CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))


#ai model settings
_FLOATX = 'float32'
IMAGE_SIZE = (96, 96)
GLOB_IMAGE_DATABASE = "images/*"
IMAGE_EXAMPLE_DIR = os.path.join(CURRENT_DIR, "images", "examples")
MODEL_INPUT_SHAPE = (3, 96, 96)
MIN_DISTANCE = 0.52 #defines the minimum distance used by the triplet loss function

PADDING = 50 #image padding used for cv2


#open cv settings
CV2_XML = os.path.join(CURRENT_DIR, "opencv", "haarcascade_frontalface_default.xml")
