FROM python:3.11

RUN apt-get update && apt-get install -y \
    vim curl wget git zip unzip bash iputils-ping net-tools \
    fonts-noto-cjk fonts-noto-cjk-extra fonts-noto-color-emoji \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt

COPY . .

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
