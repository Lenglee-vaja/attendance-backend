from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class ClassNameSchema(BaseModel):
    class_name: str = Field(...)