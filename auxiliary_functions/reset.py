def reset_params(value):
    for key_name in value.__dict__:

        if type(value.__dict__[key_name]) is int:
            value.__dict__[key_name] = None  

        elif type(value.__dict__[key_name]) is str:
            value.__dict__[key_name] = ""  

        elif type(value.__dict__[key_name]) is list:
            value.__dict__[key_name] = []

    return value



        
