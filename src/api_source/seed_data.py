from datetime import datetime, timedelta, UTC


def build_api_reviews_seed():
    now = datetime.now(UTC)

    reviews = [
        # Local 1 - mezcla normal
        {
            "review_id": "api-1001",
            "location_id": 1,
            "rating": 5,
            "text": "Excelente café y atención muy amable",
            "author": "Carlos",
            "created_at": (now - timedelta(days=1)).isoformat(),
        },
        {
            "review_id": "api-1002",
            "location_id": 1,
            "rating": 4,
            "text": "Buen ambiente, volvería",
            "author": "Laura",
            "created_at": (now - timedelta(days=2)).isoformat(),
        },

        # Local 2 - problemático, útil para alertas
        {
            "review_id": "api-2001",
            "location_id": 2,
            "rating": 1,
            "text": "Muy mala experiencia, el lugar estaba sucio y el servicio fue grosero",
            "author": "Ana",
            "created_at": (now - timedelta(hours=6)).isoformat(),
        },
        {
            "review_id": "api-2002",
            "location_id": 2,
            "rating": 1,
            "text": "La comida llegó fría y tardaron demasiado",
            "author": "Luis",
            "created_at": (now - timedelta(hours=5)).isoformat(),
        },
        {
            "review_id": "api-2003",
            "location_id": 2,
            "rating": 2,
            "text": "Pésimo servicio, nadie resolvió nada",
            "author": "Marta",
            "created_at": (now - timedelta(hours=4)).isoformat(),
        },

        # Local 3 - caso urgente
        {
            "review_id": "api-3001",
            "location_id": 3,
            "rating": 1,
            "text": "Encontré un vidrio en mi bebida, esto es gravísimo",
            "author": "Pedro",
            "created_at": (now - timedelta(hours=3)).isoformat(),
        },

        # Local 4 - neutrales
        {
            "review_id": "api-4001",
            "location_id": 4,
            "rating": 3,
            "text": "Normal, nada especial",
            "author": None,
            "created_at": (now - timedelta(days=3)).isoformat(),
        },

        # Local 5 - duplicado intencional
        {
            "review_id": "api-5001",
            "location_id": 5,
            "rating": 5,
            "text": "Muy rico todo",
            "author": "Sofía",
            "created_at": (now - timedelta(days=1, hours=2)).isoformat(),
        },
        {
            "review_id": "api-5001",  # duplicado intencional
            "location_id": 5,
            "rating": 5,
            "text": "Muy rico todo",
            "author": "Sofía",
            "created_at": (now - timedelta(days=1, hours=2)).isoformat(),
        },
    ]

    # Agregamos más datos para varios locales
    for location_id in range(6, 16):
        reviews.append({
            "review_id": f"api-{location_id}001",
            "location_id": location_id,
            "rating": 4 if location_id % 2 == 0 else 5,
            "text": f"Reseña de prueba para el local {location_id}",
            "author": None if location_id % 3 == 0 else f"user{location_id}@mail.com",
            "created_at": (now - timedelta(days=location_id % 7)).isoformat(),
        })

    return reviews