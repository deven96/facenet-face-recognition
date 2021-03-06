from keras import backend as K
from keras.models import load_model
import time
from multiprocessing.dummy import Pool
K.set_image_data_format('channels_first')
import cv2
import os
import glob
import numpy as np
from numpy import genfromtxt
import tensorflow as tf
import settings
from ai_handler.fr_utils import *
from ai_handler.inception_blocks_v2 import *
import pyttsx3



PADDING = settings.PADDING
ready_to_detect_identity = True

#global opencv face cascade classifier
face_cascade = cv2.CascadeClassifier(settings.CV2_XML)

speech_engine = pyttsx3.init()
speech_engine.setProperty('voice', 'english')  # changes the voice

#load the saved model with a custom triplet loss function defined in utils
FRmodel = load_model(settings.FROZEN_MODEL, custom_objects={'triplet_loss': fr_utils.triplet_loss})


def say_statement(text):
    """pronouces text passed as argument using pyttsx3 engine
    
    Arguments:
    text -- python string to be pronounced by TTS module
    """
    global speech_engine
    print(text)
    speech_engine.say(text)
    speech_engine.runAndWait()


def prepare_database():
    """
    prepares the image database by getting encoding and name of every image
    in the database and parsing it as a dictionary. This is to be replaced 
    with proper database functionality (pre-saved encodings).

    The images are cropped down to their resolute faces and saved 
    """
    global face_cascade

    database = {}

    # load all the images of individuals to recognize into the database
    for _file in glob.glob(settings.GLOB_IMAGE_DATABASE):
        identity = os.path.splitext(os.path.basename(_file))[0]
        image = cv2.imread(_file)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        try:
            for (x, y, w, h) in faces:
                x1 = x
                y1 = y
                x2 = x+w
                y2 = y+h
            #crop out just the faces so the network just takes into account only faces
            cropped_path = str(os.path.join(settings.CROPPED_IMAGES, identity)) + '.jpg'
            cv2.imwrite(cropped_path, image[y1:y2, x1:x2])
            database[identity] = img_path_to_encoding(cropped_path, FRmodel)
        except:
            sys.exit(f"No face detected for {_file} image in database")

    return database

def webcam_face_recognizer(database):
    """
    Runs a loop that extracts images from the computer's webcam and determines whether or not
    it contains the face of a person in our database.

    If it contains a face, an audio message will be played welcoming the user.
    If not, the program will process the next frame from the webcam
    """
    global ready_to_detect_identity, face_cascade

    cv2.namedWindow(settings.WINDOW_NAME)
    vc = cv2.VideoCapture(0)
    
    while vc.isOpened():
        _, frame = vc.read()
        img = frame

        # We do not want to detect a new identity while the program is in the process of identifying another person
        if ready_to_detect_identity:
            img = process_frame(img, frame, face_cascade)   
        
        key = cv2.waitKey(100)
        cv2.imshow(settings.WINDOW_NAME, img)

        if key == 27: # exit on ESC
            break
    cv2.destroyWindow(settings.WINDOW_NAME)

def process_frame(img, frame, face_cascade):
    """
    Determine whether the current frame contains the faces of people from our database
    """
    global ready_to_detect_identity
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    # Loop through all the faces detected and determine whether or not they are in the database
    identities = []
    for (x, y, w, h) in faces:
        x1 = x-PADDING
        y1 = y-PADDING
        x2 = x+w+PADDING
        y2 = y+h+PADDING

        img = cv2.rectangle(frame,(x1, y1),(x2, y2),(255,0,0),2)

        identity = find_identity(frame, x1, y1, x2, y2)

        if identity is not None:
            identities.append(identity)

    if identities != []:
        ready_to_detect_identity = False
        pool = Pool(processes=1) 
        # We run this as a separate process so that the camera feedback does not freeze
        handler = pool.apply_async(welcome_users, [identities])
        handler.get()
    return img

def find_identity(frame, x1, y1, x2, y2):
    """
    Determine whether the face contained within the bounding box exists in our database
    It creates a crop of just the face detected in the image

    x1,y1_____________
       |              |
       |              |
       |______________x2,y2

    """
    height, width, channels = frame.shape
    # The padding is necessary since the OpenCV face detector creates the bounding box around the face and not the head
    part_image = frame[max(0, y1):min(height, y2), max(0, x1):min(width, x2)]
    
    return who_is_it(part_image, database, FRmodel)

def who_is_it(image, database, model):
    """
    Implements face recognition by finding who is the person on the image_path image.
    
    Arguments:
    image_path -- path to an image
    database -- database containing image encodings along with the name of the person on the image
    model -- your Inception model instance in Keras
    
    Returns:
    min_dist -- the minimum distance between image_path encoding and the encodings from the database
    identity -- string, the name prediction for the person on image_path
    """
    encoding = img_to_encoding(image, model)
    
    min_dist = 100
    identity = None
    
    # Loop over the database dictionary's names and encodings.
    for (name, db_enc) in database.items():
        
        # Compute L2 distance between the target "encoding" and the current "emb" from the database.
        dist = np.linalg.norm(db_enc - encoding)

        print('distance for %s is %s' %(name, dist))

        # If this distance is less than the min_dist, then set min_dist to dist, and identity to name
        if dist < min_dist:
            min_dist = dist
            identity = name
    
    if min_dist > settings.MIN_DISTANCE:
        return None
    else:
        return str(identity)

def welcome_users(identities):
    """ Outputs a welcome audio message to the users 
    
    Arguments:
    identities: list of name strings to welcome
    """
    global ready_to_detect_identity
    welcome_message = 'Welcome '

    if len(identities) == 1:
        welcome_message += '%s, have a nice day.' % identities[0]
    else:
        for identity_id in range(len(identities)-1):
            welcome_message += '%s, ' % identities[identity_id]
        welcome_message += 'and %s, ' % identities[-1]
        welcome_message += 'have a nice day!'

    say_statement(welcome_message)

    # Allow the program to start detecting identities again
    ready_to_detect_identity = True

if __name__ == "__main__":
    database = prepare_database()
    say_statement("starting facial recognition software")
    webcam_face_recognizer(database)


# ### References:
# 
# - Florian Schroff, Dmitry Kalenichenko, James Philbin (2015). [FaceNet: A Unified Embedding for Face Recognition and Clustering](https://arxiv.org/pdf/1503.03832.pdf)
# - Yaniv Taigman, Ming Yang, Marc'Aurelio Ranzato, Lior Wolf (2014). [DeepFace: Closing the gap to human-level performance in face verification](https://research.fb.com/wp-content/uploads/2016/11/deepface-closing-the-gap-to-human-level-performance-in-face-verification.pdf) 
# - The pretrained model we use is inspired by Victor Sy Wang's implementation and was loaded using his code: https://github.com/iwantooxxoox/Keras-OpenFace.
# - Our implementation also took a lot of inspiration from the official FaceNet github repository: https://github.com/davidsandberg/facenet 
# 
