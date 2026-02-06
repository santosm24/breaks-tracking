#!/usr/bin/env python3
import asyncio
import logging
import random
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

from jeepney import DBusAddress, new_method_call
from jeepney.io.asyncio import open_dbus_connection

# -------- PARAMETERS --------
if len(sys.argv) != 6:
    sys.exit(
        "Usage: breaks_tracker.py <notify_every> <short_every> <long_every> <interval_min> <long_time>"
    )

HYDRATION_REMINDER = int(sys.argv[1])
SHORT_EVERY = int(sys.argv[2])
LONG_EVERY = int(sys.argv[3])
INTERVAL_MIN = int(sys.argv[4])
LONG_BREAK_TIME = int(sys.argv[5])

# -------- CONSTANTS --------
LOG_DIR = Path.home() / ".local" / "share" / "breaks_tracker"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG = LOG_DIR / "online_time.log"
logging.basicConfig(
    filename=LOG, level=logging.INFO, format="%(asctime)s - %(message)s"
)

SHORT_BREAK_MESSAGES = [
    "👀 Ei, piscaste hoje? Olha para longe durante 20 segundos.",
    "🧍‍♂️ Micro-pausa oficial: levanta-te antes de criares raízes.",
    "🧠 O cérebro pediu folga. Volta já.",
    "⌛ 20 segundinhos agora para não fritares mais tarde.",
    "😵 Olhos em modo grelhador? Pausa rápida!",
    "⚡ Para, respira, continua como um campeão.",
]

LONG_BREAK_MESSAGES = [
    "🛋️ Pausa longa: sim, podes abandonar o ecrã. Ele sobrevive.",
    "🚶 Vai esticar as pernas. O código não foge.",
    "🌍 Mundo real chamou. Volta daqui a pouco.",
]

HYDRATION_REMINDER_MESSAGES = [
    "💧 Águaaaa! O teu corpo não é um cacto.",
    "🚰 Bebe água antes que o cérebro seque.",
    "💦 Hidrata-te. Café não conta.",
]

# Global State
state = {
    "minutes": 0,
    "suspend_start": None,
    "last_check": time.time(),
    "today": datetime.now().strftime("%Y-%m-%d"),
}

queue = asyncio.Queue()


def notify(msg, type_str, level="normal"):
    logging.info(f"Notifying: {msg}")
    subprocess.Popen(
        [
            "notify-send",
            "-u",
            level,
            f"⏱ {type_str}",
            msg,
            "--hint=string:sound-name:message-new-instant",
        ]
    )


async def monitor_session_bus():
    """Polls GNOME Screen Lock state"""
    global state
    try:
        conn = await open_dbus_connection(bus="SESSION")
        logging.info("Session bus monitor started (polling mode)")

        was_locked = False

        while True:
            try:
                # Poll screen lock status via DBus call with timeout
                msg = new_method_call(
                    DBusAddress(
                        "/org/gnome/ScreenSaver",
                        bus_name="org.gnome.ScreenSaver",
                        interface="org.gnome.ScreenSaver",
                    ),
                    "GetActive",
                )
                await conn.send(msg)

                # Add timeout to prevent hanging
                try:
                    reply = await asyncio.wait_for(conn.receive(), timeout=5.0)
                except asyncio.TimeoutError:
                    logging.warning("D-Bus call timed out, retrying...")
                    await asyncio.sleep(5)
                    continue

                # Validate reply has expected data
                if not reply or not reply.body or len(reply.body) == 0:
                    await asyncio.sleep(2)
                    continue

                is_locked = reply.body[0]

                # Detect lock state change
                if is_locked and not was_locked:
                    logging.info("Screen locked - tracking pause started")
                    if state["suspend_start"] is None:
                        state["suspend_start"] = time.time()
                    was_locked = True
                elif not is_locked and was_locked:
                    logging.info("Screen unlocked")
                    process_resume()
                    was_locked = False

            except Exception as e:
                logging.error(f"Error checking lock state: {e}")

            await asyncio.sleep(60)  # Check every 60 seconds

    except Exception as e:
        logging.error(f"Fatal error in session bus monitor: {e}")
        raise


def process_resume():
    global state
    global queue
    if state["suspend_start"]:
        away_seconds = time.time() - state["suspend_start"]
        away_minutes = int(away_seconds // 60)

        if away_minutes >= LONG_BREAK_TIME:
            state["minutes"] = 0
            logging.info(f"Break detected: {away_minutes} min. Timer reset.")
        else:
            elapsed_minutes = int((state["suspend_start"] - state["last_check"]) // 60)
            state["minutes"] += elapsed_minutes
            logging.info(f"Resumed after {away_minutes} min. No reset.")
        queue.put_nowait("resume")
        state["suspend_start"] = None


async def tracker_loop():
    global state
    global queue
    while True:
        await asyncio.sleep(INTERVAL_MIN * 60)
        now_date = datetime.now().strftime("%Y-%m-%d")
        if state["today"] != now_date:
            state["minutes"] = 0
            state["today"] = now_date

        if state["suspend_start"]:
            await queue.get()  # Wait for resume signal
        else:
            state["minutes"] += INTERVAL_MIN
        m = state["minutes"]
        state["last_check"] = time.time()

        if m % (HYDRATION_REMINDER * LONG_EVERY) == 0:
            message = random.choice(LONG_BREAK_MESSAGES)
            notify(message, "Long Break", "critical")
        elif m % (HYDRATION_REMINDER * SHORT_EVERY) == 0:
            message = random.choice(SHORT_BREAK_MESSAGES)
            notify(message, "Short Break")
        elif m % HYDRATION_REMINDER == 0:
            message = random.choice(HYDRATION_REMINDER_MESSAGES)
            notify(message, "Hidratação")


async def main():
    logging.info("Starting breaks tracker...")
    try:
        await asyncio.gather(monitor_session_bus(), tracker_loop())
    except Exception as e:
        logging.error(f"Fatal error in main: {e}")
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
