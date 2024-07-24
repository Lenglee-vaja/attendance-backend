from fastapi import APIRouter, Form, UploadFile, File, Body, Depends, Query
from fastapi.encoders import jsonable_encoder
from server.controller.student import student_controller
from server.controller.class_room import class_controller
from server.controller.class_name import class_name_controller
from server.controller.attendance import attendance_controller
from server.config.index import faceApp
import uuid
from typing import List
from typing import Optional


import numpy as np
import cv2
from server.helper.index import (
    ErrorResponseModel,
    ResponseRegister,
    ResponseLogin,
    ResponseModel,
    ResponseModels,
    verify_jwt_token,
    verify_jwt_token_and_role
)
from server.models.student import (
    StudentSchema,
    StudentLoginSchema,
    UpdateStudentModel,
    TeacherSchema
)
from server.models.class_room import (
    ClassSchema,
    CheckLocationSchema
)
from server.models.class_name import ClassNameSchema
from server.controller.student import session_embeddings
router = APIRouter()

#========================================detect=============================================

@router.post("/detect", response_description="detect")
async def detect_frames(files: List[UploadFile] = File(...), class_code: str = Query(...)):
    print("class_code ============>", class_code)
    for file in files:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        data = await student_controller.face_prediction(img, class_code)
    return ResponseModel(data, "SUCCESSFULLY")


#========================================auth================================================


@router.post("/student/register", response_description="route for student register")
async def student_register(student: StudentSchema = Body(...)):
    student = jsonable_encoder(student)
    new_student, token = await student_controller.student_register(student)
    return ResponseRegister(new_student,token, "SUCCESSFULLY")
@router.post("/teacher/register", response_description="route for teacher register")
async def teacher_register(teacher: TeacherSchema = Body(...)):
    teacher = jsonable_encoder(teacher)
    new_teacher, token = await student_controller.teacher_register(teacher)
    return ResponseRegister(new_teacher, token, "SUCCESSFULLY")

@router.post("/login", response_description="route for login")
async def login_data(student: StudentLoginSchema = Body(...)):
    student = jsonable_encoder(student)
    token, user = await student_controller.user_login(student)
    return ResponseLogin(token, user, "SUCCESSFULLY")

@router.post("/upload_frames", response_description="upload_frames")
async def upload_frames(files: List[UploadFile] = File(...)):
    session_id = str(uuid.uuid4())
    session_embeddings[session_id] = []
    for file in files:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        reg_img = await student_controller.get_embedding(img, session_id)
    return ResponseModel(session_id, "SUCCESSFULLY")


#===========================================user==================================================

@router.get("/students", response_description="retrieve all students")
async def retrieve_students(
    search: Optional[str] = Query(None, description="Search query to filter classes"),
    payload: dict = Depends(verify_jwt_token_and_role)
):
    classes = await student_controller.retrieve_students(search)
    return ResponseModels(classes, "SUCCESSFULLY")

@router.get("/student/count", response_description="count all students")
async def retrieve_students(
    search: Optional[str] = Query(None, description="Search count students"),
    payload: dict = Depends(verify_jwt_token_and_role)
):
    classes = await student_controller.count_students(search)
    return ResponseModels(classes, "SUCCESSFULLY")




#===========================================class_room==================================================


@router.post("/add_class", response_description="add class")
async def add_class_room(class_room:  ClassSchema= Body(...), payload: dict = Depends(verify_jwt_token_and_role)):
    print(class_room)
    class_room = jsonable_encoder(class_room)
    new_class = await class_controller.add_class(class_room, payload)
    return ResponseModel(new_class, "SUCCESSFULLY")

@router.get("/classes", response_description="retrieve all classes")
async def retrieve_classes(
    search: Optional[str] = Query(None, description="Search query to filter classes"),
    payload: dict = Depends(verify_jwt_token_and_role)
):
    classes = await class_controller.retrieve_classes(search)
    return ResponseModels(classes, "SUCCESSFULLY")


@router.get("/class/{class_code}", response_description="retrieve class")
async def retrieve_class(class_code):
    class_room = await class_controller.retrieve_class(class_code)
    if class_room:
        return ResponseModel(class_room, "SUCCESSFULLY")
    return ErrorResponseModel("Error", 404, "STUDENT_DOES_NOT_EXIST")

@router.post("/check_location", response_description="check location")
async def check_location(check_location:  CheckLocationSchema= Body(...)):
    check_locations = jsonable_encoder(check_location)
    location = await class_controller.check_location(check_locations)
    return ResponseModels(location, "SUCCESSFULLY")


#===========================================class_name================================================

@router.post("/add_class_name", response_description="add class name")
async def add_class_name(class_room:  ClassNameSchema= Body(...)):
    class_room = jsonable_encoder(class_room)
    new_class = await class_name_controller.add_class_name(class_room)
    return ResponseModel(new_class, "SUCCESSFULLY")

@router.get("/class_names", response_description="retrieve all class_name")
async def retrieve_class_names(
    search: Optional[str] = Query(None, description="Search query to filter class name")
):
    classes = await class_name_controller.retrieve_class_names(search)
    return ResponseModels(classes, "SUCCESSFULLY")


#==========================================Attendance================================================

@router.get("/attendances", response_description="retrieve all students")
async def retrieve_attendances(
    search: Optional[str] = Query(None, description="Search query to filter classes"),
    payload: dict = Depends(verify_jwt_token_and_role)
):
    classes = await attendance_controller.retrieve_attendances(search)
    return ResponseModels(classes, "SUCCESSFULLY")

@router.get("/attendance/count", response_description="count all attendance")
async def count_attendances(
    search: Optional[str] = Query(None, description="Search count attendance"),
    payload: dict = Depends(verify_jwt_token_and_role)
):
    classes = await attendance_controller.count_attendances(search)
    return ResponseModels(classes, "SUCCESSFULLY")
