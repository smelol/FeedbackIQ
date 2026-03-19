import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def extract_json_text(text: str) -> str:
    text = text.strip()

    if text.startswith("```"):
        lines = text.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines).strip()

    return text


def generate_text(prompt: str) -> str:
    response = client.responses.create(
        model="gpt-4o-mini",
        input=prompt,
    )

    return response.output[0].content[0].text.strip()


def analyze_text(prompt: str) -> dict:
    text = generate_text(prompt)
    cleaned_text = extract_json_text(text)

    try:
        return json.loads(cleaned_text)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Respuesta no es JSON válido.\n"
            f"Texto original:\n{text}\n\n"
            f"Texto limpiado:\n{cleaned_text}"
        ) from exc