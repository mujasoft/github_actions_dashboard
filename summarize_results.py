import json
from datetime import datetime
import statistics
from pprint import pprint
import os
import typer


# Load typer.
app = typer.Typer(
    help="A tool to read a json of github actions results and print a summary")


def parse_duration(run):
    """Return run duration in seconds (or None if missing)."""

    start = run.get("run_started_at")
    end = run.get("updated_at")

    if not start or not end:
        return None

    start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
    end_dt = datetime.fromisoformat(end.replace("Z", "+00:00"))
    return (end_dt - start_dt).total_seconds()


def get_statistics(list):
    """Given a list, return a dictionary of various statistics.

    Args:
        list (int): list of ints.

    Returns:
        _dict_: dictionary of the following fields:
                - average
                - max
                - min
                - median
    """

    average_value = round(statistics.mean(list), 2)
    median_value = round(statistics.median(list), 2)
    max_value = round(max(list), 2)
    min_value = round(min(list), 2)

    return {
            "average": average_value, "median": median_value,
            "max": max_value, "min": min_value
           }


@app.command()
def read_json_file_and_print_summary(filename: str = 'results.json',
                                     help="Path to local store."):
    """Go through results from a .json and print a summary.

    Args:
        filename (str): location of json file.
    """

    if ".json" not in filename:
        filename = os.path.join(filename, ".json")

    with open(filename) as f:
        runs = json.load(f)

    durations = []
    successes = 0
    failures = 0
    total = 0

    for run in runs:
        total = total + 1
        if run["conclusion"] == "success":
            successes += 1
        else:
            failures += 1
        
        duration = parse_duration(run)
        durations.append(duration)

    success_rate = round(100*(successes/total), 1)
    failure_rate = round(100*(failures/total), 1)

    duration_stats = get_statistics(durations)

    print("GitHub Actions Summary")
    print("-"*50)
    print(f"Successes   : {successes} ({success_rate}%)")
    print(f"Failures    : {failures} ({failure_rate}%)")
    print(f"Total Runs  : {total}")

    print("\nDuration (seconds)")
    print(f"    Max.     : {duration_stats['max']}")
    print(f"    Min.     : {duration_stats['min']}")
    print(f"    Avg.     : {duration_stats['average']}")
    print(f"    Median   : {duration_stats['median']}")


if __name__ == "__main__":
    app()
