"""Utilities for handling patch data
"""
def path_to_dot(path):
    return path.replace('/', '.').lstrip('.')

def patch_to_mongo(patch):
    op = patch["op"]
    dot_path = path_to_dot(patch["path"])
    value = patch["value"]
    if op == "add":
        # TODO! This is not complete - it does not resolve nested updates
        parts = dot_path.split('.')
        key = parts[0]
        try:
            index = int(parts[1])
            return {"$push": {key: {"$each": [value], "$position": index}}}
        except ValueError:
            return {"$push": {dot_path: value}}
    elif op == "remove":
        return {"$unset": {dot_path: value}}

    elif op == "replace":
        return {"$set": {dot_path: value}}
