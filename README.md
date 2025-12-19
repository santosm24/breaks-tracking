# Online Tracker

Um script para rastrear o tempo que passas online no Ubuntu, com notificações de pausas curtas e longas.  

Funciona com **Python 3** e **systemd user timer**.  



## 📂 Estrutura

```
/pasta-do-script/
├── breaks_tracker.py
├── setup_breaks_tracker.sh
└── README.md
```

- `breaks_tracker.py` → script Python que conta tempo online e envia notificações  
- `setup_breaks_tracker.sh` → script para configurar o timer no systemd  
- `README.md` → este arquivo  

---

## ⚙️ Instalação / Setup

Na pasta onde está o Python e o setup:

```bash
chmod +x setup_breaks_tracker.sh
./setup_breaks_tracker.sh <TOTAL_TIME> <NOTIFY_EVERY> <INTERVAL_MIN>
````

Parâmetros:

| Parâmetro    | Descrição                                       | Exemplo |
| ------------ | ----------------------------------------------- | ------- |
| TOTAL_TIME   | Total de minutos online que desejas registrar   | 480     |
| NOTIFY_EVERY | Intervalo em minutos para enviar notificações   | 30      |
| INTERVAL_MIN | Intervalo em minutos para rodar o script Python | 1       |

Exemplo de execução:

```bash
./setup_breaks_tracker.sh 480 30 5
```

> Isso irá rodar o script a cada 5 minutos, notificando a cada 30 minutos, contando até 480 minutos por dia.

---

## 🔍 Como confirmar que o serviço está a correr

```bash
systemctl --user status breaks-tracker.timer
```

Deve aparecer algo como:

```
Active: active (waiting) since ...
```

Também podes ver os logs:

```bash
journalctl --user -u breaks-tracker.service
```

Ou verificar o log do script:

```bash
cat online_time.log
```

---

## 🛑 Como parar o serviço

Para parar o timer temporariamente:

```bash
systemctl --user stop breaks-tracker.timer
```

Para desativar (não inicia automaticamente no login):

```bash
systemctl --user disable breaks-tracker.timer
```

---

## 🔄 Como fazer update

Se atualizares o script Python (`breaks_tracker.py`):

1. Recarrega o daemon do systemd:

```bash
systemctl --user daemon-reload
```

2. Reinicia o timer para aplicar alterações:

```bash
systemctl --user restart breaks-tracker.timer
```

> Se quiseres alterar parâmetros (TOTAL_TIME, NOTIFY_EVERY, INTERVAL_MIN), executa novamente:

```bash
./setup_breaks_tracker.sh <TOTAL_TIME> <NOTIFY_EVERY> <INTERVAL_MIN>
```

Isso irá atualizar o service com os novos valores.

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

