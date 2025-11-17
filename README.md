# Weather Forecast CLI

This project is a small command-line helper that fetches a three-day forecast for one or more U.S. ZIP codes using the AccuWeather API. It no longer embeds any credentials; provide your own API key at runtime.

## Prerequisites
- Python 3.9+
- An AccuWeather API key

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Provide your API key via an environment variable or flag:
   ```bash
   export ACCUWEATHER_API_KEY="your-key-here"
   ```

## Usage
Run the script with the default locations (Fremont, San Francisco, Los Angeles):
```bash
python main.py
```

Supply your own ZIP codes:
```bash
python main.py 10001 60601 --api-key "$ACCUWEATHER_API_KEY"
```

Example output:
```
Location                Day 1        Day 2        Day 3
Fremont, CA             H:  70° L:  55°  H:  68° L:  54°  H:  67° L:  53°
```

## Notes
- Requests time out after 10 seconds to avoid hanging.
- Errors from the API (e.g., bad key or unknown ZIP) are surfaced with helpful messages.
