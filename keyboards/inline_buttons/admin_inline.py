from .create_inline_buttons import create_inline

def set_admin_value(variants):

    admin_value = {f"админ {elem}": {"number": 0, "callback": f"админ {elem}"} for elem in variants}

    return admin_value