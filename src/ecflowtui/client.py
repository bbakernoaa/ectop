import ecflow

# --- State Icons ---
STATE_MAP = {
    "unknown": "⚪",
    "complete": "🟢",
    "queued": "🔵",
    "aborted": "🔴",
    "submitted": "🟡",
    "active": "🔥",
    "suspended": "🟠",
}

class EcflowClient:
    def __init__(self, host="localhost", port=3141):
        self.host = host
        self.port = port
        self.client = ecflow.Client(host, port)

    def ping(self):
        self.client.ping()

    def sync_local(self):
        self.client.sync_local()

    def get_defs(self):
        return self.client.get_defs()

    def file(self, path, file_type):
        return self.client.get_file(path, file_type)

    def suspend(self, path):
        self.client.suspend(path)

    def resume(self, path):
        self.client.resume(path)

    def kill(self, path):
        self.client.kill(path)

    def force_complete(self, path):
        self.client.force_state(path, ecflow.State.complete)

    def alter(self, path, alter_type, name, value=""):
        self.client.alter(path, alter_type, name, value)

    def requeue(self, path):
        self.client.requeue(path)
