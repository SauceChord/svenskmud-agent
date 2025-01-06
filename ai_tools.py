import inspect
import re

class AITools:
    # Map Python types to JSON Schema-compatible types
    TYPE_MAPPING = {
        int: "integer",
        float: "number",
        str: "string",
        bool: "boolean",
        list: "array",
        dict: "object"
    }

    PARAM_DOCSTRING_PATTERN = re.compile(r':param\s+(?P<param_name>\w+):\s+(?P<description>.*)')

    def __init__(self):
        self.metadata = []
        self.funcs = {}
        pass

    def add(self, func):
        metadata = self.generate_metadata(func)
        self.metadata.append(metadata)
        self.funcs[metadata["function"]["name"]] = func

    def call(self, func_name: str, func_args):
        func = self.funcs[func_name]
        
        # Check if the function requires approval
        if hasattr(func, 'requires_approval'):
            args_str = ', '.join(f'{key}={value}' for key, value in func_args.items())
            while True:
                choice = input(f"Function '{func.__name__}({args_str})' requires approval to execute (Y/n): ").lower()
                if choice == "y":
                    print(f"calling {func_name}")
                    return func(**func_args)
                if choice == "n":
                    return "ERROR: Function call denied"

        # print(f"calling {func_name}")
        return func(**func_args)

    def generate_metadata(self, func):
        """Generate metadata for OpenAI's functions parameter and docstring from a Python function."""
        sig = inspect.signature(func)
        parameters = {}
        required = []

        # Fetching the function docstring
        docstring = inspect.getdoc(func) or ""
        param_descriptions = {
            match.group('param_name'): match.group('description') for match in AITools.PARAM_DOCSTRING_PATTERN.finditer(docstring)
        }
        
        for name, param in sig.parameters.items():
            # Fetch description from parsed docstring, or default
            description = param_descriptions.get(name, f"The {name} parameter.")

            if param.annotation != inspect.Parameter.empty:
                param_type = AITools.TYPE_MAPPING.get(param.annotation, "string") # Default to string if type is not mapped
                parameters[name] = {
                    "type": param_type,
                    "description": description
                }
                if param.default == inspect.Parameter.empty:  # Required if no default value
                    required.append(name)
            else:
                parameters[name] = {
                    "type": "string",
                    "description": description
                }

        return {
            "type": "function",
            "function": {
                "name": func.__name__,
                "description": docstring,
                "parameters": {
                    "type": "object",
                    "properties": parameters,
                    "required": required
                }
            }
        }

def requires_approval(func):
    """Decorator to tag a function that requires user approval to execute."""
    func.requires_approval = True  # Add an attribute to the function
    return func
      