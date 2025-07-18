# GitHub Actions Dashboard Tool

Summarize the situation with your github actions! 

This is a CLI tool that allows the user to fetch GitHub Actions workflow runs for any public or private repository, summarize them, and generate a helpful HTML dashboard.

The project consists of two primary components:

1. **get_github_action_runs.py** which downloads workflow run data from the GitHub REST API and saves it as a JSON. 
2. **summarize_results.py** which computes success/failure statistics and job durations, and renders a polished report using Semantic UI and Plotly.js.

---

## Features

- Fetch workflow runs from any GitHub repository using GitHub's REST API and save them in a JSON.
- Support for multiple configuration profiles via `settings.toml`
- Summarize pass/fail counts, rates, and duration statistics
- Generate an interactive HTML dashboard using Semantic UI and Plotly.js
- Automatically opens the dashboard in the browser
- Command-line interface built with Typer
- GitHub authentication via personal access token

---
## Prerequisite
### Requirements

Install dependencies using `requirements.txt`:

```bash
pip3 install -r requirements.txt
```

Required packages:
- requests
- typer
- dynaconf

---

### GitHub Authentication

This tool requires a GitHub personal access token with `repo` access. It needs to be a 'classic' token.

Set it as an environment variable:

```bash
export GITHUB_TOKEN=ghp_your_token_here
```
The tool will error out othewrise.
## Example Usage

### 1. Fetch GitHub Actions Runs

```bash
python get_github_action_runs.py --configuration-profile homebrew --filename results.json
```

This will fetch GitHub Actions data for the `homebrew/brew` repository (as defined in `settings.toml`) and store the results in `results.json`.

### 2. Generate Summary Dashboard

```bash
python summarize_results.py --filename results.json --html-filename summary.html
```

This will:
- Parse the results
- Calculate success/failure stats
- Compute duration metrics (average, median, min, max)
- Render a semantic HTML report with interactive Plotly charts
- Automatically open the report in your browser

---

## Configuration (`settings.toml`)

Define multiple repositories under different profiles. Example:

```toml
[default]
github_api_url = "https://api.github.com"
repo = "homebrew/brew"
no_of_results_per_page = 50
max_no_of_pages = 3

[cpython]
repo = "python/cpython"
no_of_results_per_page = 25
max_no_of_pages = 2
```

You can switch profiles using the `--configuration-profile` flag.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
