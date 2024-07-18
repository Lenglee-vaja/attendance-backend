from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class ClassSchema(BaseModel):
    class_name: str = Field(...)
    subject: str = Field(...)
    class_hour: str = Field(...)
    teacher_lat: str = Field(...)
    teacher_long: str = Field(...)

class CheckLocationSchema(BaseModel):
    teacher_lat: str = Field(...)
    teacher_long: str = Field(...)
    student_lat: str = Field(...)
    student_long: str = Field(...)
