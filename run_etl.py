from load_surveys_to_unified import load_surveys
from load_api_to_unified import load_api_reviews


def run_etl():
    print("=== ETL: Surveys ===")
    surveys_result = load_surveys()

    print("\n=== ETL: API Reviews ===")
    api_result = load_api_reviews()

    result = {
        "surveys": surveys_result,
        "api": api_result,
    }

    print("\nETL completado.")
    return result


if __name__ == "__main__":
    run_etl()