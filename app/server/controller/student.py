from server.database.index import attendance_collection, student_collection
from server.helper.student import student_helper, ml_search_algorithm
from server.config.index import faceApp
from server.helper.index import ErrorResponseModel

from bson import ObjectId
import cv2
import numpy as np
import os
import logging
import bcrypt
import jwt
from datetime import datetime, timedelta



logger = logging.getLogger(__name__)
session_embeddings = {}
SECRET_KEY = "lenglee@1234"
class StudentController:
    def __init__(self, collection):
        self.collection = collection
    async def face_prediction(self,image_test):
        # step1: find the time
        current_time = str(datetime.now())
        data_frame = self.collection.find()
        # step1: take the test image and apply to insightface
        results = faceApp.get(image_test)
        # step2: use loop the extract each embedding and past to ml_search_algorithem
        for res in results:
            embeddings = res["embedding"]
            _id = ml_search_algorithm(data_frame,test_vector=embeddings)
            if _id != "Unknown":
                student_data = self.collection.find_one({"_id": ObjectId(_id)})
                #save student_data to attendance collection
                student_attendance = {
                    "student_id": _id,
                    "student_number": student_data["student_number"],
                    "phone": student_data["phone"],
                    "fullname": student_data["fullname"],
                    "classroom": student_data["classroom"],
                    "time": current_time
                }
                await attendance_collection.insert_one(student_attendance)
        return _id
    async def retrieve_students(self):
        students = []
        async for student in self.collection.find():
            students.append(student_helper(student))
        return students

    async def add_student(self, student_data: dict) -> dict:
        session_id = student_data.get("session_id")
        print("session_id", session_id)
        print("embeddings", session_embeddings)
        if session_id not in session_embeddings or not session_embeddings[session_id]:
            return "embedding_false"
        x_array = np.array(session_embeddings[session_id], dtype=np.float32)
        x_mean = x_array.mean(axis=0)
        x_mean = x_mean.astype(np.float32)
        student_data["facial_features"] = x_mean.tolist()
        student_data["role"] = "student"
        # Hash the password
        password = student_data.get("password")
        if password:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            student_data["password"] = hashed_password

        student = await self.collection.insert_one(student_data)
        del session_embeddings[session_id]
        new_student = await self.collection.find_one({"_id": student.inserted_id})
        return student_helper(new_student)

    async def get_embedding(self, frame, session_id):
        results = faceApp.get(frame, max_num=1)
        embeddings = None
        for res in results:
            x1, y1, x2, y2 = res["bbox"].astype(int)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 1)
            text = "ດີຫຼາຍ"
            cv2.putText(frame, text, (x1, y1), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 0), 2)
            embedding = res["embedding"]
            if embedding is not None:
                session_embeddings[session_id].append(embedding)
        return frame
    async def login_student(self, student_data: dict) -> dict:
        phone = student_data.get("phone")
        password = student_data.get("password")

        student = await self.collection.find_one({"phone": phone})
        
        if not student:
            return {"error": "Invalid email or password"}

        if bcrypt.checkpw(password.encode('utf-8'), student["password"]):
            token = self.generate_token(student["_id"], student["role"])
            return token, student_helper(student)
        else:
            return {"error": "Invalid email or password"}
    def generate_token(self, student_id: str, role: str) -> str:
        payload = {
            "student_id": str(student_id),
            "role": role,
            "exp": datetime.utcnow() + timedelta(hours=24)  # Token expires in 24 hours
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        return token
    async def register_student(self, student_data: dict) -> dict:
        file = student_data.get("file")

        if file is None:
            return ErrorResponseModel("Error", 400, "File not provided")

        # Read the image file in binary mode
        image_data = await file.read()

        # Decode the image data using OpenCV
        image_array = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        if image is None:
            return ErrorResponseModel("Error", 400, "Invalid image format")
        # Process the image and continue with your logic
        results = faceApp.get(image, max_num=1)
        if not results:
            return ErrorResponseModel("Error", 400, "No face detected")
        print("after results")
        embeddings = results[0]["embedding"]
        np.savetxt("face_embedding.txt", embeddings)
        x_array = np.loadtxt("face_embedding.txt", dtype=np.float32)
        received_samples = int(x_array.size / 512)
        x_array = x_array.reshape(received_samples, 512)
        x_mean = x_array.mean(axis=0).astype(np.float32).tolist()
        student_data["facial_features"] = x_mean
        await self.collection.insert_one(student_data)
        os.remove("face_embedding.txt")

        return {"message": "Student added successfully"}

    async def retrieve_student(self, id: str) -> dict:
        student = await self.collection.find_one({"_id": ObjectId(id)})
        if student:
            return student_helper(student)
        return None

    async def update_student(self, id: str, data: dict):
        if len(data) < 1:
            return False
        student = await self.collection.find_one({"_id": ObjectId(id)})
        if student:
            updated_student = await self.collection.update_one(
                {"_id": ObjectId(id)}, {"$set": data}
            )
            if updated_student.modified_count > 0:
                return True
        return False

    async def delete_student(self, id: str):
        student = await self.collection.find_one({"_id": ObjectId(id)})
        if student:
            await self.collection.delete_one({"_id": ObjectId(id)})
            return True
        return False

# Instantiate the StudentService class
student_controller = StudentController(student_collection)
