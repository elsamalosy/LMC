import streamlit as st
import PIL
import tensorflow_hub as hub
import numpy as np
import pandas as pd
from geopy.geocoders import Nominatim

model_url = 'https://tfhub.dev/google/on_device_vision/classifier/landmarks_classifier_africa_V1/1'
labels = 'landmarks_classifier_egypt_V1_label_map.csv'
df = pd.read_csv(labels)
labels = dict(zip(df.id, df.name))


def image_processing(image):
    img_shape = (321, 321)
    model = hub.load(model_url)
    infer = model.signatures["default"]
    
    img = PIL.Image.open(image)
    img = img.resize(img_shape)
    img1 = img
    img = np.array(img) / 255.0
    img = img[np.newaxis].astype(np.float32)  # Ensure the input dtype is float32
    
    result = infer(tf.constant(img))
    output_key = list(result.keys())[0]  # Get the first key of the result dictionary
    class_idx = np.argmax(result[output_key].numpy()[0])  # Access predictions using the correct key
    prediction = labels[class_idx]
    
    return prediction, img1





def get_map(loc):
    geolocator = Nominatim(user_agent="Your_Name")
    location = geolocator.geocode(loc)
    return location.address, location.latitude, location.longitude

def run():
    st.title("Landmark Recognition")
    img = PIL.Image.open('logo.png')
    img = img.resize((256,256))
    st.image(img)
    img_file = st.file_uploader("Choose your Image", type=['png', 'jpg'])
    if img_file is not None:
        save_image_path = './Uploaded_Images/' + img_file.name
        with open(save_image_path, "wb") as f:
            f.write(img_file.getbuffer())
        prediction, image = image_processing(save_image_path)
        st.image(image)
        st.header("📍 **Predicted Landmark is: " + prediction + '**')
        try:
            address, latitude, longitude = get_map(prediction)
            st.success('Address: '+address )
            loc_dict = {'Latitude': latitude, 'Longitude': longitude}
            st.subheader('✅ **Latitude & Longitude of '+prediction+'**')
            st.json(loc_dict)
            data = [[latitude, longitude]]
            df = pd.DataFrame(data, columns=['lat', 'lon'])
            st.subheader('✅ **'+prediction +' on the Map**'+'🗺️')
            st.map(df)
        except Exception as e:
            st.warning("No address found!!")

run()
