import requests
import os
import json
import time
import sys
from dynaconf import Dynaconf
import typer

# Load config. 
settings = Dynaconf(settings_files=["settings.toml"], environments=True, 
                    default_env="default")

# Load typer.
app = typer.Typer(
    help="A tool to fetch github workflow runs and dump them into a json."
)


def check_rate_limit_and_sleep_if_needed(github_api_url):
    """Check if rate limit has been exceeded and sleep if it did.
    """
    
    headers = get_headers()

    # Get data through a get request.
    url = f"{github_api_url}/rate_limit"
    r = requests.get(url, headers=headers)

    # Dump data.
    data = r.json()

    # Figure out remaining data.
    remaining = data["rate"]["remaining"]

    # Time to be dormant.
    if remaining == 0:
        sleep_time = int(data["rate"]["reset"] - time.time()) + 5
        print(f"*** The rate limit has been exceeded so will "
              f"sleep for {sleep_time}s.")
        time.sleep(sleep_time)


def get_workflow_runs(headers, github_api_url, no_of_results_per_page, repo, 
                      page):

    url = f"{github_api_url}/repos/{repo}/actions/runs"

    # Construct parameters.
    params = {"per_page": no_of_results_per_page, "page": page}
    r = requests.get(url, headers=headers, params=params)

    status = False
    if r.status_code == 200:
        status = True

    return status, r.json()


@app.command()
def get_github_actions_run(
    configuration_profile: str = typer.Option(
        "default", "--configuration-profile", "-c",
        help="Dynaconf config section to use."
    ),
    filename: str = typer.Option(
        "results.json", "--filename", "-o",
        help="Output file for JSON data"
    ),
    sleep_interval: int = typer.Option(
        1, "--sleep-interval", "-s",
        help="Time (in seconds) to wait between page fetches."
    )
):

    headers = get_headers()

    settings.configure(env=configuration_profile)

    # Dump settings.    
    max_no_of_pages = settings.get("max_no_of_pages")
    repo = settings.get("repo")
    no_of_results_per_page = settings.get("no_of_results_per_page")
    github_api_url = settings.get("github_api_url")

    github_action_runs = []

    for page in range(1, max_no_of_pages + 1):

        # May have to wait if rate limit is exceeded.
        check_rate_limit_and_sleep_if_needed(github_api_url)

        print(f"*** Fetching page {page}")
        status, data = get_workflow_runs(headers, github_api_url, 
                                         no_of_results_per_page,
                                         repo, page)
        if not status:
            sys.exit("*** Failed to get workflow information")
        runs = data.get("workflow_runs", [])

        github_action_runs.extend(runs)
        time.sleep(sleep_interval)

    # Log information.
    with open(filename, "w") as f:
        json.dump(github_action_runs, f, indent=2)

    print(f"*** Saved {len(github_action_runs)} runs to {filename}\n")


def get_headers():
    """Construct a header dictionary with $GITHUB_TOKEN for github rest APIs.

    Returns:
        header(_dict_): A dict. populated appropriately.
    """

    # GITHUB_TOKEN is not defined, prompt user to set to it.
    github_token = os.getenv("GITHUB_TOKEN", "")

    if github_token == "":
        sys.exit("*** GITHUB_TOKEN is not set!\n\n"
                 "Without it, there is no accessing github. Please"
                 "visit the following for more info:\n"
                 "https://docs.github.com/en/authentication/keeping\
                    -your-account-and-data-secure/managing-your-personal\
                        -access-tokens")

    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github+json",
    }

    return headers


if __name__ == "__main__":

    app()

