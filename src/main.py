import os

import requests
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel
from requests.adapters import HTTPAdapter, Retry
from schema import (
    CoreEventCreate,
    EventCreate,
    EventResponse,
    EventResponseExtraField,
    Option,
    Stats,
    SummaryCreate,
)

load_dotenv()

session = requests.Session()
session.headers.update(
    {
        "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
        "Content-Type": "application/json",
    }
)
retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
adapter = HTTPAdapter(max_retries=retries)
session.mount("https://", adapter)

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

Stats description:
name - name of the player
age - age of the player

priorities - list of priorities of the player

health - health status of the player
relations - satisfaction with relationships
happiness - happiness of the player
money - satisfaction with money
income - income of the player
expenses - monthly expenses
savings - savings/money on hand of the player
ZUS - ZUS contributions
education - education level of the player
job_experience - job experience of the player in form of 1-100
job - current job of the player in form of "unemployed", "low_paid_job", "middle_paid_job", "high_paid_job"
job_name - name of the current job
has_serious_health_issues - true if the player has serious health issues
relationship - relationship status of the player
children - number of children of the player

"text" should be interesting and engaging. Be concise and to the point.
Don't make it longer than single sentence if this isn't necessary.

Example response:
{
  "title": "Nagła decyzja podczas codzienności",
  "text": "Wracając z pracy, zauważasz na chodniku portfel wypchany banknotami. Wokół przechodzą ludzie, a właściciela nie widać. Zastanawiasz się, jak postąpić w tej sytuacji. Czy oddać portfel odpowiednim służbom, poszukać właściciela na własną rękę, zatrzymać pieniądze dla siebie, czy po prostu odejść, jakby nic się nie stało?",
  "options": [
    "Oddaj portfel odpowiednim służbom",
    "Spróbuj samodzielnie znaleźć właściciela",
    "Zatrzymaj portfel dla siebie",
    "Odejdź, ignorując sytuację"
  ]
}
"""

SUMMARY_SYSTEM_PROMPT = """
You are an assistant that generates a life summary for a choice-based game.

YOU MUST RETURN CONTENT IN POLISH LANGUAGE.

You receive:
- final stats of the player
- history of all events and choices made
- is_retired flag indicating if the player reached retirement age (65+)

You must return a JSON object with exactly this field:
- "summary": A string describing the player's life story, achievements, and final outcome

The summary should:
- Be written in Polish language
- Tell the story of the player's life based on their choices
- Highlight key achievements and failures
- Mention the final stats and their impact on the player's life
- If is_retired is true, focus on a successful retirement
- If is_retired is false, explain why the player didn't reach retirement successfully
- Be engaging and narrative, like a life story
- Be concise but comprehensive (2-4 paragraphs)

Example response:
{
  "summary": "Twoje życie było pełne wyzwań i ważnych decyzji. Zaczynając jako młody dorosły, udało Ci się zbudować stabilną karierę zawodową i założyć rodzinę. Twoje wybory doprowadziły Cię do emerytury w wieku 65 lat z solidnymi oszczędnościami i dobrym zdrowiem. Przez lata dbałeś o relacje z bliskimi i rozwijałeś swoje umiejętności zawodowe. Twoja emerytura to zasłużony odpoczynek po latach ciężkiej pracy i mądrych decyzji."
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
        return model.model_validate_json(content)
    else:
        raise Exception(
            f"API call failed with status {response.status_code}: {response.text}"
        )


def get_base_prompt(stats: Stats, options: list[Option]):
    return f"Generate an event text for the following stats: {stats}. The event should have the following options consequences (add or subtract from the stats): {options}. The number of options should be {len(options)}. The options order should match the order of the options in the list."


@app.post("/generate-event", response_model=EventResponseExtraField)
def generate_event(event: EventCreate):
    prompt = f"{get_base_prompt(event.stats, event.options)} The event should be in the following category: {event.category}"
    return EventResponseExtraField.from_event_response(
        generate_event_response(event, EventResponse, prompt)
    )


@app.post("/generate-core-event", response_model=EventResponseExtraField)
def generate_core_event(event: CoreEventCreate):
    prompt = f"{event.prompt} {get_base_prompt(event.stats, event.options)}"

    if event.extra_field:
        prompt = f"{event.prompt} You must output extra_field with corresponding {event.extra_field}. {get_base_prompt(event.stats, event.options)}"

        return generate_event_response(event, EventResponseExtraField, prompt)
    resp = EventResponseExtraField.from_event_response(
        generate_event_response(event, EventResponse, prompt)
    )
    print(resp)
    return resp


@app.post("/generate-summary")
def generate_summary(summary_data: SummaryCreate):
    history_text = ""
    for i, state in enumerate(summary_data.history):
        history_text += (
            f"\nWydarzenie {i+1}: {state.event.get('title', 'Brak tytułu')}\n"
        )
        history_text += f"Opis: {state.event.get('text', 'Brak opisu')}\n"
        history_text += f"Wybór: {state.choice.get('text', 'Brak wyboru')}\n"
        history_text += f"Statystyki po wyborze: {state.stats}\n"

    prompt = f"""
Wygeneruj podsumowanie życia gracza na podstawie następujących informacji:

Finalne statystyki: {summary_data.stats}
Czy gracz przeszedł na emeryturę: {'Tak' if summary_data.is_retired else 'Nie'}

Historia wydarzeń i wyborów:
{history_text}

Wygeneruj podsumowanie życia gracza w języku polskim.
"""

    response = session.post(
        f"{os.getenv('OPENROUTER_API_URL')}/chat/completions",
        json={
            "model": "google/gemini-2.5-flash-preview-09-2025",
            "messages": [
                {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "response_format": {
                "type": "json_object",
                "json_schema": {
                    "type": "object",
                    "properties": {"summary": {"type": "string"}},
                    "required": ["summary"],
                },
            },
        },
    )

    if response.status_code == 200:
        result = response.json()
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "{}")
        import json

        parsed_content = json.loads(content)
        return parsed_content.get("summary", "Nie udało się wygenerować podsumowania.")
    else:
        raise Exception(
            f"API call failed with status {response.status_code}: {response.text}"
        )
