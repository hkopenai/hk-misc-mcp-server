"""
Tool for fetching auction data from Government Logistics Department Hong Kong.

This module provides functionality to retrieve and process auction data
for a specified date range and language.
"""

import requests
import csv
from io import StringIO
from typing import List, Dict, Optional
from datetime import datetime


def validate_language(language: str) -> str:
    """Validate and return the uppercase language code."""
    lang = language.upper()
    if lang not in ["EN", "TC", "SC"]:
        raise ValueError("Language must be one of 'EN', 'TC', 'SC'")
    return lang


def create_date_range(
    start_year: int, start_month: int, end_year: int, end_month: int
) -> tuple:
    """Create start and end datetime objects for the specified date range."""
    start_date = datetime(start_year, start_month, 1)
    end_date = datetime(end_year, end_month, 28)  # Using 28 to cover most months safely
    return start_date, end_date


def fetch_csv_data(url: str) -> Optional[StringIO]:
    """Fetch CSV data from the given URL and return it as a StringIO object if successful."""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            content = response.content.decode("utf-8-sig")
            return StringIO(content)
        elif response.status_code == 404:
            print(f"Data not found for URL: {url}. Trying a smaller list number.")
        else:
            print(
                f"Unexpected status code {response.status_code} for URL: {url}. Continuing to older records."
            )
    except Exception as e:
        print(
            f"Error fetching data for URL: {url}: {str(e)}. Continuing to older records."
        )
    return None


def process_auction_row(
    row: Dict, start_date: datetime, end_date: datetime
) -> Optional[Dict]:
    """Process a single row of auction data and return a formatted dictionary if within date range."""
    if "Description" not in row or "Quantity" not in row:
        return None

    auction_date_str = row.get("Date of Auction", "")
    try:
        auction_date = datetime.strptime(auction_date_str, "%d/%m/%Y")
        if start_date <= auction_date <= end_date:
            return {
                "Date of Auction": auction_date.isoformat().split("T")[0],
                "Auction List No.": row.get("Auction List No.", ""),
                "Lot No.": row.get("Lot No.", ""),
                "Description": row["Description"],
                "Quantity": row["Quantity"],
                "Unit": row.get("Unit", ""),
            }
    except ValueError:
        return {
            "Date of Auction": auction_date_str,
            "Auction List No.": row.get("Auction List No.", ""),
            "Lot No.": row.get("Lot No.", ""),
            "Description": row["Description"],
            "Quantity": row["Quantity"],
            "Unit": row.get("Unit", ""),
        }
    return None


def get_auction_data(
    start_year: int, start_month: int, end_year: int, end_month: int, language: str
) -> List[Dict]:
    """
    Fetch auction data from Government Logistics Department Hong Kong for a specified range of years and language.
    The tool fetches data starting from the latest list number (24) backward until the specified year range is covered.
    Items are filtered by the 'Date of Auction' to ensure they fall within the specified date range.

    Args:
        start_year (int): Starting year for the data range.
        start_month (int): Starting month for the data range (1-12).
        end_year (int): Ending year for the data range.
        end_month (int): Ending month for the data range (1-12).
        language (str): Language code for the data ('EN', 'TC', 'SC').

    Returns:
        List[Dict]: List of dictionaries containing auction data with Description and Quantity.
    """
    base_url = "https://www.gld.gov.hk/datagovhk/supplies-mgmt/auctionList_{}-{}_{}.csv"
    result = []

    lang = validate_language(language)
    start_date, end_date = create_date_range(
        start_year, start_month, end_year, end_month
    )

    current_year = end_year
    current_list_no = 24  # Always start from list number 24

    while current_year >= start_year:
        url = base_url.format(current_list_no, current_year, lang)
        csv_content = fetch_csv_data(url)
        if csv_content:
            reader = csv.DictReader(csv_content)
            for row in reader:
                processed_row = process_auction_row(row, start_date, end_date)
                if processed_row:
                    result.append(processed_row)

        current_list_no -= 1
        if current_list_no < 1:
            current_list_no = 24
            current_year -= 1
            if current_year < start_year:
                break

    return result
