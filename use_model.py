import tensorflow as tf
import numpy as np
import cv2
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import plotly.express as px
import pytesseract as pt

def use_model():
    try:
        model = tf.keras.models.load_model('object_detection.h5')
    except Exception as e:
        print("Error loading model:", e)
        exit()

    def object_detection(path):
        # Read image
        image = load_img(path)  # PIL object
        image = np.array(image, dtype=np.uint8)  # 8-bit array (0,255)
        image1 = load_img(path, target_size=(224,224))

        # Data preprocessing
        image_arr_224 = img_to_array(image1) / 255.0  # Convert to array & normalize
        h, w, d = image.shape
        test_arr = image_arr_224.reshape(1, 224, 224, 3)

        # Make predictions
        coords = model.predict(test_arr)

        # Denormalize the values
        denorm = np.array([w, w, h, h])
        coords = coords * denorm
        coords = coords.astype(np.int32)

        # Draw bounding box on top of the image
        xmin, ymin, xmax, ymax = coords[0]
        pt1 = (xmin, ymin)
        pt2 = (xmax, ymax)
        print(pt1, pt2)
        cv2.rectangle(image, pt1, pt2, (0, 255, 0), 3)
        return image, coords

    # Define the path to the image
    path = r'CarNumberData\images\Cars1.png'

    # Call the object_detection function
    image, coords = object_detection(path)

    # Plot the image with the bounding box
    fig = px.imshow(image)
    fig.update_layout(width=700, height=500, margin=dict(l=10, r=10, b=10, t=10), xaxis_title='Figure 14')
    fig.show()

    # Extract region of interest (ROI)
    img = np.array(load_img(path))
    xmin, ymin, xmax, ymax = coords[0]
    roi = img[ymin:ymax, xmin:xmax]

    # Plot the cropped image
    fig = px.imshow(roi)
    fig.update_layout(width=350, height=250, margin=dict(l=10, r=10, b=10, t=10), xaxis_title='Figure 15 Cropped image')
    fig.show()

    # Extract text from the ROI
    text = pt.image_to_string(roi)
    print(text)
if __name__=='__main__':
    pass