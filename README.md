# facenet-face-recognition

This repository contains a demonstration of face recognition using the FaceNet network (https://arxiv.org/pdf/1503.03832.pdf) and a webcam. Our implementation feeds frames from the webcam to the network to determine whether or not the frame contains an individual or individuals we recognize (i.e individuals that have their image in our image folder).

## How to use

- To install all the requirements for the project run

```bash
	pip install -r requirements.txt
```

- Upload a good photograph of yourself with a valid filename e.g "adam.jpg" into the `images/` directory


- In the root directory. After the modules have been installed you can run the project by using python

```bash
	python facenet.py
```

## NOTE

This is to be used as a smaller part of a facial recognition desktop software

We are using the pyttsx3 library to output our audio message, so if you want to run it using a different TTS engine then you will have to replace the speech library used in facenet.py
