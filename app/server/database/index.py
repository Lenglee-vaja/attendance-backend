import motor.motor_asyncio

MONGO_DETAILS = "mongodb+srv://HomeFind:RH5qHJJWiMJvaUKA@cluster0.xflsd3v.mongodb.net/?retryWrites=true&w=majority"

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

database = client.attendance
student_collection = database.get_collection("students_collection")
attendance_collection = database.get_collection("attendance_collection")
class_collection = database.get_collection("class_collection")
class_name_collection = database.get_collection("class_name_collection")