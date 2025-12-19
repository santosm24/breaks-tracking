#!/bin/bash

set -e


# ===== DETECTAR PASTA DO SCRIPT =====
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ===== PARÂMETROS =====
NOTIFY_EVERY=${1:-30}                 # notificação a cada X minutos (padrão 30)
LONG_BREAK=${2:-3}                    # long break a cada X breaks (padrão 3)
INTERVAL_MIN=${3:-1}                 # intervalo do timer em minutos (padrão 1)
SERVICE_NAME="breaks-tracker"
SYSTEMD_DIR="$HOME/.config/systemd/user"
# =====================

PY_SCRIPT="$SCRIPT_DIR/breaks_tracker.py $NOTIFY_EVERY $LONG_BREAK $INTERVAL_MIN"

PY_SCRIPT_CMD="$PY_SCRIPT $NOTIFY_EVERY $LONG_BREAK $INTERVAL_MIN"

# Verificações básicas
if [ ! -f "$PY_SCRIPT" ]; then
  echo "❌ Script Python não encontrado em $PY_SCRIPT"
  exit 1
fi

# Linha do cron a ser adicionada
CRON_LINE="*/$INTERVAL_MIN * * * * DISPLAY=:0 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/\$(id -u)/bus /usr/bin/python3 $PY_SCRIPT_CMD"

# Verifica se a linha já existe no crontab
(crontab -l 2>/dev/null | grep -F "$PY_SCRIPT_CMD") && {
    echo "A tarefa já existe no crontab."
    exit 0
}

# Adiciona a linha ao crontab
(crontab -l 2>/dev/null; echo "$CRON_LINE") | crontab -

echo "✅ CONFIGURAÇÃO CONCLUÍDA"
echo "📊 Logs: ~/.local/share/breaks_tracker/online_time.log"
echo "🛑 Parar: crontab -l | grep -v \"$PY_SCRIPT\" | crontab -"
