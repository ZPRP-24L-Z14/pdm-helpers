from typing import List, Dict
import subprocess
import time
import tempfile
import argparse
from pathlib import Path
from tqdm import tqdm
from tabulate import tabulate

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
    "boto3",
    "botocore",
    "urllib3",
    "requests",
    "wheel",
    "certifi",
    "idna",
    "typing-extensions",
    "charset-normalizer",
    "pip",
    "setuptools",
    "python-dateutil",
    "s3transfer",
    "packaging",
    "aiobotocore",
    "pyyaml",
    "six",
    "s3fs",
    "fsspec",
    "numpy",
    "cryptography",
    "grpcio-status",
    "google-api-core",
    "cffi",
    "pycparser",
    "pypular",
    "pandas",
    "importlib-metadata",
    "pyasn1",
    "rsa",
    "zipp",
    "attrs",
    "click",
    "pydantic",
    "protobuf",
    "jmespath",
    "platformdirs",
    "pytz",
    "jinja2",
    "colorama",
    "markupsafe",
    "pyjwt",
    "awscli",
    "tomli",
    "wrapt",
    "google-auth",
    "googleapis-common-protos",
    "filelock",
    "cachetools",
    "requests-oauthlib",
    "oauthlib",
    "pluggy",
    "virtualenv",
    "pyarrow",
    "docutils",
    "jsonschema",
    "pyasn1-modules",
    "pytest",
    "exceptiongroup",
    "aiohttp",
    "pyparsing",
    "sqlalchemy",
    "scipy",
    "isodate",
    "multidict",
    "psutil",
    "pyopenssl",
    "yarl",
    "iniconfig",
    "decorator",
    "soupsieve",
    "pygments",
    "tzdata",
    "async-timeout",
    "beautifulsoup4",
    "frozenlist",
    "aiosignal",
    "tqdm",
    "grpcio",
    "pillow",
    "requests-toolbelt",
    "greenlet",
    "pydantic-core",
    "openpyxl",
    "et-xmlfile",
    "lxml",
    "werkzeug",
    "pynacl",
    "tomlkit",
    "proto-plus",
    "importlib-resources",
    "asn1crypto",
    "azure-core",
    "deprecated",
    "distlib",
    "websocket-client",
    "annotated-types",
    "coverage",
    "google-cloud-storage",
    "more-itertools",
]
print("All packages: ", packages_list)
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


def run_command(command: List[str], cwd="", repetitions=1, mute_output=False):
    start_time = time.perf_counter()
    if repetitions == 1:
        execute_command(command, cwd=cwd, mute_output=mute_output)
    else:
        for i in tqdm(range(repetitions)):
            execute_command(command, cwd=cwd, mute_output=mute_output)

    end_time = time.perf_counter()

    return end_time - start_time


def initialize_project(work_dir):
    run_command(["pdm", "init", "-n"], cwd=work_dir)


def install_packages(work_dir):
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
                f"{clean_time:.5f}s",
                f"{dirty_time:.5f}s",
                f"{percent_difference:.2f}%",
            ]
        )

    print(
        tabulate(
            table, headers=["Test", "Clean project", "Dirty project", "Difference"]
        )
    )


def test_performance_difference(test_suite, repetitions):
    with tempfile.TemporaryDirectory() as work_dir:
        initialize_project(work_dir)

        clean_project_times = {}
        dirty_project_times = {}

        print("Running tests on clean project...")
        for test_name, test_command in test_suite.items():
            print(f"Test {test_name}:")
            clean_project_times[test_name] = (
                run_command(
                    test_command,
                    repetitions=repetitions,
                    cwd=work_dir,
                    mute_output=True,
                )
                / repetitions
            )

        install_packages(work_dir)

        print("Running tests on dirty project...")
        for test_name, test_command in test_suite.items():
            print(f"Test {test_name}:")
            dirty_project_times[test_name] = (
                run_command(
                    test_command,
                    repetitions=repetitions,
                    cwd=work_dir,
                    mute_output=True,
                )
                / repetitions
            )

        report_results(clean_project_times, dirty_project_times)


def main():
    current_path = Path(__file__).parent
    testing_commands = {
        "pdm list": ["pdm", "list"],
        "findpython": [
            "pdm",
            "run",
            (current_path / "../src/pdm_helpers/findpython.py").resolve(),
        ],
        "regular python": [
            "pdm",
            "run",
            "python3",
            (current_path / "../src/pdm_helpers/speed_test.py").resolve(),
        ],
        "python without site modules": [
            "pdm",
            "run",
            "python3",
            "-S",
            (current_path / "../src/pdm_helpers/speed_test.py").resolve(),
        ],
    }

    parser = argparse.ArgumentParser(
        description="Compare the performance of Python startup without packages and with many packages installed"
    )
    parser.add_argument(
        "--repetitions",
        type=int,
        default=1,
        help="number of test repetitions to run (default 1)",
    )

    args = parser.parse_args()

    test_performance_difference(testing_commands, repetitions=args.repetitions)


if __name__ == "__main__":
    main()
