FROM singularityware/singularity:3.2.1

# Testing package
RUN apk add --update python python-dev py-pip build-base
RUN pip install flake8 pytest pytest-cov pytest-flake8 python-coveralls

RUN mkdir /app
COPY . /app

RUN cd /app && python setup.py install

EXPOSE 8088
EXPOSE 8081
EXPOSE 8082

WORKDIR /app
ENTRYPOINT [ '/usr/bin/clair-singularity' ]
