# .. note:: warning: "If you modify features, API, or usage, you MUST update the documentation immediately."
import os
import shutil
import subprocess
import sys
import time

import ecflow


def run_smoke_test():
    ecf_port = 3145
    ecf_home = os.path.join(os.path.expanduser("~"), "ecflow_smoke_test_final")
    if os.path.exists(ecf_home):
        shutil.rmtree(ecf_home)
    os.makedirs(ecf_home, exist_ok=True)

    print(f"Starting ecFlow server on port {ecf_port}...")

    server_process = subprocess.Popen(
        ["ecflow_server"],
        env={**os.environ, "ECF_PORT": str(ecf_port), "ECF_HOME": ecf_home},
        stdout=open("server_stdout_final.log", "w"),
        stderr=open("server_stderr_final.log", "w"),
    )

    client = ecflow.Client("localhost", ecf_port)
    try:
        # Give it a moment to start
        for _i in range(10):
            time.sleep(1)
            try:
                client.ping()
                print("Ping successful!")
                break
            except Exception:
                continue
        else:
            print("Failed to ping server after 10 seconds")
            sys.exit(1)

        print("Loading a test suite...")
        defs = ecflow.Defs()
        suite = defs.add_suite("smoke_test_suite")
        suite.add_task("smoke_task")
        client.load(defs)
        print("Suite loaded successfully!")

        print("Retrieving suite definitions...")
        client.sync_local()
        retrieved_defs = client.get_defs()
        if retrieved_defs.find_suite("smoke_test_suite"):
            print("Verified: Suite exists on server.")
        else:
            print("Error: Suite NOT found on server.")
            sys.exit(1)

    finally:
        print("Shutting down server...")
        try:
            client.halt_server()
            client.terminate_server()
        except Exception:
            server_process.terminate()
        server_process.wait(timeout=5)
        print("Server stopped.")
        if os.path.exists(ecf_home):
            shutil.rmtree(ecf_home)


if __name__ == "__main__":
    run_smoke_test()
