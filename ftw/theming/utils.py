import inspect


def find_object_in_stack(name, klass):
    frame = inspect.currentframe()
    while not isinstance(frame.f_locals.get(name, None), klass):
        frame = frame.f_back
    return frame.f_locals[name]
