#!/bin/bash
# Script de restart para Railway
echo "🔄 Reiniciando serviço bacen-cron..."

# Mata processo existente se houver
pkill -f "python cron.py" || true

# Aguarda um pouco
sleep 5

# Inicia novo processo
echo "🚀 Iniciando novo processo..."
python cron.py &

# Aguarda um pouco para verificar se iniciou
sleep 10

# Verifica se está rodando
if pgrep -f "python cron.py" > /dev/null; then
    echo "✅ Serviço reiniciado com sucesso"
else
    echo "❌ Falha ao reiniciar serviço"
    exit 1
fi
