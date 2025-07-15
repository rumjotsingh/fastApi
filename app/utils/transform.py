def mongo_obj_to_dict(obj):
    if not obj:
        return obj
    obj = dict(obj)
    if "_id" in obj:
        obj["id"] = str(obj["_id"])
        obj.pop("_id")
    return obj 