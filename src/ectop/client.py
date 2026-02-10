"""
ecFlow Client Wrapper for ectop.

.. note::
    If you modify features, API, or usage, you MUST update the documentation immediately.
"""

import ecflow

# --- State Icons ---
STATE_MAP: dict[str, str] = {
    "unknown": "⚪",
    "complete": "🟢",
    "queued": "🔵",
    "aborted": "🔴",
    "submitted": "🟡",
    "active": "🔥",
    "suspended": "🟠",
}


class EcflowClient:
    """
    A wrapper around the ecflow.Client to provide a cleaner API and error handling.

    .. note::
        If you modify features, API, or usage, you MUST update the documentation immediately.

    Attributes
    ----------
    host : str
        The hostname of the ecFlow server.
    port : int
        The port number of the ecFlow server.
    client : ecflow.Client
        The underlying ecFlow client instance.
    """

    def __init__(self, host: str = "localhost", port: int = 3141) -> None:
        """
        Initialize the EcflowClient.

        Parameters
        ----------
        host : str, optional
            The hostname of the ecFlow server, by default "localhost".
        port : int, optional
            The port number of the ecFlow server, by default 3141.
        """
        self.host: str = host
        self.port: int = port
        self.client: ecflow.Client = ecflow.Client(host, port)

    def ping(self) -> None:
        """
        Ping the ecFlow server to check connectivity.

        Raises
        ------
        RuntimeError
            If the server is unreachable or the ping fails.
        """
        try:
            self.client.ping()
        except RuntimeError as e:
            raise RuntimeError(f"Failed to ping ecFlow server at {self.host}:{self.port}: {e}") from e

    def sync_local(self) -> None:
        """
        Synchronize the local definition with the server.

        Raises
        ------
        RuntimeError
            If synchronization fails.
        """
        try:
            self.client.sync_local()
        except RuntimeError as e:
            raise RuntimeError(f"Failed to sync with ecFlow server: {e}") from e

    def get_defs(self) -> ecflow.Defs | None:
        """
        Retrieve the current definitions from the client.

        Returns
        -------
        ecflow.Defs | None
            The ecFlow definitions, or None if not available.

        Raises
        ------
        RuntimeError
            If the definitions cannot be retrieved.
        """
        try:
            return self.client.get_defs()
        except RuntimeError as e:
            raise RuntimeError(f"Failed to get definitions from client: {e}") from e

    def file(self, path: str, file_type: str) -> str:
        """
        Retrieve a file (log, script, job) for a specific node.

        Parameters
        ----------
        path : str
            The absolute path to the node.
        file_type : str
            The type of file to retrieve ('jobout', 'script', 'job').

        Returns
        -------
        str
            The content of the requested file.

        Raises
        ------
        RuntimeError
            If the file cannot be retrieved.
        """
        try:
            return self.client.file(path, file_type)
        except RuntimeError as e:
            raise RuntimeError(f"Failed to retrieve {file_type} for {path}: {e}") from e

    def suspend(self, path: str) -> None:
        """
        Suspend a node.

        Parameters
        ----------
        path : str
            The absolute path to the node.

        Raises
        ------
        RuntimeError
            If the node cannot be suspended.
        """
        try:
            self.client.suspend(path)
        except RuntimeError as e:
            raise RuntimeError(f"Failed to suspend {path}: {e}") from e

    def resume(self, path: str) -> None:
        """
        Resume a suspended node.

        Parameters
        ----------
        path : str
            The absolute path to the node.

        Raises
        ------
        RuntimeError
            If the node cannot be resumed.
        """
        try:
            self.client.resume(path)
        except RuntimeError as e:
            raise RuntimeError(f"Failed to resume {path}: {e}") from e

    def kill(self, path: str) -> None:
        """
        Kill a running task.

        Parameters
        ----------
        path : str
            The absolute path to the node.

        Raises
        ------
        RuntimeError
            If the node cannot be killed.
        """
        try:
            self.client.kill(path)
        except RuntimeError as e:
            raise RuntimeError(f"Failed to kill {path}: {e}") from e

    def force_complete(self, path: str) -> None:
        """
        Force a node to the complete state.

        Parameters
        ----------
        path : str
            The absolute path to the node.

        Raises
        ------
        RuntimeError
            If the node state cannot be forced.
        """
        try:
            self.client.force_complete(path)
        except RuntimeError as e:
            raise RuntimeError(f"Failed to force complete {path}: {e}") from e

    def alter(self, path: str, alter_type: str, name: str, value: str = "") -> None:
        """
        Alter a node attribute or variable.

        Parameters
        ----------
        path : str
            The absolute path to the node.
        alter_type : str
            The type of alteration (e.g., 'change', 'add', 'delete').
        name : str
            The name of the attribute or variable.
        value : str, optional
            The new value, by default "".

        Raises
        ------
        RuntimeError
            If the alteration fails.
        """
        try:
            self.client.alter(path, alter_type, name, value)
        except RuntimeError as e:
            raise RuntimeError(f"Failed to alter {path} ({alter_type} {name}={value}): {e}") from e

    def requeue(self, path: str) -> None:
        """
        Requeue a node.

        Parameters
        ----------
        path : str
            The absolute path to the node.

        Raises
        ------
        RuntimeError
            If the node cannot be requeued.
        """
        try:
            self.client.requeue(path)
        except RuntimeError as e:
            raise RuntimeError(f"Failed to requeue {path}: {e}") from e
