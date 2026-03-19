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
