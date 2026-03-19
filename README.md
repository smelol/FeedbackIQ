# FeedbackIQ

Pipeline:

```
[customer_surveys] ──┐
                     ├── ETL → unified_reviews
[API FastAPI]   ─────┘
```

Destino:

* `unified_reviews` → tabla consolidada lista para análisis

## Seed

El script `seed.py` genera:

* ~600 encuestas (`customer_surveys`)
* ~700+ reviews API
* duplicados intencionales
* casos críticos
* picos de reseñas negativas
* locales con bajo promedio

### Ejecutar:

```bash
py init_db.py
py seed.py
```

Genera:

* datos en SQLite
* archivo `data/api_reviews_seed.json`

Reproducible con `random.seed(42)`.

---

## API de reseñas (FastAPI)

Simula una fuente externa.

### Endpoint:

```
GET /api/reviews
```

### Parámetros:

* `location_id` (1–15)
* `since` (ISO datetime)

### Ejemplo:

```
http://127.0.0.1:8081/api/reviews?location_id=2&since=2026-03-10T00:00:00Z
```

### Ejecutar:

```bash
py -m uvicorn src.api_source.app:app --host 127.0.0.1 --port 8081 --reload
```

Swagger:

```
http://127.0.0.1:8081/docs
```

---

## ETL

### 1. Surveys → unified

```bash
py load_surveys_to_unified.py
```

* filtra últimos 7 días
* transforma datos
* inserta en `unified_reviews`
* ignora duplicados

---

### 2. API → unified

(la API debe estar corriendo)

```bash
py load_api_to_unified.py
```

* consulta por `location_id`
* filtra por `since`
* transforma datos
* inserta en `unified_reviews`
* ignora duplicados

---

### 3. Pipeline completo

```bash
py run_etl.py
```

Ejecuta ambas fuentes.

---

## Sentiment analysis

(debe haber resenas en unified_reviews)
(debe haber una clave de openAI en .env OPENAI_API_KEY)

```bash
py run_analysis.py
```

* toma (20 por defecto) reviews de unified_reviews
* crea un prompt con cada review
* ejecuta el modelo con cada prompt
* verifica que el resultado sea valido
* inserta resultado en review_analysis

Salida esperada por review

* sentiment → positive | negative | neutral
* categories → lista de categorías válidas
* summary → resumen corto
* urgency → entero entre 1 y 5

Categorías usadas

* producto
* servicio
* ambiente
* precio
* limpieza
* otro

## Alertas

El sistema genera alertas a partir de reglas sobre unified_reviews y review_analysis.

Ejecutar:
```bash
py run_alerts.py
```

# Reglas actuales

1. CRITICA

Se genera si una review tiene:

urgency = 5

2. ALTA

Se genera si un local tiene:

3 o más reseñas negativas en las últimas 24 horas

3. MEDIA

Se genera si un local tiene:

promedio semanal de rating menor a 3.5

# Persistencia

Las alertas se guardan en:

tabla alerts
archivo data/alerts_log.jsonl

Dedupe
Cada alerta usa un dedupe_key único para evitar duplicados si el detector corre varias veces.

## Reporte semanal

Genera un HTML con métricas y resumen ejecutivo.

Ejecutar:
```bash
py run_report.py
```

Salida:

data/reports/weekly_report.html

### Incluye
- total de reseñas
- total analizadas
- total de alertas
- distribución de sentimiento
- top 3 locales mejor valorados
- top 3 locales con más problemas
- categorías más mencionadas
- resumen ejecutivo generado con IA
- alertas recientes


## Pipeline completo

Ejecuta ETL, análisis y alertas en secuencia.

Ejecutar:
```bash
py run_pipeline.py
```

Orden:

ETL
análisis IA
alertas
resumen final por consola

La API debe estar corriendo antes de lanzar el pipeline.



# Flujo recomendado
1. Inicializar y sembrar datos
```bash
py init_db.py
py seed.py
```

2. Levantar la API
```bash
py -m uvicorn src.api_source.app:app --host 127.0.0.1 --port 8081 --reload
```

3. Correr pipeline completo
```bash
py run_pipeline.py
```
4. Generar reporte
```bash
py run_report.py
```
