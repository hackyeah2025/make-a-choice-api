import os

import requests
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from openai import OpenAI
from pydantic import BaseModel
from schema import CoreEventCreate, EventCreate, EventResponse, Option, Stats

from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

session = requests.Session()
session.headers.update(
    {
        "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
        "Content-Type": "application/json",
    }
)

app = FastAPI()

origins = [
    "http://localhost:3000",
    # You can also use "*" to allow all origins, but not recommended in production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # or ["*"] for all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


SYSTEM_PROMPT = """
You are an assistant that generates a JSON event for a choice-based game.

YOU MUST RETURN CONTENT IN POLISH LANGUAGE.

You receive: 
- a list of options with their consequences (add or subtract from the stats).
- a list of stats.

You must return a JSON object with exactly these fields:
- "title": A string describing the event/scenario
- "text": A string describing the situation and context of the event
- "options": An array of strings, where each string is a choice the player can make

"text" should be interesting and engaging. Be concise and to the point.

Example format:
{
  "title": "Nieoczekiwane spotkanie na rynku",
  "text": "Podczas codziennych zakupów na zatłoczonym rynku zauważasz, że ktoś upuścił portfel pełen pieniędzy. Wokół Ciebie przechadzają się różni ludzie, a właściciel portfela wydaje się być nieobecny. Zastanawiasz się, co zrobić w tej sytuacji. Możesz oddać portfel strażnikowi miejskimu, spróbować odnaleźć właściciela samodzielnie, zatrzymać portfel dla siebie lub po prostu odejść, udając, że nic nie widziałeś.",
  "options": [
    "Oddaj portfel strażnikowi miejskiemu",
    "Spróbuj odnaleźć właściciela samodzielnie",
    "Zatrzymaj portfel dla siebie",
    "Odejdź, udając, że nic nie widziałeś"
  ]
}
"""


# core task
# base task


def generate_event_response(event: EventCreate, model: BaseModel, prompt: str):
    response = session.post(
        f"{os.getenv('OPENROUTER_API_URL')}/chat/completions",
        json={
            "model": "google/gemini-2.5-flash-preview-09-2025",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "response_format": {
                "type": "json_object",
                "json_schema": model.model_json_schema(),
            },
        },
    )
    if response.status_code == 200:
        result = response.json()
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "{}")
        return EventResponse.model_validate_json(content)
    else:
        raise Exception(
            f"API call failed with status {response.status_code}: {response.text}"
        )


def get_base_prompt(stats: Stats, options: list[Option]):
    return f"Generate an event text for the following stats: {stats}. The event should have the following options consequences (add or subtract from the stats): {options}. The number of options should be {len(options)}. The options order should match the order of the options in the list."


@app.post("/generate-event", response_model=EventResponse)
def generate_event(event: EventCreate):
    prompt = f"{get_base_prompt(event.stats, event.options)} The event should be in the following category: {event.category}"
    return generate_event_response(event, EventResponse, prompt)


@app.post("/generate-core-event", response_model=EventResponse)
def generate_core_event(event: CoreEventCreate):
    prompt = f"{event.prompt} {get_base_prompt(event.stats, event.options)}"
    return generate_event_response(event, EventResponse, prompt)
