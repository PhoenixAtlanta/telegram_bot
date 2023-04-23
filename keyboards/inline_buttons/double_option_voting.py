from ..inline_buttons.create_inline_buttons import create_inline

double_inline_value = {"да": {"number": 0, "callback": "да"}, "нет": {"number": 0, "callback": "нет"}}
    

double_inline_keyboard = create_inline(double_inline_value, type_placement="add")



