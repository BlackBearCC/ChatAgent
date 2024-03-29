class UserMessage:
    def __init__(self, role, message):
        self.role = role
        self.message = message

    @classmethod
    def from_dict(cls, data):
        return cls(role=data.get("role"), message=data.get("message"))

    def to_dict(self):
        return {"type": "UserMessage", "role": self.role, "message": self.message}

class AiMessage:
    def __init__(self, role, message):
        self.role = role
        self.message = message

    @classmethod
    def from_dict(cls, data):
        return cls(role=data.get("role"), message=data.get("message"))

    def to_dict(self):
        return {"type": "AiMessage", "role": self.role, "message": self.message}

class SystemMessage:
    def __init__(self, role, message,type="SystemMessage" ):
        self.role = role
        self.message = message
        self.type = type

    @classmethod
    def from_dict(cls, data):
        return cls(role=data.get("role"), message=data.get("message"))

    def to_dict(self):
        return {"type": self.type, "role": self.role, "message": self.message}

