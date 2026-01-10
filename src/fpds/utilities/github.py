import os

def set_github_output(**kwargs) -> None:
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a") as f:
            for key, value in kwargs.items():
                f.write(f"{key}={value}\n")
