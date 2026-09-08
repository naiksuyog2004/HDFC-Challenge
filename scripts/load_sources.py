from pathlib import Path
from datetime import datetime

import pandas as pd

from backend.app.database import SessionLocal
from backend.app.models import Company, Source


# Location of the supplied CSV file
CSV_PATH = Path("data/disclosure_links.csv")


COMPANIES = {
    "Maruti Suzuki": "MARUTI",
    "Infosys": "INFY",
}


def get_or_create_company(db, name, ticker):
    company = (
        db.query(Company)
        .filter(Company.name == name)
        .first()
    )

    if company:
        return company

    company = Company(
        name=name,
        ticker=ticker,
    )

    db.add(company)
    db.commit()
    db.refresh(company)

    return company


def parse_date(date_string):
    if pd.isna(date_string):
        return None

    try:
        return datetime.strptime(
            str(date_string),
            "%d-%m-%Y",
        )
    except ValueError:
        return None


def main():
    print("Reading source CSV...")

    df = pd.read_csv(CSV_PATH)

    print(f"Found {len(df)} sources.")

    db = SessionLocal()

    try:
        for _, row in df.iterrows():

            company_name = row["company"]

            if company_name not in COMPANIES:
                print(
                    f"Skipping unknown company: {company_name}"
                )
                continue

            company = get_or_create_company(
                db,
                company_name,
                COMPANIES[company_name],
            )

            # Do not insert the same URL twice.
            existing_source = (
                db.query(Source)
                .filter(Source.url == row["url"])
                .first()
            )

            if existing_source:
                print(
                    f"Already exists: {row['title']}"
                )
                continue

            source = Source(
                company_id=company.id,
                source_type=row["type"],
                title=row["title"],
                url=row["url"],
                published_at=parse_date(row["date"]),
                status="pending",
            )

            db.add(source)

            print(
                f"Added: {company_name} | "
                f"{row['type']} | "
                f"{row['title']}"
            )

        db.commit()

        print()
        print("Source ingestion completed successfully.")

    except Exception as error:
        db.rollback()
        print(f"Error while loading sources: {error}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()