import subprocess


def main():
    packages_list = [
        "numpy",
        "pandas",
        "requests",
        "matplotlib",
        "scikit-learn",
        "tensorflow",
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
        "torch",
    ]

    for name in packages_list:
        subprocess.run(['pip', 'install', name])


if __name__ == "__main__":
    main()
