from src.analysis.llm_client import generate_text


def build_executive_summary_prompt(metrics: dict) -> str:
    return f"""
Genera un resumen ejecutivo breve en español, en un solo párrafo, con tono profesional y claro.

No uses markdown.
No uses viñetas.
Máximo 120 palabras.

Datos:
- Total reseñas: {metrics['total_reviews']}
- Total analizadas: {metrics['total_analyzed']}
- Total alertas: {metrics['total_alerts']}
- Distribución sentimiento: {metrics['sentiment_distribution']}
- Top locales mejor valorados: {metrics['top_rated_locations']}
- Top locales con más problemas: {metrics['problematic_locations']}
- Categorías más mencionadas: {metrics['top_categories']}
- Alertas recientes: {metrics['recent_alerts']}
""".strip()


def generate_executive_summary(metrics: dict) -> str:
    return generate_text(build_executive_summary_prompt(metrics))