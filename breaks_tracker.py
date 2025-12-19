#!/usr/bin/env python3
import logging
import random
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# -------- PARÂMETROS --------
if len(sys.argv) != 4:
    sys.exit(
        "Uso: breaks_tracker.py <notificar_a_cada_x_min> <long_break> <intervalo_minutos>"
    )

NOTIFY_EVERY = int(sys.argv[1])  # ex: 30
LONG_BREAK = int(sys.argv[2])  # ex: 3
INTERVAL_MIN = int(sys.argv[3])  # intervalo do timer em minutos
LONG_BREAK_TIME = int(sys.argv[4])  # duração do long break em minutos

# -------- CONSTANTES E VARIÁVEIS --------
LOG_DIR = Path.home() / ".local" / "share" / "breaks_tracker"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG = LOG_DIR / "online_time.log"
STATE = LOG_DIR / ".online_state"

SHORT_BREAK_MESSAGES = [
    "👀 Descanso para os olhos: olha para longe durante 20 segundos.",
    "🧍‍♂️ Micro-pausa: levanta-te, respira fundo e continua.",
    "💧 Hidratação: bebe um pouco de água antes de continuar.",
    "⌛ Reset rápido: pequena pausa agora = mais produtividade a seguir.",
]

LONG_BREAK_MESSAGES = [
    "🛋️ Pausa longa: hora de parar a sério. Afasta-te do ecrã.",
    "🚶 Movimento: dá uma pequena caminhada, o corpo precisa.",
]


def is_unlocked():
    try:
        user = subprocess.check_output("whoami", shell=True).decode().strip()
        session = (
            subprocess.check_output(
                f"loginctl | grep {user} | awk '{{print $1}}'", shell=True
            )
            .decode()
            .strip()
        )

        locked = (
            subprocess.check_output(
                f"loginctl show-session {session} -p LockedHint --value", shell=True
            )
            .decode()
            .strip()
        )

        return locked == "no"
    except:
        return False


def notify(msg, type, level="normal"):
    logging.info(f"Notifying: {msg}")
    subprocess.Popen(
        [
            "notify-send",
            "-u",
            level,
            f"⏱ {type}",
            msg,
            "--hint=string:sound-name:message-new-instant",
        ]
    )


# Configurar logging
logging.basicConfig(
    filename=LOG,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Estado: data|minutos
today = datetime.now().strftime("%Y-%m-%d")
minutes = 0
idle = 0
sequence_minutes = 0
last_date = today

if STATE.exists():
    last_date, minutes, sequence_minutes, idle = STATE.read_text().split("|")
    minutes = int(minutes)
    sequence_minutes = int(sequence_minutes)
    idle = int(idle)

# RESET DIÁRIO
if last_date != today:
    minutes = 0
    sequence_minutes = 0
    idle = 0
    logging.info(f"--- {today} ---")

# CONTAGEM
if is_unlocked():
    minutes += INTERVAL_MIN
    sequence_minutes += INTERVAL_MIN
    if minutes % (NOTIFY_EVERY * LONG_BREAK) == 0:
        message = random.choice(LONG_BREAK_MESSAGES)
        notify(message, "Long Break", "critical")
    elif minutes % NOTIFY_EVERY == 0:
        message = random.choice(SHORT_BREAK_MESSAGES)
        notify(message, "Short Break")
    else:
        time_to_notify = NOTIFY_EVERY - (minutes % NOTIFY_EVERY)
        logging.info(f"Next notification in {time_to_notify} minute(s).")
else:
    idle += INTERVAL_MIN
    logging.info(f"System is locked/idle. Idle time: {idle} minute(s).")
    if sequence_minutes != 0 and idle >= LONG_BREAK_TIME:
        sequence_minutes = 0
        logging.info("Idle time exceeded long break time. Resetting minutes counter.")
STATE.write_text(f"{today}|{minutes}|{sequence_minutes}|{idle}")
