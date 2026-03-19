CATEGORIES = [
    "producto",
    "servicio",
    "ambiente",
    "precio",
    "limpieza",
    "otro",
]


def build_prompt(text: str, rating: int) -> str:
    return f"""
Analiza la siguiente reseña de cliente.

Responde con EXACTAMENTE un objeto JSON válido.
No uses markdown.
No uses bloques de código.
No agregues texto antes ni después del JSON.
No expliques tu respuesta.

El formato debe ser exactamente:

{{
  "sentiment": "positive | negative | neutral",
  "categories": ["categorías válidas"],
  "summary": "máximo 100 caracteres",
  "urgency": 1
}}

Reglas:
- Usa solo estas categorías: {CATEGORIES}
- No inventes categorías
- Si ninguna categoría aplica claramente, usa ["otro"]
- "summary" debe ser corto, claro y de máximo 100 caracteres
- "urgency" debe ser un entero entre 1 y 5
- Usa urgency=5 solo si hay riesgo serio de salud, seguridad o agresión
- Usa urgency=4 para problemas graves sin riesgo extremo
- Usa urgency=1 para molestias menores

Reseña:
\"\"\"{text}\"\"\"

Rating: {rating}
""".strip()