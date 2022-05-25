def create_id_generator(prefix=""):
    """Generic id generator"""
    count = 1
    while True:
        yield f"{prefix}{count}"
        count += 1


def is_equal(a, b):
    """Return True if both value can be conciderated as the same"""
    # might need some deeper investigation
    return a == b


def is_valid_value(v):
    """Return true if a value can be stored into a property of a proxy"""
    if v is None:
        return False
    if isinstance(v, (str, bool, int, float)):
        return True
    if isinstance(v, (list, tuple)):
        for item in v:
            if not is_valid_value(item):
                return False
        return True
    return False
