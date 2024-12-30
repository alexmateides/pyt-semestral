# BI-PYT semestrální práce

### Alexander Mateides

---

### [DOCS](https://pyt-semestral-docs.mateides.com)

---

## Instalace a spuštění

#### 1. Naklonování repozitáře

```shell
cd ~
git clone https://github.com/alexmateides/pyt-semestral
```

#### 2. Konfigurace serveru (přes .env)

```shell
cd ~/pyt-semestral/backend
nano .env
```

Vložte a doplňte následující šablonu:

```dotenv
API_KEY="TEST"
FRONTEND_URL="http://localhost:3000"
SENDER_EMAIL="abc@def.ghi"
SENDER_PASSWORD="...."
SENDER_SMTP_HOST="smtp.def.ghi"
RECEIVER_EMAIL="qrs@uvw.xyz"
```

PS: následující postup očekává `API_KEY="TEST"` a `FRONTEND_URL="http://localhost:3000"`

#### 3. Vytvoření docker images (je nutno mít docker)

```shell
cd ~/pyt-semestral
docker build -t pyt-semestral-backend ./backend
docker build -t pyt-semestral-frontend ./frontend
```

#### 4. Vytvoření a spuštění docker containers

```shell    
docker run -d -p 8000:8000 --name pyt-semestral-backend-container pyt-semestral-backend:latest
docker run -d -p 3000:3000 --name pyt-semestral-frontend-container pyt-semestral-frontend:latest
```

#### 4.1 Kontrola containers

```shell
docker ps
```

Nyní se lze připojit přes na frontend (localhost:3000) nebo provolat backend (localhost:8000).
Při provolávání backendu pochopitelně budou fungovat pouze endpointy, které nepotřebují fyzickou kameru.
Tj. /alive a /camera. Uživatel si tedy může vyzkoušet přidat do interní databáze kamery, popřípadě vyvolat jejich
informace.

---

## Testy a Linter

---

### Spuštění pytest a pylint

#### 1. Připojení se na docker container

```shell
docker exec -it pyt-semestral-backend-container /bin/bash
```

#### 2. Spuštění testů (je důležité python -m kvůli absolutním importům)

```shell
python -m pytest
```

#### 3. Spuštění linteru (zase důležité použití python -m)

```shell
python -m pylint --disable=C0301,C0103 app/
```

---

### Poznámky k testům

Testy zdánlivě ukazují poměrně malou test coverage. To je hlavně ze dvou důvodů

1. Pro testování FastAPI endpointů používám FastAPI TestClient, který přímo nevolá funkce endpointů, ale spustí aplikaci a endpointy potom provolává.
Pytest toto zřejmě nedetekuje, neboť jak lze vidět v backend/tests/api, tak endpointy jsou testovány všechny

2. Některé funkce, které přímo interagují s Tapo kamerou se špatně testují (například simulace posílání videí a vysílání rtsp streamu), tyto testy, které by vyžadovaly
velmi složité mocky jsem vynechal.

---

### Poznámky k linteru

> app/main.py:69:11: W0718: Catching too general exception Exception (broad-exception-caught)

- Pro FastAPI (a víceméně všechny ostatní serverové aplikace) je best-practice mít jeden middleware, který případně odchytí libovolnou 
nezachycenou exception, čímž předejdeme pádu serveru. Exception je potom patřičně zalogována jako CRITICAL

>   app/camera/tapo_320ws/video_stream.py:21:32: E1101: Module 'cv2' has no 'VideoCapture' member (no-member)

- Nějaký issue s opencv2, podobný jsem měl v úkolu, tam ale prošel přes testy v pipeline. Některé zdroje na internetu (zejména StackOverflow)
radily `from cv2 import cv2`, ovšem toto mi nepomohlo

> Module backend.app.camera.tapo_320ws.download

- Celý modul download je transplantace experimenální části knihovny [pytapo](https://github.com/JurajNyiri/pytapo/tree/main/pytapo), kterou jsem potom ještě upravoval 
(protože nespolupracovala s mým modelem kamery). Většina knihovny je napsána dost 'punkově', což potom vede k PEP-8 chybám.  

