
TicketHub

TicketHub je middleware REST servis koji prikuplja i izlaže support tickete iz vanjskih izvora. Izgrađen s FastAPI-jem, pruža moderan, asinkron API za upravljanje ticketima s automatskom OpenAPI dokumentacijom.
Značajke

    🎫 Upravljanje ticketima: Dohvaćanje, filtriranje i pretraživanje ticketa iz vanjskih izvora

    🔍 Napredno filtriranje: Filtriranje po statusu, prioritetu i pretraživanje po naslovu

    📊 Statistike: Agregirane statistike ticketa

    🚀 Visoke performanse: Async/await s httpx-om za optimalne performanse

    📝 Automatska dokumentacija: Interaktivna OpenAPI/Swagger dokumentacija

    🐳 Docker spreman: Potpuna Docker Compose konfiguracija s Redisom

    ✅ Dobro testiran: Opsežni jedinični i integracijski testovi

    🔧 Developer-friendly: Potpuna razvojna konfiguracija s lintingom, formatiranjem i CI/CD-om

Tehnološki stack

    Python 3.11 s modernim typingom i async/await

    FastAPI 0.111 za REST API s automatskom OpenAPI dokumentacijom

    httpx 0.27 za pozive vanjskih API-ja

    Pydantic 2.7 za validaciju i serijalizaciju podataka

    pytest za testiranje

    Redis za caching (opcionalno)

    Docker & Docker Compose za kontejnerizaciju

Brza konfiguracija

Preduvjeti

    Python 3.11+

    pip

    Docker & Docker Compose (opcionalno)

Razvojno okruženje

    Kloniraj repozitorij

git clone <repository-url>
cd tickethub

Postavi razvojno okruženje

make dev-setup

Pokreni razvojni server

    make run

    Posjeti API dokumentaciju

        Swagger UI: http://localhost:8000/docs

        ReDoc: http://localhost:8000/redoc

        Health Check: http://localhost:8000/health

Korištenje Dockera

    Pokreni s Docker Compose

make docker-run

Zaustavi servise

    make docker-stop

API endpointovi
Osnovni endpointovi

    GET /tickets – Dohvati paginiranu listu ticketa s opcionalnim filtriranjem

    GET /tickets/{id} – Dohvati detaljne informacije o ticketu

    GET /tickets/search?q={query} – Pretraži tickete po naslovu

    GET /stats – Dohvati statistike ticketa

    GET /health – Health check endpoint

Query parametri
/tickets endpoint:

    page (int): Broj stranice (počinje od 1, default: 1)

    limit (int): Broj stavki po stranici (1–100, default: 10)

    status (str): Filtriraj po statusu (“open” ili “closed”)

    priority (str): Filtriraj po prioritetu (“low”, “medium” ili “high”)

/tickets/search endpoint:

    q (str): Upit za pretraživanje (obavezan)

    page (int): Broj stranice (počinje od 1, default: 1)

    limit (int): Broj stavki po stranici (1–100, default: 10)

Primjeri zahtjeva

# Dohvati prvu stranicu ticketa
curl "http://localhost:8000/tickets?page=1&limit=10"

# Filtriraj po statusu i prioritetu
curl "http://localhost:8000/tickets?status=open&priority=high"

# Pretraži tickete
curl "http://localhost:8000/tickets/search?q=important"

# Dohvati detalje ticketa
curl "http://localhost:8000/tickets/1"

# Dohvati statistike
curl "http://localhost:8000/stats"

Model podataka

Ticketi se transformiraju iz vanjskog DummyJSON API-ja prema sljedećem mapiranju:

{
    "id": int,                    # Direktno iz vanjskog API-ja
    "title": str,                 # Iz "todo" polja
    "status": str,                # "closed" ako je completed=true, inače "open"
    "priority": str,              # Izračunato: id % 3 → low/medium/high
    "assignee": str,              # Korisničko ime iz users API-ja preko userId
    "description": str            # Skraćeni naslov (≤100 znakova)
}

Razvoj
Dostupne naredbe

make help              # Prikaži sve dostupne naredbe
make install           # Instaliraj produkcijske ovisnosti
make install-dev       # Instaliraj razvojne ovisnosti
make run               # Pokreni razvojni server
make test              # Pokreni sve testove s coverageom
make test-unit         # Pokreni samo jedinične testove
make test-integration  # Pokreni samo integracijske testove
make lint              # Pokreni linting (flake8, mypy)
make format            # Formatiraj kod s blackom
make check             # Pokreni sve provjere (lint + test)
make docker-build      # Izgradi Docker image
make docker-run        # Pokreni s Docker Compose
make clean             # Očisti cache datoteke

Struktura projekta

tickethub/
├── src/tickethub/          # Aplikacijski source kod
│   ├── __init__.py
│   ├── main.py             # FastAPI aplikacija
│   ├── models.py           # Pydantic modeli
│   └── services.py         # Servis vanjskog API-ja
├── tests/                  # Test suite
│   ├── test_main.py        # Testovi API endpointova
│   ├── test_models.py      # Testovi validacije modela
│   └── test_services.py    # Testovi servis sloja
├── ci/                     # CI/CD konfiguracija
│   └── github-workflow.yml # GitHub Actions workflow
├── Dockerfile              # Docker image konfiguracija
├── docker-compose.yml      # Multi-service setup
├── Makefile                # Razvojne naredbe
├── requirements.txt        # Produkcijske ovisnosti
├── requirements-dev.txt    # Razvojne ovisnosti
├── pytest.ini              # Test konfiguracija
├── pyproject.toml          # Tool konfiguracija
├── .flake8                 # Linting konfiguracija
└── README.md               # Dokumentacija

Kvaliteta koda

Projekt održava visoke standarde kvalitete koda:

    Type hints: Potpune type anotacije koristeći Python 3.11+ typing

    Linting: flake8 za stil koda

    Type checking: mypy za statičku analizu tipova

    Formatiranje: black za konzistentno formatiranje koda

    Testiranje: pytest s async podrškom i coverage izvještajima

Varijable okruženja

# Opcionalna Redis konfiguracija
REDIS_URL=redis://localhost:6379

# Postavke vanjskog API-ja (default: DummyJSON)
EXTERNAL_API_BASE_URL=https://dummyjson.com

Vanjski izvor podataka

TicketHub se trenutno integrira s DummyJSON REST API-jem:

    Ticketi: https://dummyjson.com/todos

    Korisnici: https://dummyjson.com/users

Servis automatski dohvaća i cacheira korisničke informacije radi razrješavanja imena assigneeja.
Testiranje

Pokreni test suite:

# Svi testovi s coverageom
make test

# Samo jedinični testovi
make test-unit

# Samo integracijski testovi
make test-integration

Test coverage uključuje:

    Validaciju i serijalizaciju modela

    Servis sloj s mockanim vanjskim API-jima

    API endpointove s različitim scenarijima

    Error handling i granične slučajeve

Deployment
Docker deployment

    Izgradi i pokreni s Docker Compose

docker-compose up --build

Produkcijski deployment

    docker build -t tickethub:latest .
    docker run -p 8000:8000 tickethub:latest

Manualni deployment

    Instaliraj ovisnosti

pip install -r requirements.txt

Pokreni s Uvicornom

    uvicorn src.tickethub.main:app --host 0.0.0.0 --port 8000

CI/CD


