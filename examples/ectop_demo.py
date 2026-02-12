"""
Comprehensive demo suite for ectop.
This script creates an ecFlow suite, generates all necessary script files,
and can optionally load it into an ecFlow server.

Usage:
    python ectop_demo.py --port 3141 --home ./ecflow_home --load
"""

# If you modify features, API, or usage, you MUST update the documentation immediately.
from __future__ import annotations

import argparse
import os

import ecflow


def create_demo_suite(home: str) -> ecflow.Defs:
    """
    Create a comprehensive ecFlow suite definition.

    Parameters
    ----------
    home : str
        The ECF_HOME directory where scripts and logs will be stored.

    Returns
    -------
    ecflow.Defs
        The suite definition.

    Notes
    -----
    This suite includes various features such as limits, triggers, and multiple families
    to demonstrate the capabilities of ecFlow and ectop.
    """
    defs = ecflow.Defs()
    suite = defs.add_suite("ectop_demo")

    # Global suite variables
    suite.add_variable("ECF_HOME", home)
    suite.add_variable("ECF_INCLUDE", home)
    # Use a simple job command that runs bash on the generated job file
    suite.add_variable("ECF_JOB_CMD", "%ECF_JOB% > %ECF_JOBOUT% 2>&1")
    suite.add_variable("PROJECT", "ectop_testing")
    suite.add_variable("USER_NAME", os.environ.get("USER", "tester"))

    # Add a limit to test queuing
    suite.add_limit("max_jobs", 2)

    # --- Setup Family ---
    setup = suite.add_family("setup")
    init = setup.add_task("init")
    init.add_variable("SLEEP_TIME", "2")

    config = setup.add_task("config")
    config.add_trigger("init == complete")
    config.add_variable("SLEEP_TIME", "1")

    # --- Operational Family ---
    oper = suite.add_family("operational")
    oper.add_trigger("setup == complete")

    # Tasks using limits
    batch = oper.add_family("batch")
    for i in range(1, 6):
        t = batch.add_task(f"process_{i}")
        t.add_inlimit("max_jobs")
        t.add_variable("SLEEP_TIME", str(5 + i))
        t.add_variable("ITERATION", str(i))

    # Task that fails to test 'Why?' and 'Aborted' status
    errors = oper.add_family("errors")
    fail_task = errors.add_task("critical_failure")
    fail_task.add_variable("SHOULD_FAIL", "1")

    # Task with complex trigger
    dependency = errors.add_task("dependency_task")
    dependency.add_trigger("critical_failure == complete")

    # --- Maintenance Family (Suspended) ---
    maint = suite.add_family("maintenance")
    maint.add_defstatus(ecflow.DState.suspended)
    cleanup = maint.add_task("cleanup")
    cleanup.add_variable("SLEEP_TIME", "5")

    # --- Long Running Family ---
    long_run = suite.add_family("monitoring")
    monitor = long_run.add_task("heartbeat")
    monitor.add_variable("SLEEP_TIME", "60")

    return defs


def get_all_tasks(node: ecflow.NodeContainer) -> list[ecflow.Task]:
    """
    Recursively get all tasks from a node.

    Parameters
    ----------
    node : ecflow.NodeContainer
        The node container (Suite or Family) to search for tasks.

    Returns
    -------
    list[ecflow.Task]
        A list of all tasks found under the node.

    Raises
    ------
    AttributeError
        If the node does not have a 'nodes' attribute when expected.

    Notes
    -----
    This function performs a depth-first search to find all task nodes.
    """
    tasks = []
    if isinstance(node, ecflow.Task):
        tasks.append(node)
    elif hasattr(node, "nodes"):
        for child in node.nodes:
            tasks.extend(get_all_tasks(child))
    return tasks


