def class_helper(new_class) -> dict:
    return {
        "id": str(new_class["_id"]),
        "class_name": new_class["class_name"],
        "subject": new_class["subject"],
        "class_hour": new_class["class_hour"],
        "class_code": new_class["class_code"],
        "teacher_lat": new_class["teacher_lat"],
        "teacher_long": new_class["teacher_long"],
        "teacher_id": str(new_class["teacher_id"]),
        "teacher_fullname": new_class["teacher_fullname"],
        "time": new_class["time"]
    }