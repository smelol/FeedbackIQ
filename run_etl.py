from load_surveys_to_unified import load_surveys
from load_api_to_unified import load_api_reviews


def run_etl():
    print("=== ETL: Surveys ===")
    load_surveys()

    print("\n=== ETL: API Reviews ===")
    load_api_reviews()

    print("\nETL completado.")


if __name__ == "__main__":
    run_etl()