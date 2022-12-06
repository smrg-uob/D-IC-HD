import re


def validate_float(val):
    if len(val) == 0 or val == '-':
        return True
    try:
        float(val)
    except:
        return False
    return True


def validate_float_positive(val):
    if len(val) == 0:
        return True
    try:
        nr = float(val)
    except:
        return False
    return nr > 0


def validate_int(val):
    if len(val) == 0 or val == '-':
        return True
    try:
        int(val)
    except:
        return False
    return True


def validate_int_positive(val):
    if len(val) == 0 or val == '-':
        return True
    try:
        nr = int(val)
    except:
        return False
    return nr > 0


def validate_exposure(val):
    if len(val) == 0:
        return True
    return re.match('^[0-9]*$', val) is not None
