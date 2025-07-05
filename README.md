# TicketHub

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue?logo=python)]()
[![FastAPI](https://img.shields.io/badge/fastapi-0.111-green?logo=fastapi)]()
[![Tests](https://img.shields.io/github/actions/workflow/status/your-org/tickethub/ci.yml?branch=main)]()
[![Coverage](https://img.shields.io/codecov/c/github/your-org/tickethub/main)]()
[![License: MIT](https://img.shields.io/badge/license-MIT-lightgrey)]()

Middleware REST servis za objedinjeno upravljanje support ticketima iz različitih izvora.

---

## 📖 Sadržaj

- [Značajke](#-značajke)  
- [Tehnološki stack](#-tehnološki-stack)  
- [Brzi početak](#-brzi-početak)  
  - [Preduvjeti](#preduvjeti)  
  - [Lokalni razvoj](#lokalni-razvoj)  
  - [Docker](#docker)  
- [Konfiguracija](#-konfiguracija)  
- [API Reference](#api-reference)  
  - [Endpoints](#endpoints)  
  - [Query parametri](#query-parametri)  
  - [Primjeri](#primjeri)  
- [Model podataka](#-model-podataka)  
- [Testiranje](#-testiranje)  
- [Struktura projekta](#-struktura-projekta)  
- [Doprinos](#-doprinos)  
- [License](#-license)  

---

## 🎫 Značajke

- **Upravljanje ticketima**: dohvaćanje, filtriranje & pretraživanje iz vanjskih API-ja  
- **Napredno filtriranje**: prema statusu (`open`/`closed`), prioritetu (`low`/`medium`/`high`)  
- **Pretraživanje**: po naslovu ili punom tekstu  
- **Statistike**: agregirani podaci o broju i statusima ticketa  
- **Visoke performanse**: async/await + `httpx`  
- **OpenAPI & Swagger**: interaktivna dokumentacija out-of-the-box  
- **Docker & Redis**: spremno za kontejnerizaciju i caching  
- **CI/CD**: automatsko lintanje, formatiranje i testiranje  

---

## 🛠️ Tehnološki stack

- **Python** 3.11+ (modern typing, async)  
- **FastAPI** 0.111 (REST + OpenAPI)  
- **httpx** 0.27 (async HTTP klijent)  
- **Pydantic** 2.7 (modeli & validacija)  
- **pytest** (unit & integration)  
- **Redis** (opcionalni cache)  
- **Docker & Docker Compose**  

---

## 🚀 Brzi početak

### Preduvjeti

- Python 3.11+  
- `pip`  
- (opcionalno) Docker & Docker Compose  

### Lokalni razvoj

1. Kloniraj repozitorij  
   ```bash
   git clone https://github.com/your-org/tickethub.git
   cd tickethub

    Instaliraj ovisnosti

make install-dev

Pokreni razvojni server

    make run

    Otvori dokumentaciju:

        Swagger UI: http://localhost:8000/docs

        ReDoc: http://localhost:8000/redoc

        Health: http://localhost:8000/health

Docker

    Pokreni sve servise

make docker-run

Zaustavi servise

    make docker-stop

⚙️ Konfiguracija

Sve postavke preko env varijabli (zadane vrijednosti u zagradi):

# Redis (opcionalno)
REDIS_URL=redis://localhost:6379

# Vanjski API
EXTERNAL_API_BASE_URL=https://dummyjson.com

API Reference
Endpoints
Metoda	Putanja	Opis
GET	/tickets	Paginirana lista ticketa
GET	/tickets/{id}	Detalji ticketa
GET	/tickets/search	Pretraživanje ticketa (q query)
GET	/stats	Agregirane statistike ticketa
GET	/health	Health check
Query parametri
/tickets

    page (int, default=1) — broj stranice

    limit (int, default=10, 1–100) — stavki po stranici

    status (str) — open | closed

    priority (str) — low | medium | high

/tickets/search

    q (str, required) — upit za pretraživanje

    page, limit — kao iznad

Primjeri

# 1. Paginirani ticketi
curl "http://localhost:8000/tickets?page=1&limit=10"

# 2. Filtriraj po statusu i prioritetu
curl "http://localhost:8000/tickets?status=open&priority=high"

# 3. Pretraži tickete po naslovu
curl "http://localhost:8000/tickets/search?q=important"

# 4. Detalji ticketa ID=1
curl "http://localhost:8000/tickets/1"

# 5. Statistike
curl "http://localhost:8000/stats"

🗂️ Model podataka

Ticket iz DummpyJSON API-ja mapira se ovako:
Polje	Tip	Opis
id	int	originalni ID
title	str	iz polja todo
status	str	"closed" ako je completed=true, inače "open"
priority	str	izračunato: id % 3 → low/medium/high
assignee	str	korisničko ime (preko userId + /users endpoint)
description	str	skraćeni naslov (maks. 100 znakova)
✅ Testiranje

Sve testove pokreće pytest:

make test        # unit + integration + coverage
make test-unit   # samo unit testovi
make test-int    # samo integration testovi

Dodatne naredbe

make lint       # flake8, mypy
make format     # black
make check      # lint + test
make clean      # očisti cache

🏗️ Struktura projekta


tickethub/
├── src/
│   └── tickethub/
│       ├── main.py         # FastAPI app
│       ├── models.py       # Pydantic modeli
│       └── services.py     # HTTP klijent + business logic
├── tests/
│   ├── test_main.py
│   ├── test_models.py
│   └── test_services.py
├── ci/
│   └── workflow.yml         # CI/CD (GitHub Actions)
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── requirements.txt
├── requirements-dev.txt
├── pytest.ini
├── pyproject.toml
└── README.md


