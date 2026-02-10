import os

import ecflow


def create_tutorial_suite():
    """
    Create a comprehensive example suite for ecFlow tutorial.
    """
    defs = ecflow.Defs()

    # Define a suite named 'tutorial'
    suite = defs.add_suite("tutorial")

    # Set ECF_HOME (where logs and scripts will be stored)
    suite.add_variable("ECF_HOME", os.path.join(os.getcwd(), "ecflow_home"))
    suite.add_variable("ECF_INCLUDE", os.path.join(os.getcwd(), "ecflow_home"))

    # Family 1: Data Acquisition
    ingest = suite.add_family("ingest")
    get_data = ingest.add_task("get_data")
    get_data.add_variable("SOURCE", "ftp://data.example.com")

    process_data = ingest.add_task("process_data")
    process_data.add_trigger("get_data == complete")

    # Family 2: Analysis (runs after ingest)
    analysis = suite.add_family("analysis")
    analysis.add_trigger("ingest == complete")

    for i in range(1, 4):
        task = analysis.add_task(f"model_{i}")
        task.add_variable("ITERATION", str(i))
        # Add a dummy trigger for the second and third task to run sequentially
        if i > 1:
            task.add_trigger(f"model_{i-1} == complete")

    # Family 3: Reporting
    report = suite.add_family("report")
    report.add_trigger("analysis == complete")

    report.add_task("generate_pdf")
    archive = report.add_task("archive_results")
    archive.add_trigger("generate_pdf == complete")

    return defs


if __name__ == "__main__":
    suite_defs = create_tutorial_suite()
    print(suite_defs)

    # Save the definition to a file
    suite_defs.save_as_defs("tutorial.def")
    print("Created tutorial.def")
