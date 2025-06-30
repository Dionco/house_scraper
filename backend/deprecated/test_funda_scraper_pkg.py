import json
from funda_scraper import FundaScraper

# Example: search for rental listings in Utrecht between 1000 and 2000 euro
def main():
    # area: e.g. "utrecht", want_to: "rent" or "huur"
    scraper = FundaScraper(
        area="utrecht",
        want_to="rent",
        min_price=1000,
        max_price=2000,
        n_pages=1,  # Only fetch the first page for test
        sort="date_down"
    )
    df = scraper.run()
    print(f"Found {len(df)} listings.")
    print(df.head())
    # Optionally print as JSON
    print(df.to_json(orient='records', force_ascii=False, indent=2))

if __name__ == "__main__":
    main()

# This file is not imported by any main code. Move to deprecated/ if not needed.
