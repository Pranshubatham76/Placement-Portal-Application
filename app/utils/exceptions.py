
class AuthException(Exception):
    
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class StudentException(Exception):
    
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)