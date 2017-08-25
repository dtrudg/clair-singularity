FROM python:3.5-jessie

ENV DEBIAN_FRONTEND noninteractive

# Install Singularity from NeuroDebian
RUN wget -O- http://neuro.debian.net/lists/jessie.us-nh.full > /etc/apt/sources.list.d/neurodebian.sources.list
RUN apt-key adv --recv-keys --keyserver hkp://pool.sks-keyservers.net:80 0xA5D32F012649A5A9
RUN apt-get -qq update
RUN apt-get install -y singularity-container

# Testing packages
RUN pip install flake8 pytest pytest-cov pytest-flake8 python-coveralls

RUN mkdir /app
COPY . /app

RUN cd /app && python setup.py install

EXPOSE 8088
EXPOSE 8081
EXPOSE 8082

WORKDIR /app
CMD clair-singularity
