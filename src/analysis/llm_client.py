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


def analyze_text(prompt: str) -> dict:
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
    )

    text = response.output[0].content[0].text
    cleaned_text = extract_json_text(text)

    try:
        return json.loads(cleaned_text)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Respuesta no es JSON válido.\n"
            f"Texto original:\n{text}\n\n"
            f"Texto limpiado:\n{cleaned_text}"
        ) from exc