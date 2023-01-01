FROM python:3.8

WORKDIR /usr/src/twstock_analysis


# install ta-lib
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar xvfz ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib && \
    wget 'http://git.savannah.gnu.org/gitweb/?p=config.git;a=blob_plain;f=config.guess;hb=HEAD' -O config.guess && \
    wget 'http://git.savannah.gnu.org/gitweb/?p=config.git;a=blob_plain;f=config.sub;hb=HEAD' -O config.sub && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    pip install ta-lib

COPY compute ./compute
RUN cd compute && \
    pip install -r requirements.txt

RUN apt-get update && apt-get -y install cmake protobuf-compiler

COPY core ./core
RUN cd core && mkdir -p build

EXPOSE 5432
