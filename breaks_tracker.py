#!/usr/bin/env python3
import logging
import os
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
# ----------------------------
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


def _pre_notifiy():
    # Detectar o DISPLAY e DBUS_SESSION_BUS_ADDRESS da sessão do utilizador
    if "DISPLAY" not in os.environ or "DBUS_SESSION_BUS_ADDRESS" not in os.environ:
        # Pega o PID do processo do GNOME do usuário
        try:
            user = subprocess.check_output("whoami", shell=True).decode().strip()
            # Procura um processo da sessão gráfica (ex: gnome-shell)
            pid = (
                subprocess.check_output(f"pgrep -u {user} gnome-shell", shell=True)
                .decode()
                .strip()
                .split("\n")[0]
            )
            env_file = f"/proc/{pid}/environ"
            with open(env_file, "rb") as f:
                env = f.read().decode().split("\0")
                for e in env:
                    if e.startswith("DISPLAY="):
                        os.environ["DISPLAY"] = e.split("=", 1)[1]
                    elif e.startswith("DBUS_SESSION_BUS_ADDRESS="):
                        os.environ["DBUS_SESSION_BUS_ADDRESS"] = e.split("=", 1)[1]
        except Exception as ex:
            logging.error("⚠️ Não foi possível detectar DISPLAY/DBUS:", ex)


def notify(msg):
    logging.info(f"Notifying: {msg}")
    _pre_notifiy()
    subprocess.Popen(["notify-send", "⏱ Tempo Online", msg])


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
last_date = today

if STATE.exists():
    last_date, minutes = STATE.read_text().split("|")
    minutes = int(minutes)

# RESET DIÁRIO
if last_date != today:
    minutes = 0
    logging.info(f"\n--- {today} ---\n")

# CONTAGEM
if is_unlocked():
    minutes += INTERVAL_MIN

    if minutes % (NOTIFY_EVERY * LONG_BREAK) == 0:
        message = random.choice(LONG_BREAK_MESSAGES)
        notify(message)
    elif minutes % NOTIFY_EVERY == 0:
        message = random.choice(SHORT_BREAK_MESSAGES)
        notify(message)
    else:
        time_to_notify = NOTIFY_EVERY - (minutes % NOTIFY_EVERY)
        logging.info(f"Next notification in {time_to_notify} minute(s).")

STATE.write_text(f"{today}|{minutes}")
