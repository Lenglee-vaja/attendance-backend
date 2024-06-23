import pandas as pd
import numpy as np
import cv2
import os
from pymongo import MongoClient
from insightface.app import FaceAnalysis
from sklearn.metrics import pairwise
import time
from datetime import datetime

# MongoDB connection details
mongo_uri = "mongodb://your_username:your_password@your_host:your_port/your_database"
client = MongoClient(mongo_uri)
db = client["your_database"]
register_collection = db["academy_register"]
logs_collection = db["academy_logs"]

# Retrieve data from MongoDB
def retrieve_data():
    documents = register_collection.find()
    data = []
    for doc in documents:
        name_role = doc["Name_Role"]
        facial_features = np.array(doc["Facial_Features"], dtype=np.float32)
        data.append({"name_role": name_role, "facial_features": facial_features})
    retrieved_df = pd.DataFrame(data)
    retrieved_df.reset_index(inplace=True, drop=True)
    retrieved_df.columns = ["name_role", 'facial_features']
    retrieved_df[["Name", "Role"]] = retrieved_df["name_role"].apply(lambda x: pd.Series(x.split('@')))
    return retrieved_df[["Name", "Role", "facial_features"]]

# configure face analysis
faceapp = FaceAnalysis(name='buffalo_sc',
                      root='insightface_model',
                      providers=['CPUExecutionProvider'])
faceapp.prepare(ctx_id=0, det_size=(640, 640), det_thresh=0.5)

# ML search algorithm
def ml_search_algorithm(dataframe, feature_column, test_vector, name_role=["Name", "Role"], thresh=0.5):
    dataframe = dataframe.copy()
    x_list = dataframe[feature_column].tolist()
    x = np.asarray(x_list)
    similar = pairwise.cosine_similarity(x, test_vector.reshape(1, -1))
    similar_arr = np.array(similar).flatten()
    dataframe["cosine"] = similar_arr
    data_filter = dataframe.query(f'cosine >= {thresh}')
    if len(data_filter) > 0:
        data_filter.reset_index(drop=True, inplace=True)
        argmax = data_filter['cosine'].argmax()
        person_name, person_role = data_filter.loc[argmax][name_role]
    else:
        person_name = "Unknown"
        person_role = "Unknown"
    return person_name, person_role

# Real-time prediction
class RealTimePred:
    def __init__(self):
        self.logs = dict(name=[], role=[], current_time=[])
    def reset_dict(self):
        self.logs = dict(name=[], role=[], current_time=[])
    def save_logs_mongodb(self):
        dataframe = pd.DataFrame(self.logs)
        dataframe.drop_duplicates('name', inplace=True)
        logs_data = dataframe.to_dict('records')
        if logs_data:
            logs_collection.insert_many(logs_data)
        self.reset_dict()
    def face_prediction(self, image_test, dataframe, feature_column, name_role=["Name", "Role"], thresh=0.5):
        current_time = str(datetime.now())
        results = faceapp.get(image_test)
        test_copy = image_test.copy()
        for res in results:
            x1, y1, x2, y2 = res["bbox"].astype(int)
            embeddings = res["embedding"]
            person_name, person_role = ml_search_algorithm(dataframe, feature_column, test_vector=embeddings, name_role=name_role, thresh=thresh)
            color = (0, 255, 0) if person_name != "Unknown" else (0, 0, 255)
            cv2.rectangle(test_copy, (x1, y1), (x2, y2), color)
            text_gen = person_name
            cv2.putText(test_copy, text_gen, (x1, y1), cv2.FONT_HERSHEY_DUPLEX, 0.7, color, 2)
            cv2.putText(test_copy, current_time, (x1, y2 + 10), cv2.FONT_HERSHEY_DUPLEX, 0.7, color, 2)
            self.logs["name"].append(person_name)
            self.logs["role"].append(person_role)
            self.logs["current_time"].append(current_time)
        return test_copy

# Registration form
class RegistrationForm:
    def __init__(self):
        self.sample = 0
    def reset(self):
        self.sample = 0
    def get_embedding(self, frame):
        results = faceapp.get(frame, max_num=1)
        embeddings = None
        for res in results:
            self.sample += 1
            x1, y1, x2, y2 = res["bbox"].astype(int)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 1)
            text = f"samples: {self.sample}"
            cv2.putText(frame, text, (x1, y1), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 0), 2)
            embeddings = res["embedding"]
        return frame, embeddings
    def save_data_in_mongodb(self, name, role):
        if name and name.strip():
            key = f'{name}@{role}'
        else:
            return 'name_false'
        if 'face_embedding.txt' not in os.listdir():
            return "file_false"
        x_array = np.loadtxt("face_embedding.txt", dtype=np.float32)
        received_samples = int(x_array.size / 512)
        x_array = x_array.reshape(received_samples, 512)
        x_array = np.asarray(x_array)
        x_mean = x_array.mean(axis=0).astype(np.float32).tolist()
        document = {"Name_Role": key, "Facial_Features": x_mean}
        register_collection.insert_one(document)
        os.remove("face_embedding.txt")
        self.reset()
        return True