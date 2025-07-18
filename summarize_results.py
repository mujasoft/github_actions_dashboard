# MIT License
#
# Copyright (c) 2025 Mujaheed Khan
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import json
import os
import statistics
import webbrowser
from datetime import datetime

import typer


# Load typer.
app = typer.Typer(
    help="A tool that summarizes the information from captured github action\
          runs data")


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
def summarize(filename: str = typer.Option('results.json',
                                           help="Path to a .json containing"
                                                " info of github action"
                                                " runs."),
              html_filename: str = typer.Option('summary.html',
                                                help="Save a html report"
                                                     " with this name")):
    """Summarize and generate a report from a specified json file."""

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

    repo_name = runs[0].get("repository", {}).get("full_name", "Unknown Repo")
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

    summary_dict = {
        "repo_name": repo_name,
        "successes": successes, "total": total, "failures": failures,
        "success_rate": success_rate, "failure_rate": failure_rate,
        "duration_stats": duration_stats
    }

    create_html(summary_dict, html_filename)


def create_html(summary, filename):
    """Create a summary html using a

    Args:
        summary (dict): dictionary of results
        filename (str): filename of rendered html
    """

    if 'html' not in filename:
        filename = os.path.join(filename, ".html")

    html_plate = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>GitHub Actions Dashboard</title>
  <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/semantic-ui@2.5.0/\
    dist/semantic.min.css">
  <style>
    body {{
      background: linear-gradient(to bottom right, #C0C0C0, #A9A9A9);
      padding: 0;
      margin: 0;
      font-family: 'Segoe UI', sans-serif;
    }}
    .top-bar {{
      background-color: #2185d0;
      color: white;
      padding: 1em 0;
      font-size: 1.5em;
      font-weight: bold;
      text-align: center;
      box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }}
    .main-content {{
      padding: 2em;
      margin-top: 2em;
    }}
  </style>
</head>
<body>
  <div class="top-bar">
    GITHUB ACTIONS DASHBOARD
  </div>
  <div class="ui container main-content">
    <div class="ui segment">
      <h3 class="ui dividing header">Repository Summary</h3>
      <table class="ui blue celled table">
        <tbody>
          <tr><td><strong>Repository</strong></td><td>{}</td></tr>
          <tr><td><strong>Total Runs</strong></td><td>{}</td></tr>
          <tr><td><strong>Success</strong></td><td>{} ({}%)</td></tr>
          <tr><td><strong>Failure</strong></td><td>{} ({}%)</td></tr>
        </tbody>
      </table>
    </div>

    <div class="ui segment">
      <h3 class="ui dividing header">Stats & Chart</h3>
      <div class="ui stackable two column grid">
        <div class="column">
          <table class="ui blue celled table">
            <thead>
              <tr><th>Metric</th><th>Time (seconds)</th></tr>
            </thead>
            <tbody>
              <tr><td>Average</td><td>{}</td></tr>
              <tr><td>Median</td><td>{}</td></tr>
              <tr><td>Min</td><td>{}</td></tr>
              <tr><td>Max</td><td>{}</td></tr>
            </tbody>
          </table>
        </div>

        <div class="column">
          <div id="pie-chart" style="width: 100%; height: 400px;"></div>
        </div>
      </div>
    </div>
  </div>

  <script>
    var data = [{{
      values: [{}, {}],
      labels: ['Successes', 'Failures'],
      type: 'pie',
      marker: {{
        colors: ['#4CAF50', '#F44336']
      }},
      textinfo: 'label+percent',
      insidetextorientation: 'radial'
    }}];

    var layout = {{
      title: 'Success vs Failure Breakdown',
      height: 400,
      width: 500,
      showlegend: true
    }};

    Plotly.newPlot('pie-chart', data, layout);
  </script>
</body>
</html>
""".format(
        summary["repo_name"],
        summary["total"],
        summary["successes"], summary["success_rate"],
        summary["failures"], summary["failure_rate"],
        summary["duration_stats"]["average"],
        summary["duration_stats"]["median"],
        summary["duration_stats"]["min"],
        summary["duration_stats"]["max"],
        summary["successes"], summary["failures"]
    )

    with open(filename, 'w') as f:
        f.write(html_plate)
    print(f"\nHTML summary written to {filename}")

    # Pop the report open in a browser for user convenience.
    webbrowser.open(f"file://{os.path.abspath(filename)}")


if __name__ == "__main__":
    app()
