from sklearn.metrics import pairwise
import numpy as np

def student_helper(student) -> dict:
    return {
        "id": str(student["_id"]),
        "fullname": student["fullname"],
        "email": student["email"],
        "phone": student["phone"],
        "role": student["role"],
        "course_of_study": student["course_of_study"],
        "year": student["year"],
    }

def ml_search_algorithm(data_frame,test_vector):
    """
    consine similarity base search algorithm
    """
    # step 1: take the data_frame (collection of data)
    data_frame = data_frame.copy()
    #step 2: Index face embeding from the data_frame and convert into array
    x_list = data_frame["facial_features"].tolist()
    x = np.asarray(x_list)
    #step 3: cal. cosine similarity
    similar = pairwise.cosine_similarity(x, test_vector.reshape(1,-1))
    similar_arr = np.array(similar).flatten()
    data_frame["cosine"] = similar_arr
     #step 4: filter the data
    thresh=0.5
    data_filter = data_frame.query(f'cosine >= {thresh}')
    if len(data_filter) > 0:
        data_filter.reset_index(drop = True, inplace = True)
        argmax = data_filter['cosine'].argmax()
        _id = data_filter.loc[argmax]["id"]
    else:
        _id = "Unknown"
    return _id