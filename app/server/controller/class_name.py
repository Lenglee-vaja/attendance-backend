from server.database.index import class_name_collection
from server.helper.class_name  import class_name_helper
from fastapi import HTTPException
from typing import Optional



class ClassNameController:
    def __init__(self, collection):
        self.collection = collection
    async def add_class_name(self, classData: dict) -> dict:
        class_name = classData["class_name"].upper()
        find_class = await self.collection.find_one({"class_name": class_name})
        if find_class: 
            raise HTTPException(status_code=409, detail="CLASS_NAME_ALREADY_EXISTS")
        classData["class_name"] = class_name
        add_class_name = await self.collection.insert_one(classData)
        new_class = await self.collection.find_one({"_id": add_class_name.inserted_id})
        return class_name_helper(new_class)

    async def retrieve_class_names(self, search: Optional[str] = None):
        class_names = []
        query = {}
        if search:
            query = {"class_name": {"$regex": search, "$options": "i"}}
        
        async for c in self.collection.find(query):
            class_names.append(class_name_helper(c))
        
        return class_names

# Instantiate the StudentService class
class_name_controller = ClassNameController(class_name_collection)
