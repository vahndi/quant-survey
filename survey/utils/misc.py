def listify(argument) -> list:
    """
    Turn `argument` into a list, if it is not already one.
    """
    if argument is None:
        return []
    if type(argument) is tuple:
        argument = list(argument)
    elif not type(argument) is list:
        argument = [argument]
    return argument
