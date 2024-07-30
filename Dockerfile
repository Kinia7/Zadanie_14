# Użyj oficjalnego obrazu Python jako obrazu bazowego
FROM python:3.8-slim

# Ustaw zmienną środowiskową, aby `python` oraz `pip` nie używały buforowania
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# Ustaw katalog roboczy
WORKDIR /app

# Skopiuj plik requirements.txt i zainstaluj zależności
COPY requirements.txt .
RUN pip install -r requirements.txt

# Skopiuj pozostałe pliki aplikacji
COPY . .

# Ustaw punkt wejścia do aplikacji
CMD ["python", "run.py"]
