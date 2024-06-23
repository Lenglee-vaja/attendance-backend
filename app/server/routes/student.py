from fastapi import APIRouter, Form, UploadFile, File, Body, Depends
from fastapi.encoders import jsonable_encoder
from server.controller.student import student_controller
from server.config.index import faceApp
import uuid
from typing import List

import numpy as np
import cv2
from server.helper.index import (
    ErrorResponseModel,
    ResponseModel,
    ResponseLogin,
    get_current_student
)
from server.models.student import (
    StudentSchema,
    StudentLoginSchema,
    UpdateStudentModel,
    StudentData
)
from server.controller.student import session_embeddings
router = APIRouter()

@router.post("/", response_description="student data added into the database")
async def add_student_data(student: StudentSchema = Body(...)):
    student = jsonable_encoder(student)
    new_student = await student_controller.add_student(student)
    return ResponseModel(new_student, "student added successfully.")

@router.post("/login", response_description="student login")
async def login_data(student: StudentLoginSchema = Body(...)):
    student = jsonable_encoder(student)
    token, user = await student_controller.login_student(student)
    return ResponseLogin(token, user, "successfully")

@router.get("/", response_description="Students retrieved")
async def get_students(current_student: dict = Depends()):
    students = await student_controller.retrieve_students(get_current_student)
    if students:
        return ResponseModel(students, "Students data retrieved successfully")
    return ResponseModel(students, "Empty list returned")

# @router.post("", response_description="Add new student")
# async def add_student(fullname: str = Form(...),
#     file: UploadFile = File(...)
# ):
#     student_data = {
#         "fullname": fullname,
#         "file": file
#     }
#     # student_data = jsonable_encoder(student_data)
#     result = await student_controller.register_student(student_data)
#     return ResponseModel(result, "Student added successfully")

# @router.post("/upload_frame", response_description="upload_frame")
# async def upload_frame(file: UploadFile = File(...)):
#     contents = await file.read()
#     nparr = np.frombuffer(contents, np.uint8)
#     img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#     reg_img, session_id = await student_controller.get_embedding(img)
#     print("step1")
#     # _, img_encoded = cv2.imencode('.jpg', reg_img)
#     return {"status": "success", "id": session_id}

@router.post("/upload_frames", response_description="upload_frames")
async def upload_frames(files: List[UploadFile] = File(...)):
    session_id = str(uuid.uuid4())
    session_embeddings[session_id] = []
    for file in files:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        reg_img = await student_controller.get_embedding(img, session_id)
    return {"status": "success", "session_id": session_id}

@router.post("/check", response_description="check_face_alignment")
async def check_face_alignment(image: UploadFile = File(...), alignment_name: str = Form(...)):
    # Read and process the uploaded image
    contents = await image.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Detect face alignment
    faces = faceApp.get(img)
    print("faces====>", len(faces))
    if len(faces) == 1:
        # Assuming only one face is present in the image
        face = faces[0]
        bbox = face.bbox.astype(int)
        center_x = (bbox[0] + bbox[2]) // 2

        # Determine face alignment
        if alignment_name.lower() == "center":
            alignment_check = center_x >= img.shape[1] // 3 and center_x <= img.shape[1] * 2 // 3
        elif alignment_name.lower() == "left":
            alignment_check = center_x < img.shape[1] // 3
        elif alignment_name.lower() == "right":
            alignment_check = center_x > img.shape[1] * 2 // 3
        else:
            return {"error": "Invalid alignment name"}
        if alignment_check == True:
            return {"result": True}
        else:
            return {"result": False}
    else:
        return {"error": "No face detected or multiple faces detected"}

