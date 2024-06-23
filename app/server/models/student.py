from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from fastapi import File, UploadFile

class StudentSchema(BaseModel):
    fullname: str = Field(...)
    email: EmailStr = Field(...)
    phone: str = Field(...)
    course_of_study: str = Field(...)
    year: int = Field(..., gt=0, lt=4)
    session_id: str = Field(...)
    password: str = Field(...)
    class Config:
        schema_extra = {
            "example": {
                "fullname": "John Doe",
                "email": "fXyqQ@example.com",
                "course_of_study": "Computer Science",
                "year": 3,
                "session_id": "09126a9d-ee51-43b1-ac96-e660ad695e1e"
            }
        }
class UpdateStudentModel(BaseModel):
    fullname: Optional[str]
    email: Optional[EmailStr]
    course_of_study: Optional[str]
    year: Optional[int]

    class Config:
        schema_extra = {
            "example": {
                "fullname": "John Doe",
                "email": "fXyqQ@example.com",
                "course_of_study": "Computer Science",
                "year": 3
            }
        }

class StudentData(BaseModel):
    fullname: str
    file: UploadFile = File(...)


class StudentLoginSchema(BaseModel):
    phone: str = Field(...)
    password: str = Field(...)