from .create_inline_buttons import create_inline

def set_bunker_value(variants):

    bunker_value = {f"изгнать {elem}": {"number": 0, "callback": f"изгнать {elem}"} for elem in variants}

    return bunker_value

    # return create_inline(bunker_value, type_placement="row")
    