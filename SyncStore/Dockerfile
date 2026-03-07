# Usa uma imagem leve do Python
FROM python:3.9-slim

# Define a pasta de trabalho dentro do container
WORKDIR /app

# Copia todos os arquivos da sua pasta para dentro do container
COPY . .

# Comando padrão (será sobrescrito pelo docker-compose, mas é bom ter)
CMD ["python", "node_cluster.py", "1"]