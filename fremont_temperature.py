"""
Fetch and visualize daily temperatures for Fremont, California (last 7 days).
Uses the Open-Meteo forecast API.
"""

import os
from datetime import date, timedelta

import matplotlib.pyplot as plt
import pandas as pd
import requests

# Fremont, California coordinates
FREMONT_LATITUDE = 37.5485
FREMONT_LONGITUDE = -121.9886

API_URL = "https://api.open-meteo.com/v1/forecast"


def get_last_week_dates():
    """Return start and end dates for the previous 7 days (excluding today)."""
    today = date.today()
    end_date = today - timedelta(days=1)
    start_date = end_date - timedelta(days=6)
    return start_date.isoformat(), end_date.isoformat()


def fetch_temperature_data(start_date, end_date):
    """Fetch daily min/max temperatures from Open-Meteo."""
    params = {
        "latitude": FREMONT_LATITUDE,
        "longitude": FREMONT_LONGITUDE,
        "start_date": start_date,
        "end_date": end_date,
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "America/Los_Angeles",
    }

    response = requests.get(API_URL, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def build_dataframe(api_data):
    """Convert API response into a pandas DataFrame with average temperature."""
    daily = api_data["daily"]
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(daily["time"]),
            "min_temp_c": daily["temperature_2m_min"],
            "max_temp_c": daily["temperature_2m_max"],
        }
    )
    df["avg_temp_c"] = (df["min_temp_c"] + df["max_temp_c"]) / 2
    return df


def print_temperature_info(df, start_date, end_date):
    """Print a summary of temperature data for last week."""
    print("=" * 60)
    print("Fremont, California — Temperature Report (Last Week)")
    print(f"Period: {start_date} to {end_date}")
    print(f"Location: {FREMONT_LATITUDE}°N, {FREMONT_LONGITUDE}°W")
    print("=" * 60)

    print("\nDaily Temperatures (°C):")
    print("-" * 60)
    for _, row in df.iterrows():
        day = row["date"].strftime("%A, %b %d")
        print(
            f"  {day}:  Min {row['min_temp_c']:.1f}°C  |  "
            f"Max {row['max_temp_c']:.1f}°C  |  "
            f"Avg {row['avg_temp_c']:.1f}°C"
        )

    print("\nWeekly Summary (°C):")
    print("-" * 60)
    print(f"  Lowest minimum:  {df['min_temp_c'].min():.1f}°C")
    print(f"  Highest maximum: {df['max_temp_c'].max():.1f}°C")
    print(f"  Average minimum: {df['min_temp_c'].mean():.1f}°C")
    print(f"  Average maximum: {df['max_temp_c'].mean():.1f}°C")
    print(f"  Average daily avg: {df['avg_temp_c'].mean():.1f}°C")
    print("=" * 60)


def create_temperature_graph(df, start_date, end_date, output_dir="output"):
    """Create and save a line chart of min, max, and average temperatures."""
    os.makedirs(output_dir, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 6))

    dates = df["date"]
    ax.plot(dates, df["max_temp_c"], marker="o", linewidth=2, label="Max Temp (°C)", color="#e74c3c")
    ax.plot(dates, df["avg_temp_c"], marker="s", linewidth=2, label="Avg Temp (°C)", color="#f39c12")
    ax.plot(dates, df["min_temp_c"], marker="^", linewidth=2, label="Min Temp (°C)", color="#3498db")

    ax.set_title(
        f"Fremont, CA Daily Temperatures\n({start_date} to {end_date})",
        fontsize=14,
        fontweight="bold",
    )
    ax.set_xlabel("Date", fontsize=11)
    ax.set_ylabel("Temperature (°C)", fontsize=11)
    ax.legend(loc="best")
    ax.grid(True, alpha=0.3)
    fig.autofmt_xdate()
    plt.tight_layout()

    output_path = os.path.join(output_dir, "fremont_temperature_last_week.png")
    plt.savefig(output_path, dpi=150)
    print(f"\nGraph saved to: {os.path.abspath(output_path)}")
    plt.show()


def main():
    start_date, end_date = get_last_week_dates()

    print(f"Fetching temperature data for {start_date} to {end_date}...")
    api_data = fetch_temperature_data(start_date, end_date)
    df = build_dataframe(api_data)

    print_temperature_info(df, start_date, end_date)
    create_temperature_graph(df, start_date, end_date)


if __name__ == "__main__":
    main()