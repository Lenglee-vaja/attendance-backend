from server.helper.attendance import attendance_helper
from typing import Optional
from pymongo import DESCENDING 
from server.database.index import attendance_collection


class AttendanceController:
    def __init__(self, collection):
        self.collection = collection
    async def retrieve_attendances(self, search: Optional[str] = None):
            students = []
            query = {}
            sort_order = [("time", DESCENDING)]  # Assuming you have a field like "created_at" to sort by

            
            if search:
                query["$or"] = [
                    {"class_code": {"$regex": search, "$options": "i"}}
                ]
            
            async for c in self.collection.find(query).sort(sort_order):
                students.append(attendance_helper(c))
            
            return students
    
    async def count_attendances(self, search: Optional[str] = None):
        query = {}  # Include the role condition in the query
        if search:
            query["$or"] = [
                {"class_code": {"$regex": search, "$options": "i"}}
            ]
        
        count = await self.collection.count_documents(query)
        return count

attendance_controller = AttendanceController(attendance_collection)