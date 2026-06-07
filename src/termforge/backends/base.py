

class BackendError(Exception):
    pass

class BackendBase:
    name = "base"
    label = "Base Backend"
    description = "Abstract backend"

    def __init__(self, app):
        self.app = app

    def is_available(self):
        return True

    def select_target(self):
        raise NotImplementedError

    def send_text(self, text: str, record_history: bool = True):
        raise NotImplementedError

    def run_detached(self, command: str, record_history: bool = True):
        raise NotImplementedError
