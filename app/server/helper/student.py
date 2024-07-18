from sklearn.metrics import pairwise
import numpy as np
import pandas as pd
from server.database.index import student_collection


def student_helper(student) -> dict:
    return {
        "id": str(student["_id"]),
        "student_code": student["student_code"],
        "fullname": student["fullname"],
        "phone": student["phone"],
        "role": student["role"],
        "class_name": student["class_name"],
    }
def teacher_helper(teacher) -> dict:
    return {
        "id": str(teacher["_id"]),
        "fullname": teacher["fullname"],
        "phone": teacher["phone"],
        "role": teacher["role"],
    }
# def ml_search_algorithm(data_frame,test_vector):
#     """
#     consine similarity base search algorithm
#     """
#     # step 1: take the data_frame (collection of data)
#     data_frame = data_frame.copy()
#     #step 2: Index face embeding from the data_frame and convert into array
#     x_list = data_frame["facial_features"].tolist()
#     x = np.asarray(x_list)
#     #step 3: cal. cosine similarity
#     similar = pairwise.cosine_similarity(x, test_vector.reshape(1,-1))
#     similar_arr = np.array(similar).flatten()
#     data_frame["cosine"] = similar_arr
#      #step 4: filter the data
#     thresh=0.5
#     data_filter = data_frame.query(f'cosine >= {thresh}')
#     if len(data_filter) > 0:
#         data_filter.reset_index(drop = True, inplace = True)
#         argmax = data_filter['cosine'].argmax()
#         _id = data_filter.loc[argmax]["_id"]
#     else:
#         _id = "Unknown"
#     return _id

async def ml_search_algorithm(test_vector):
    # Step 1: Fetch data from MongoDB
    cursor = student_collection.find({})
    data_list = await cursor.to_list(length=None)

    # Step 2: Convert list to DataFrame
    data_frame = pd.DataFrame(data_list)

    # Ensure 'facial_features' is a column in the DataFrame
    if 'facial_features' not in data_frame.columns:
        return "Unknown"

    # Filter out 'nan' values from the DataFrame
    data_frame = data_frame.dropna(subset=['facial_features'])

    if len(data_frame) == 0:
        return "No valid facial features found"

    # Step 3: Convert remaining data to NumPy array
    x_list = data_frame["facial_features"].tolist()
    x = np.asarray(x_list)

    # Step 4: Calculate cosine similarity
    similar = pairwise.cosine_similarity(x, test_vector.reshape(1, -1))
    similar_arr = np.array(similar).flatten()
    data_frame["cosine"] = similar_arr

    # Step 5: Filter the data based on similarity threshold
    thresh = 0.5
    data_filter = data_frame.query(f'cosine >= {thresh}')
    if len(data_filter) > 0:
        data_filter.reset_index(drop=True, inplace=True)
        argmax = data_filter['cosine'].argmax()
        _id = data_filter.loc[argmax]["_id"]
    else:
        _id = "Unknown"

    return _id