import requests
import argparse
from datetime import datetime, timezone, timedelta
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from pydantic import Field
from pydantic_settings import BaseSettings


# Configuração via arquivo .env
class Settings(BaseSettings):
    TRELLO_API_KEY: str = Field(..., description="Chave da API do Trello")
    TRELLO_TOKEN: str = Field(..., description="Token de autenticação do Trello")
    TRELLO_BOARD_ID: str = Field(..., description="ID do quadro do Trello")
    GOOGLE_CALENDAR_ID: str = Field("primary", description="ID do Google Calendar")

    class Config:
        env_file = ".env"


settings = Settings()

# Configurações do Google Calendar
SCOPES = ["https://www.googleapis.com/auth/calendar"]
BRL_TIME_ZONE = timezone(timedelta(hours=-3))


def autenticar_google():
    creds = Credentials.from_service_account_file(
        "./src/credentials.json", scopes=SCOPES
    )
    return build("calendar", "v3", credentials=creds)


def obter_cards_trello():
    url = f"https://api.trello.com/1/boards/{settings.TRELLO_BOARD_ID}/lists"
    params = {"key": settings.TRELLO_API_KEY, "token": settings.TRELLO_TOKEN}
    response = requests.get(url, params=params)
    lists = response.json()
    cards = []
    for lista in lists:
        if lista["name"] in ["A Fazer", "Em andamento"]:
            url_cards = f"https://api.trello.com/1/lists/{lista['id']}/cards"
            response_cards = requests.get(url_cards, params=params)
            cards.extend(response_cards.json())
    return cards


def proxima_segunda():
    hoje = datetime.today()
    dias_ate_segunda = (7 - hoje.weekday()) % 7 or 7
    return hoje + timedelta(days=dias_ate_segunda)


def inicio_semana(data_base):
    return data_base - timedelta(days=data_base.weekday())


def fim_semana(data_base):
    return inicio_semana(data_base) + timedelta(
        days=6, hours=23, minutes=59, seconds=59
    )


def evento_existe(service, titulo, data_inicial, data_final):
    eventos = (
        service.events()
        .list(
            calendarId=settings.GOOGLE_CALENDAR_ID,
            timeMin=data_inicial.isoformat() + "Z",
            timeMax=data_final.isoformat() + "Z",
            q=titulo,
            singleEvents=True,
        )
        .execute()
        .get("items", [])
    )
    return any(evento["summary"] == titulo for evento in eventos)


def criar_evento_google(service, card, data_evento):
    start_time = data_evento.replace(hour=8, minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(hours=1)
    evento = {
        "summary": card["name"],
        "description": card.get("desc", ""),
        "start": {
            "dateTime": start_time.isoformat() + "Z",
            "timeZone": "America/Sao_Paulo",
        },
        "end": {
            "dateTime": end_time.isoformat() + "Z",
            "timeZone": "America/Sao_Paulo",
        },
    }
    service.events().insert(
        calendarId=settings.GOOGLE_CALENDAR_ID, body=evento
    ).execute()


def main():
    parser = argparse.ArgumentParser(
        description="Sync Trello cards with Google Calendar"
    )
    parser.add_argument(
        "--target",
        choices=["monday", "today"],
        default="today",
        help="Escolha 'today' para criar eventos para hoje ou 'monday' para a próxima segunda-feira.",
    )
    args = parser.parse_args()

    service = autenticar_google()
    cards = obter_cards_trello()

    if args.target == "today":
        data_evento = datetime.today()
        inicio_periodo = inicio_semana(data_evento).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        fim_periodo = fim_semana(data_evento)
    elif args.target == "monday":
        data_evento = proxima_segunda()
        inicio_periodo = data_evento.replace(hour=0, minute=0, second=0, microsecond=0)
        fim_periodo = inicio_periodo + timedelta(
            days=6, hours=23, minutes=59, seconds=59
        )
    else:
        return

    for card in cards:
        if card["name"].startswith("#"):
            continue
        if not evento_existe(service, card["name"], inicio_periodo, fim_periodo):
            criar_evento_google(service, card, data_evento)
    print("✅ Eventos criados com sucesso!")


if __name__ == "__main__":
    main()
