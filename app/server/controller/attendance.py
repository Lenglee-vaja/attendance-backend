from server.helper.attendance import attendance_helper
from typing import Optional
from pymongo import DESCENDING 
from server.database.index import attendance_collection
from datetime import datetime, timedelta


class AttendanceController:
    def __init__(self, collection):
        self.collection = collection
    async def retrieve_attendances(self,time: Optional[str] = None, search: Optional[str] = None):
            students = []
            query = {}
            if time:
                print("time======>", time)
                # Assuming the time sent from the frontend is in "HH:MM" format
                time_format = "%H:%M"
                # Get the current date and combine it with the provided time
                current_date = datetime.now().date()
                given_time = datetime.strptime(time, time_format).time()
                
                # Combine date and time into a datetime object
                start_time = datetime.combine(current_date, given_time)
                # Add one hour to get the end time
                end_time = start_time + timedelta(hours=1)
                
                # Set end_time to the very last moment of the hour
                end_time = end_time.replace(microsecond=999999)

                print("start_time======>", start_time)
                print("end_time======>", end_time)

                # Query for the datetime range
                query["time"] = {"$gte": start_time, "$lt": end_time}

            if search:
                query["$or"] = [
                    {"class_code": {"$regex": search, "$options": "i"}}
                ]
            print("searcher======>", query)
            sort_order = [("time", DESCENDING)]  
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