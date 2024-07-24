def attendance_helper(new_attendance) -> dict:
    return {
        "id": str(new_attendance["_id"]),
        "student_id": str(new_attendance["student_id"]),
        "student_code": new_attendance["student_code"],
        "phone": new_attendance["phone"],
        "fullname": new_attendance["fullname"],
        "class_name": new_attendance["class_name"],
        "time": new_attendance["time"]
    }