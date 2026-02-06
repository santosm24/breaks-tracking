#!/bin/bash

# Script para instalar o Breaks Tracker como serviço systemd
# Roda automaticamente ao iniciar o PC

SERVICE_FILE="breaks_tracker.service"
SYSTEMD_USER_DIR="$HOME/.config/systemd/user"

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}=== Instalador do Breaks Tracker ===${NC}\n"

# Criar diretório se não existir
mkdir -p "$SYSTEMD_USER_DIR"

# Copiar service file
echo -e "${YELLOW}Copiando service file...${NC}"
cp "$SERVICE_FILE" "$SYSTEMD_USER_DIR/"

# Recarregar systemd
echo -e "${YELLOW}Recarregando systemd...${NC}"
systemctl --user daemon-reload

# Ativar serviço
echo -e "${YELLOW}Ativando serviço para iniciar automaticamente...${NC}"
systemctl --user enable breaks_tracker.service

# Iniciar serviço agora
echo -e "${YELLOW}Iniciando serviço...${NC}"
systemctl --user start breaks_tracker.service

echo -e "\n${GREEN}✓ Breaks Tracker instalado com sucesso!${NC}"
echo -e "${GREEN}O serviço iniciará automaticamente ao ligar o PC.${NC}\n"

echo -e "${YELLOW}Comandos úteis:${NC}"
echo "  Ver status:       systemctl --user status breaks_tracker"
echo "  Ver logs:         journalctl --user -u breaks_tracker -f"
echo "  Parar serviço:    systemctl --user stop breaks_tracker"
echo "  Reiniciar:        systemctl --user restart breaks_tracker"
echo "  Desinstalar:      systemctl --user disable breaks_tracker && systemctl --user stop breaks_tracker"
echo -e "\n${YELLOW}Para editar os parâmetros (intervalos, tempos), edite o arquivo:${NC}"
echo "  $SYSTEMD_USER_DIR/breaks_tracker.service"
echo -e "  ${YELLOW}Depois execute: systemctl --user daemon-reload && systemctl --user restart breaks_tracker${NC}"
