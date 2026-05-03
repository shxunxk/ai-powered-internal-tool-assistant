import inspect

class Tool:

    def __init__(self, func):

        self.name = func.__name__

        self.description = inspect.getdoc(func)

        self.schema = self._build_schema(func)

        self.func = func

    def _build_schema(self, func):

        sig = inspect.signature(func)

        schema = {}

        for name, param in sig.parameters.items():

            schema[name] = {
                "type": str(param.annotation),
                "required": param.default == inspect._empty
            }

        return schema
