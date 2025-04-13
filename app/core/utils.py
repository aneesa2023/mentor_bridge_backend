from bson import ObjectId

def serialize_mongo_doc(doc):
    if not doc: return None
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc