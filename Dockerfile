FROM python:3.12-alpine AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app/

COPY requirements.txt .

RUN apk add --no-cache \
        build-base \
        libffi-dev \
        openssl-dev \
        linux-headers

RUN pip wheel --no-deps --wheel-dir /wheels -r requirements.txt

COPY . .

FROM python:3.12-alpine

RUN apk add --no-cache \
        libffi \
        openssl \
        tzdata

# Crear usuario no-root
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /app

# Cambiar al usuario appuser antes de instalar las dependencias
USER appuser

# Copiar wheels y requirements
COPY --from=builder /wheels /wheels
COPY requirements.txt .

# Instalar dependencias a partir de los wheels (ahora como appuser)
RUN pip install --no-index --find-links=/wheels -r requirements.txt

# Copiar resto del código
COPY --from=builder --chown=appuser:appgroup /app .

# Exponer el puerto
ENV PORT=8000
EXPOSE 8000

# Añadir la ruta de los ejecutables de usuario al PATH
ENV PATH="/home/appuser/.local/bin:${PATH}"

# Comando por defecto
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]