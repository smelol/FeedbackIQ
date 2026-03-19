from src.reports.metrics import build_report_metrics
from src.reports.executive_summary import generate_executive_summary
from src.reports.html_report import render_weekly_report


def run_report():
    print("Construyendo métricas del reporte...")
    metrics = build_report_metrics()

    print("Generando resumen ejecutivo...")
    executive_summary = generate_executive_summary(metrics)

    context = {
        **metrics,
        "executive_summary": executive_summary,
    }

    print("Renderizando HTML...")
    output_path = render_weekly_report(context)

    print(f"Reporte generado: {output_path}")


if __name__ == "__main__":
    run_report()