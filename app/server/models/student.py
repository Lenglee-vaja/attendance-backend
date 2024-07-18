from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class StudentSchema(BaseModel):
    fullname: str = Field(...)
    student_code: str = Field(...)
    phone: str = Field(...)
    class_name: str = Field(...)
    session_id: str = Field(...)
    password: str = Field(...)
    class Config:
        schema_extra = {
            "example": {
                "fullname": "John Doe",
                "student_code": "fXyqQ@example.com",
                "class_name": "Computer Science",
                "phone": "2056941975",
                "session_id": "09126a9d-ee51-43b1-ac96-e660ad695e1e"
            }
        }
class TeacherSchema(BaseModel):
    fullname: str = Field(...)
    phone: str = Field(...)
    password: str = Field(...)


class UpdateStudentModel(BaseModel):
    fullname: Optional[str]
    email: Optional[EmailStr]
    class_name: Optional[str]
    year: Optional[int]

    class Config:
        schema_extra = {
            "example": {
                "fullname": "John Doe",
                "email": "fXyqQ@example.com",
                "class_name": "Computer Science",
                "year": 3
            }
        }


class StudentLoginSchema(BaseModel):
    phone: str = Field(...)
    password: str = Field(...)