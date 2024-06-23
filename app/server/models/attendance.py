from pydantic import BaseModel, EmailStr, Field

class AttendanceSchema(BaseModel):
    student_id: str
    student_data: dict
    time: str