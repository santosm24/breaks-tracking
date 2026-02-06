# Breaks Tracker 🕐💧

Sistema inteligente de rastreamento de tempo online com notificações automáticas para pausas, hidratação e saúde ocular.

**Compatibilidade:** Linux (GNOME/sistemas com DBus)  
**Tecnologias:** Python 3, asyncio, jeepney, systemd

## ✨ Funcionalidades

- ⏱️ Rastreamento contínuo do tempo online
- 💧 Lembretes periódicos de hidratação
- 👀 Pausas curtas para descanso dos olhos
- 🚶 Pausas longas para movimento
- 🔒 Detecção automática de bloqueio de ecrã (via DBus)
- 📊 Logging de atividade em `~/.local/share/breaks_tracker/online_time.log`
- 🔄 Reset automático após pausas longas
- 🎯 Notificações inteligentes via `notify-send`

## 📂 Estrutura

```
/pasta-do-script/
├── breaks_tracker.py           # Script principal (daemon)
├── install_autostart.sh        # Instalador para autostart
├── breaks_tracker.service      # Systemd service file
├── setup_breaks_tracker.sh     # Setup alternativo (timer)
└── README.md
```

- `breaks_tracker.py` → daemon Python que monitora tempo e envia notificações  
- `install_autostart.sh` → script para configurar autostart com systemd  
- `breaks_tracker.service` → service file do systemd

---

## 📦 Dependências

```bash
pip install -r requirements.txt
```

---

## ⚙️ Instalação Rápida (Autostart)

**Método recomendado** - o script roda automaticamente ao iniciar o PC:

```bash
chmod +x install_autostart.sh
./install_autostart.sh
```

Isso irá:
1. Copiar o service para `~/.config/systemd/user/`
2. Ativar o serviço para iniciar automaticamente
3. Iniciar o serviço imediatamente

### Parâmetros do Script

O script aceita 5 parâmetros obrigatórios:

```
breaks_tracker.py <notify_every> <short_every> <long_every> <interval_min> <long_time>
```

| Parâmetro    | Descrição                                         | Exemplo |
| ------------ | ------------------------------------------------- | ------- |
| notify_every | Intervalo base para lembretes de hidratação (min) | 1       |
| short_every  | Short break a cada X lembretes de hidratação      | 2       |
| long_every   | Long break a cada X lembretes de hidratação       | 8       |
| interval_min | Intervalo de verificação do timer (min)           | 15      |
| long_time    | Tempo mínimo de ausência para reset do timer (min)| 30      |

**Exemplo de configuração padrão no service:**

```bash
ExecStart=/usr/bin/python3 /path/to/breaks_tracker.py 1 2 8 15 30
```

Isso significa:
- 💧 Hidratação a cada 15 min  (15 * 1)
- 👀 Short break a cada 30 min (15 × 2)
- 🚶 Long break a cada 120 min (15 × 8)
- Verifica estado a cada 15 min
- Ausências ≥30 min resetam o timer

---

## � Personalização

### Alterar Parâmetros

Edita o arquivo de serviço:

```bash
nano ~/.config/systemd/user/breaks_tracker.service
```

Altera a linha `ExecStart` com os parâmetros desejados, depois:

```bash
systemctl --user daemon-reload
systemctl --user restart breaks_tracker
```

### Alterar Mensagens

Edita o `breaks_tracker.py` nas listas:

```python
SHORT_BREAK_MESSAGES = [
    "👀 Descanso para os olhos: olha para longe durante 20 segundos.",
    "🧍‍♂️ Micro-pausa: levanta-te, respira fundo e continua.",
    # ... adiciona mais mensagens
]

LONG_BREAK_MESSAGES = [
    "🛋️ Pausa longa: hora de parar a sério. Afasta-te do ecrã.",
    # ... adiciona mais mensagens
]
```

Depois reinicia o serviço:

```bash
systemctl --user restart breaks_tracker
```

---

## 🔍 Gestão do Serviço

### Ver Status

```bash
systemctl --user status breaks_tracker
```

### Ver Logs em Tempo Real

```bash
journalctl --user -u breaks_tracker -f
```

### Ver Histórico de Atividade

```bash
cat ~/.local/share/breaks_tracker/online_time.log
```

### Parar Serviço

```bash
systemctl --user stop breaks_tracker
```

### Iniciar Serviço

```bash
systemctl --user start breaks_tracker
```

### Reiniciar Serviço

```bash
systemctl --user restart breaks_tracker
```

### Desinstalar (Desativar Autostart)

```bash
systemctl --user disable breaks_tracker
systemctl --user stop breaks_tracker
rm ~/.config/systemd/user/breaks_tracker.service
systemctl --user daemon-reload
```

---

## 📊 Logs

* Local: mesmo diretório do Python script
* Arquivo: `online_time.log`
* Contém linhas como:

```
2025-12-18 14:05:00 ONLINE
2025-12-18 14:10:00 ONLINE
```

* Reset diário automático é feito pelo script

---

## 💡 Dicas

* Para alterar mensagens de short/long break, edita diretamente o Python script nas listas:

```python
SHORT_BREAK_MESSAGES = [ ... ]
LONG_BREAK_MESSAGES = [ ... ]
```

* Para intervalos diferentes de timer, use o parâmetro `INTERVAL_MIN` ao executar `setup_breaks_tracker.sh`.

