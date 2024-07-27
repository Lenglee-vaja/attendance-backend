from server.database.index import attendance_collection, student_collection
from server.helper.student import student_helper, ml_search_algorithm, teacher_helper
from server.config.index import faceApp

from fastapi import HTTPException
from bson import ObjectId
import cv2
import numpy as np
import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional
import pandas as pd
from pymongo import DESCENDING


session_embeddings = {}
SECRET_KEY = "lenglee@1234"
class StudentController:
    def __init__(self, collection):
        self.collection = collection
    async def face_prediction(self, image_test, class_code):
    # step 1: Find the time
        face = "Unknown"
        current_time = str(datetime.now())

        # step 1: Take the test image and apply to insightface
        results = faceApp.get(image_test)

        # step 2: Use loop to extract each embedding and pass to ml_search_algorithm
        for res in results:
            embeddings = res["embedding"]
            _id = await ml_search_algorithm(embeddings)
            if _id != "Unknown":
                face = "Known"
                # Fetch student data from MongoDB
                student_data = await self.collection.find_one({"_id": ObjectId(_id)})

                checkPresent = await attendance_collection.find_one({"class_code": class_code, "student_id": str(student_data["_id"])})
                if checkPresent:
                    face = "Present"
                    return face

                # Save student_data to attendance collection
                student_attendance = {
                    "class_code": class_code,
                    "student_id": str(student_data["_id"]),
                    "student_code": student_data["student_code"],
                    "phone": student_data["phone"],
                    "fullname": student_data["fullname"],
                    "class_name": student_data["class_name"],
                    "time": current_time
                }
                await attendance_collection.insert_one(student_attendance)
        
        return face
    


    #========================================auth===============================================

    async def teacher_register(self, teacher_data: dict) -> dict:
        find_teacher = await self.collection.find_one({"phone": teacher_data["phone"]})
        if find_teacher:
            raise HTTPException(status_code=409, detail="USER_ALREADY_EXISTS")
        teacher_data["role"] = "teacher"
        # Hash the password
        password = teacher_data.get("password")
        if password:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            teacher_data["password"] = hashed_password

        teacher = await self.collection.insert_one(teacher_data)
        new_teacher = await self.collection.find_one({"_id": teacher.inserted_id})
        token = self.generate_token(new_teacher["_id"], new_teacher["role"])
        return teacher_helper(new_teacher), token

    async def student_register(self, student_data: dict) -> dict:
        find_student = await self.collection.find_one({"phone": student_data["phone"]})
        if find_student:
            raise HTTPException(status_code=409, detail="USER_ALREADY_EXISTS")
        session_id = student_data.get("session_id")
        if session_id not in session_embeddings or not session_embeddings[session_id]:
            raise HTTPException(status_code=409, detail="SESSION_NOT_FOUND")
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
        token = self.generate_token(new_student["_id"], new_student["role"])
        return student_helper(new_student), token

    async def get_embedding(self, frame, session_id):
        results = faceApp.get(frame, max_num=1)
        for res in results:
            embedding = res["embedding"]
            if embedding is not None:
                session_embeddings[session_id].append(embedding)
        return frame
    async def user_login(self, student_data: dict) -> dict:
        phone = student_data.get("phone")
        password = student_data.get("password")

        user = await self.collection.find_one({"phone": phone})
        
        if not user:
            raise HTTPException(status_code=404, detail="USER_NOT_FOUND")

        if bcrypt.checkpw(password.encode('utf-8'), user["password"]):
            token = self.generate_token(user["_id"], user["role"])
            if user["role"] == "student":
                return token, student_helper(user)
            else:
                return token, teacher_helper(user)
            
        else:
            raise HTTPException(status_code=401, detail="INVALID_PASSWORD")
    def generate_token(self, user_id: str, role: str) -> str:
        payload = {
            "_id": str(user_id),
            "role": role,
            "exp": datetime.utcnow() + timedelta(hours=24)  # Token expires in 24 hours
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        return token
    


    #========================================crud student===============================================


    async def retrieve_students(self,search: Optional[str] = None):
        students = []
        query = {"role": "student"}  # Include the role condition in the query
        sort_order = [("time", DESCENDING)]  # Assuming you have a field like "created_at" to sort by

        print("searcher======>", query)
        if search:
            query["$or"] = [
                {"fullname": {"$regex": search, "$options": "i"}},
                {"class_name": {"$regex": search, "$options": "i"}},
                {"student_code": {"$regex": search, "$options": "i"}},
            ]
        
        async for c in self.collection.find(query).sort(sort_order):
            students.append(student_helper(c))
        
        return students
    
    async def count_students(self, search: Optional[str] = None):
        query = {"role": "student"} 
        print("query count======>", search) # Include the role condition in the query
        if search:
            query["$or"] = [
                {"fullname": {"$regex": search, "$options": "i"}},
                {"class_name": {"$regex": search, "$options": "i"}},
                {"student_code": {"$regex": search, "$options": "i"}},
            ]
        
        count = await self.collection.count_documents(query)
        return count

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
