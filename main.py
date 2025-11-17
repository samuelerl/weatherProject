"""CLI utility for fetching short-term weather forecasts from AccuWeather.

The script queries the AccuWeather Locations and Forecasts APIs to retrieve the
next three days of high/low temperatures for one or more ZIP codes. Results are
printed in a simple table to make the data easy to read.
"""
from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from typing import Dict, Iterable, List

import requests

# Default ZIP codes used when no explicit input is provided.
DEFAULT_ZIP_CODES = {
    "New York, NY": "10036",
    "San Francisco, CA": "94103",
    "Los Angeles, CA": "90012",
}

API_BASE = "https://dataservice.accuweather.com"


@dataclass
class DailyForecast:
    """Container for a single day's forecast temperatures."""

    high: int
    low: int

    @classmethod
    def from_api(cls, forecast_entry: dict) -> "DailyForecast":
        maximum = forecast_entry["Temperature"]["Maximum"]["Value"]
        minimum = forecast_entry["Temperature"]["Minimum"]["Value"]
        return cls(high=int(maximum), low=int(minimum))


class AccuWeatherClient:
    """Lightweight client for the AccuWeather REST API."""

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def _get(self, path: str, *, params: Dict[str, str]) -> dict:
        response = requests.get(f"{API_BASE}{path}", params=params, timeout=10)
        response.raise_for_status()
        return response.json()

    def lookup_location_key(self, postal_code: str) -> str:
        data = self._get(
            "/locations/v1/postalcodes/search",
            params={"q": postal_code, "apikey": self.api_key},
        )
        if not data:
            raise ValueError(f"No location found for postal code {postal_code}")
        return data[0]["Key"]

    def fetch_daily_forecasts(self, location_key: str, *, days: int = 3) -> List[DailyForecast]:
        forecast_data = self._get(
            f"/forecasts/v1/daily/5day/{location_key}",
            params={"apikey": self.api_key},
        )
        daily_entries = forecast_data.get("DailyForecasts", [])
        if len(daily_entries) < days:
            raise ValueError("Insufficient forecast data returned from API")
        return [DailyForecast.from_api(entry) for entry in daily_entries[:days]]


def build_forecasts(client: AccuWeatherClient, zip_codes: Dict[str, str]) -> Dict[str, List[DailyForecast]]:
    forecasts: Dict[str, List[DailyForecast]] = {}
    for label, postal_code in zip_codes.items():
        location_key = client.lookup_location_key(postal_code)
        forecasts[label] = client.fetch_daily_forecasts(location_key)
    return forecasts


def render_table(forecasts: Dict[str, List[DailyForecast]]) -> str:
    lines = ["Location                Day 1        Day 2        Day 3"]
    for location, daily_forecasts in forecasts.items():
        padded_name = location.ljust(22)
        temps: Iterable[str] = (
            f"H:{forecast.high:3d}° L:{forecast.low:3d}°" for forecast in daily_forecasts
        )
        lines.append(f"{padded_name} " + "  ".join(temps))
    return "\n".join(lines)


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Show a 3-day forecast for ZIP codes.")
    parser.add_argument(
        "zip_codes",
        nargs="*",
        help="Postal codes to include. If omitted, defaults are used.",
    )
    parser.add_argument(
        "--api-key",
        dest="api_key",
        default=os.environ.get("ACCUWEATHER_API_KEY"),
        help="AccuWeather API key (or set ACCUWEATHER_API_KEY).",
    )
    return parser.parse_args(list(argv))


def main(argv: Iterable[str]) -> int:
    args = parse_args(argv)
    if not args.api_key:
        print("Error: AccuWeather API key is required (set --api-key or ACCUWEATHER_API_KEY).")
        return 1

    zip_codes = DEFAULT_ZIP_CODES if not args.zip_codes else {code: code for code in args.zip_codes}

    client = AccuWeatherClient(api_key=args.api_key)
    try:
        forecasts = build_forecasts(client, zip_codes)
    except (requests.HTTPError, ValueError) as exc:
        print(f"Failed to retrieve forecasts: {exc}")
        return 1

    print(render_table(forecasts))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