def generate_scripts(defs: ecflow.Defs, home: str) -> None:
    """
    Generate .ecf script files for all tasks in the definition.

    Parameters
    ----------
    defs : ecflow.Defs
        The ecFlow definitions containing the suites and tasks.
    home : str
        The ECF_HOME directory where scripts will be saved.

    Returns
    -------
    None

    Raises
    ------
    OSError
        If the directory or files cannot be created.

    Notes
    -----
    This function creates the directory structure and .ecf files required for ecFlow tasks.
    Each script is made executable.
    """
    template = """#!/bin/bash
export ECF_PORT=%ECF_PORT%
export ECF_HOST=%ECF_HOST%
export ECF_NAME=%ECF_NAME%
export ECF_PASS=%ECF_PASS%
export ECF_TRYNO=%ECF_TRYNO%
export ECF_RID=$$

# Notify ecFlow that the task has started
ecflow_client --init=$$

# Trap errors to notify ecFlow
trap 'ecflow_client --abort; exit 1' ERR

echo "------------------------------------------------"
echo "Task: %ECF_NAME%"
echo "Time: $(date)"
echo "Host: $(hostname)"
echo "User: %USER_NAME%"
echo "Project: %PROJECT%"
echo "------------------------------------------------"

SHOULD_FAIL=%SHOULD_FAIL:0%
if [ "$SHOULD_FAIL" -eq 1 ]; then
    echo "ERROR: This task is configured to fail for demonstration purposes."
    sleep 2
    exit 1
fi

SLEEP_TIME=%SLEEP_TIME:5%
echo "Action: Sleeping for $SLEEP_TIME seconds..."
sleep $SLEEP_TIME

echo "------------------------------------------------"
echo "Task %ECF_NAME% completed successfully at $(date)"
echo "------------------------------------------------"

# Notify ecFlow that the task has completed
ecflow_client --complete
"""

    # Iterate over all suites and tasks to create script files
    for suite in defs.suites:
        for task in get_all_tasks(suite):
            # Get the path relative to ECF_HOME
            # ecflow paths start with /, so we remove it
            rel_path = task.get_abs_node_path()[1:]
            script_path = os.path.join(home, rel_path + ".ecf")

            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(script_path), exist_ok=True)

            with open(script_path, "w") as f:
                f.write(template)

            # Make the script executable
            os.chmod(script_path, 0o755)

    print(f"Generated scripts in {home}")


def main() -> None:
    """
    Main entry point for the demo setup script.

    Raises
    ------
    RuntimeError
        If connection to ecFlow server fails when --load is specified.

    Notes
    -----
    This script parses command-line arguments, creates the suite definition,
    generates scripts, and optionally loads the suite into an ecFlow server.
    """
    parser = argparse.ArgumentParser(description="Setup ectop demo suite")
    parser.add_argument("--port", type=int, default=3141, help="ecFlow server port")
    parser.add_argument("--host", type=str, default="localhost", help="ecFlow server host")
    parser.add_argument("--home", type=str, default="./ectop_demo_home", help="ECF_HOME directory")
    parser.add_argument("--load", action="store_true", help="Load and play the suite")

    args = parser.parse_args()

    home = os.path.abspath(args.home)
    if not os.path.exists(home):
        os.makedirs(home)

    defs = create_demo_suite(home)
    generate_scripts(defs, home)

    print("\nSuite Definition created.")
    print(f"ECF_HOME is set to: {home}")

    if args.load:
        client = ecflow.Client(args.host, args.port)
        try:
            print(f"Connecting to ecFlow server at {args.host}:{args.port}...")
            client.ping()

            print("Loading suite...")
            client.load(defs)

            print("Beginning suite playback...")
            client.begin_suite("ectop_demo")

            print("\nSuccess! The demo suite 'ectop_demo' is now running.")
            print("You can now start ectop to monitor it:")
            print(f"  ectop --host {args.host} --port {args.port}")

        except RuntimeError as e:
            print(f"\nError: Could not connect to or load suite into server: {e}")
            print("Make sure your ecFlow server is running.")
            print(f"To start a local server: ecflow_server --port {args.port}")


if __name__ == "__main__":
    main()
