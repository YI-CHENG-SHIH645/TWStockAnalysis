FROM python:3

WORKDIR /usr/src/FinTech_2020

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# install ta-lib
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar xvfz ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    pip install ta-lib

COPY . .
