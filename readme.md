# PricingHub 🚀

PricingHub is a robust, containerized web scraping and data pipeline backend built for automated price tracking and data analytics. It extracts pricing data using modern automation tools, persists it reliably via SQLite volumes, and serves it through a high-performance FastAPI backend.

## 📊 Project Metrics

* **Total Products Tracked:** 3
* **Total Price Records:** 10
* **Average Scrape Duration:** ~3.5s per run

## 🏗️ Architecture & Tech Stack

* **Backend:** FastAPI (Python 3.11)
* **Web Scraping & Automation:** Playwright (Chromium)
* **Database & ORM:** SQLite & SQLAlchemy
* **Data Processing:** Pandas
* **Containerization:** Docker & Docker Compose (with volume persistence)

## ⚙️ How to Run

1. Clone the repository and navigate to the project directory.
2. Build and run the containers using Docker Compose:
   ```bash
   docker compose up -d --build

## Access the interactive API documentation (Swagger UI):
 http://localhost:8000/docs

## Project Structure

pricinghub/
│
├── app/
│   ├── main.py          # FastAPI application entrypoint
│   ├── models.py        # SQLAlchemy database models
│   ├── schemas.py       # Pydantic validation schemas
│   └── ...
├── data/                # Persistent SQLite database storage (Docker Volume)
├── scripts/             # Automated scraping scripts (scrape_all.py, etc.)
├── Dockerfile           # Container build configuration
├── docker-compose.yml   # Multi-container orchestration & volume mapping
└── requirements.txt     # Python dependencies