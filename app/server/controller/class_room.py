from server.database.index import class_collection, student_collection
from server.helper.class_room  import class_helper
from server.database.index import class_collection
import datetime
import random
from bson import ObjectId
from fastapi import HTTPException
from typing import Optional
from pymongo import DESCENDING
import math





class ClassRoomController:
    def __init__(self, collection):
        self.collection = collection
    def generate_class_code(self):
        prefix = "FNS"
        random_digits = ''.join([str(random.randint(0, 9)) for _ in range(7)])
        return f"{prefix}{random_digits}"
    @staticmethod
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371  # Earth radius in kilometers
        d_lat = math.radians(lat2 - lat1)
        d_lon = math.radians(lon2 - lon1)
        a = math.sin(d_lat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        return distance
    
    async def check_location(self, checkLocation: dict) -> dict:
        teacher_lat = checkLocation["teacher_lat"]
        teacher_long = checkLocation["teacher_long"]
        student_lat = checkLocation["student_lat"]
        student_long = checkLocation["student_long"]
        print("student_lat =============+>", student_lat)
        distance = self.haversine(float(teacher_lat), float(teacher_long), float(student_lat), float(student_long))
        radius = 0.1  # in kilometers
        print("distance =============+>", distance)
        if distance <= radius:
            return {
                "distance": distance,
                "status": "in_range"
            }
        else:
            return {
                "distance": distance,
                "status": "out_of_range"
            }
    async def add_class(self, classData: dict, payload) -> dict:
        _id = payload.get("_id")
        teacher_data = await student_collection.find_one({"_id": ObjectId(_id)})
        if not teacher_data:
            raise HTTPException(status_code=404, detail="TEACHER_NOT_FOUND")
        classData["time"] = datetime.datetime.now()
        classData["class_code"] = self.generate_class_code()
        classData["teacher_id"] = str(teacher_data["_id"])
        classData["teacher_fullname"] = teacher_data["fullname"]
        add_class = await self.collection.insert_one(classData)
        new_class = await self.collection.find_one({"_id": add_class.inserted_id})
        return class_helper(new_class)

    async def retrieve_classes(self, search: Optional[str] = None):
        classes = []
        query = {}
        sort_order = [("time", DESCENDING)]  # Assuming you have a field like "created_at" to sort by

        if search:
            query = {"$or": [
                {"class_name": {"$regex": search, "$options": "i"}},
                {"class_code": {"$regex": search, "$options": "i"}},
                {"subject": {"$regex": search, "$options": "i"}},
            ]}

        async for c in self.collection.find(query).sort(sort_order):
            classes.append(class_helper(c))

        return classes
    # Retrieve a student with a matching ID
    async def retrieve_class(self,class_code: str) -> dict:
        class_room = await self.collection.find_one({"class_code": class_code})
        if class_room:
            return class_helper(class_room)

# Instantiate the StudentService class
class_controller = ClassRoomController(class_collection)
