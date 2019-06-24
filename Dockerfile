FROM singularityware/singularity:3.2.1

# Testing package
RUN apk add --update python3 python3-dev py3-pip build-base
RUN pip3 install flake8 pytest pytest-cov pytest-flake8 python-coveralls

RUN mkdir /app
COPY . /app

RUN cd /app && python3 setup.py install

EXPOSE 8088
EXPOSE 8081
EXPOSE 8082

WORKDIR /app
ENTRYPOINT [ '/usr/bin/clair-singularity' ]
