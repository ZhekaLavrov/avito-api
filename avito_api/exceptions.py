import json


class Error(Exception):
    def __init__(self, *args):
        if len(args) >= 2:
            self.error = args[0]
            self.error_description = args[1]
        elif len(args) >= 1:
            self.error = args[0]
            self.error_description = ''
        else:
            self.error = ''
            self.error_description = ''

    def __to_dict__(self):
        return {
            "error": self.error,
            "error_description": self.error_description
        }

    def __str__(self):
        return json.dumps(self.__to_dict__(), ensure_ascii=False)

    def __repr__(self):
        return self.__str__()