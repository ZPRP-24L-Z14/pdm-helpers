from typing import List, Dict
import os
import shutil
import subprocess
import time
from tqdm import tqdm
from tabulate import tabulate

work_dir = "./testing_project"  # TODO: use a temp dir

packages_list = [
    "numpy",
    "pandas",
    "requests",
    "matplotlib",
    "scikit-learn",
    "flask",
    "django",
    "sqlalchemy",
    "pillow",
    "beautifulsoup4",
    "pytz",
    "click",
    "pytest",
    "pyyaml",
    "tqdm",
    "seaborn",
    "keras",
    "scipy",
]

try:
    with open("modules.txt", "r") as file:
        for row in file.readlines():
            packages_list.append(row)
except:
    print("file with modules not found")

# TODO: remove relative paths
testing_commands = {
    "pdm list": ["pdm", "list"],
    "findpython": ["pdm", "run", "../src/pdm_helpers/findpython.py"],
    "regular python": ["pdm", "run", "python3", "../src/pdm_helpers/speed_test.py"],
    "python without site modules": [
        "pdm",
        "run",
        "python3",
        "-S",
        "../src/pdm_helpers/speed_test.py",
    ],
}


def execute_command(command: List[str], cwd="", mute_output=False):
    if mute_output:
        subprocess.run(
            command, cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
        )
    else:
        subprocess.run(command, cwd=cwd)


def run_command(command: List[str], cwd="", repeats=1, mute_output=False):
    start_time = time.perf_counter()
    if repeats == 1:
        execute_command(command, cwd=cwd, mute_output=mute_output)
    else:
        for i in tqdm(range(repeats)):
            execute_command(command, cwd=cwd, mute_output=mute_output)

    end_time = time.perf_counter()

    return end_time - start_time


def initialize_project():
    if os.path.isdir(work_dir):
        shutil.rmtree(work_dir)

    os.makedirs(work_dir)

    run_command(["pdm", "init", "-n"], cwd=work_dir)


def install_packages():
    run_command(["pdm", "add"] + packages_list, cwd=work_dir)


def report_results(
    clean_project_times: Dict[str, str], dirty_project_times: Dict[str, str]
):
    table = []
    for test_name in clean_project_times.keys():
        clean_time = clean_project_times[test_name]
        dirty_time = dirty_project_times[test_name]

        percent_difference = 100 * (dirty_time - clean_time) / clean_time

        table.append(
            [
                test_name,
                f"{clean_time:.5f}",
                f"{dirty_time:.5f}",
                f"{percent_difference:.2f}%",
            ]
        )

    print(
        tabulate(
            table, headers=["Test", "Clean project", "Dirty project", "Difference"]
        )
    )


def test_performance_difference(test_suite, repeats):
    initialize_project()

    clean_project_times = {}
    dirty_project_times = {}

    print("Running tests on clean project...")
    for test_name, test_command in test_suite.items():
        print(f"Test {test_name}:")
        clean_project_times[test_name] = (
            run_command(test_command, repeats=repeats, cwd=work_dir, mute_output=True)
            / repeats
        )

    install_packages()

    print("Running tests on dirty project...")
    for test_name, test_command in test_suite.items():
        print(f"Test {test_name}:")
        dirty_project_times[test_name] = (
            run_command(test_command, repeats=repeats, cwd=work_dir, mute_output=True)
            / repeats
        )

    report_results(clean_project_times, dirty_project_times)


def main():
    test_performance_difference(testing_commands, repeats=5)
    # TODO: add argparse for testing options


if __name__ == "__main__":
    main()
