FROM python:3.11

RUN apt-get update && apt-get install -y \
    vim curl wget git zip unzip bash iputils-ping net-tools \
    libatlas-base-dev \
    && rm -rf /var/lib/apt/lists/*
  
RUN cd /tmp \
    && wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz \
    && tar -xvf ta-lib-0.4.0-src.tar.gz \
    && cd ta-lib \
    && wget -O config.guess https://git.savannah.gnu.org/cgit/config.git/plain/config.guess \
    && wget -O config.sub https://git.savannah.gnu.org/cgit/config.git/plain/config.sub \
    && chmod +x config.guess config.sub \
    && ./configure --prefix=/usr/local \
    && (make -j4 || make) \
    && make install \
    && rm -rf /tmp/* \
    && echo "/usr/lib" >> /etc/ld.so.conf \
    && ldconfig

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
