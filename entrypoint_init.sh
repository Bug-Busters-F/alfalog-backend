#!/bin/bash

# Caso ocorra um erro dentro da execução, ele para sai imediatamente
set -e 

# HOST e PORT do docker compose.
DB_HOST="db"
DB_PORT="3306"

# Espera até 60 segundos pelo banco de dados
echo "Etapa: aguardando conexão ${DB_HOST}:${DB_PORT}..."
/app/wait-for-it.sh "${DB_HOST}:${DB_PORT}" --timeout=60 --strict -- echo "Conexão estabelecida!"

# Executa o script de criação de tabelas
echo "Etapa: criando as tabelas com o script (python -m database.create)..."
python -m database.create
echo "Entrypoint: Database tables created."


echo "Etapa: rodando COMEX update script automaticamente (argumento 'sim')..."
echo "sim" | flask comex update
echo "Etapa: COMEX update finalizado!."


# O container finaliza aqui, pois não há 'exec flask run'
exit 0