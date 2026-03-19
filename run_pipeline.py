from run_etl import run_etl
from src.analysis.analyzer import run_analysis
from src.alerts.detector import run_alert_detection


def print_section(title: str):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def run_pipeline():
    print_section("PIPELINE FEEDBACKIQ")

    print_section("1. ETL")
    etl_result = run_etl()

    print_section("2. ANALISIS IA")
    analysis_result = run_analysis(batch_size=20)

    print_section("3. ALERTAS")
    alerts_result = run_alert_detection()

    print_section("4. RESUMEN FINAL")

    print("ETL Surveys:")
    print(f"  procesadas: {etl_result['surveys']['processed']}")
    print(f"  insertadas: {etl_result['surveys']['inserted']}")
    print(f"  duplicadas: {etl_result['surveys']['duplicates']}")

    print("\nETL API:")
    print(f"  fetched: {etl_result['api']['fetched']}")
    print(f"  insertadas: {etl_result['api']['inserted']}")
    print(f"  duplicadas: {etl_result['api']['duplicates']}")
    print(f"  locales con error: {len(etl_result['api']['failed_locations'])}")

    print("\nAnalisis IA:")
    print(f"  intentadas: {analysis_result['attempted']}")
    print(f"  exitosas: {analysis_result['success']}")
    print(f"  fallidas: {analysis_result['failed']}")

    print("\nAlertas:")
    print(f"  candidatas: {alerts_result['candidates']}")
    print(f"  nuevas: {alerts_result['inserted']}")
    print(f"  duplicadas: {alerts_result['duplicates']}")

    return {
        "etl": etl_result,
        "analysis": analysis_result,
        "alerts": alerts_result,
    }


if __name__ == "__main__":
    run_pipeline()