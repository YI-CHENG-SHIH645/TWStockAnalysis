FROM python:3.9

WORKDIR /usr/src/twstock_analysis


# install ta-lib
RUN wget https://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar xvfz ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib && \
    wget 'https://git.savannah.gnu.org/gitweb/?p=config.git;a=blob_plain;f=config.guess;hb=HEAD' -O config.guess && \
    wget 'https://git.savannah.gnu.org/gitweb/?p=config.git;a=blob_plain;f=config.sub;hb=HEAD' -O config.sub && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    pip install ta-lib

COPY compute ./compute
RUN cd compute && \
    pip install -r requirements.txt

COPY td_op ./td_op
RUN pip install ./td_op

RUN apt-get update && apt-get -y install cmake protobuf-compiler

EXPOSE 5432
