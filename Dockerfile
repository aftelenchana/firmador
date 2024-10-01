# Usa una imagen base de Python
FROM python:3.10-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos requeridos
COPY requirements.txt .

# Instala las dependencias del sistema
RUN apt-get update && \
    apt-get install -y libssl-dev g++ libcrypto++-dev && \
    rm -rf /var/lib/apt/lists/*

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de tu aplicación
COPY . .

# Expone el puerto que usarás
EXPOSE 5000

# Comando para iniciar tu aplicación
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
