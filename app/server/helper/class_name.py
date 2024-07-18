def class_name_helper(class_name) -> dict:
    return {
        "id": str(class_name["_id"]),
        "class_name": class_name["class_name"],
    }