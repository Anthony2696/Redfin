FROM ubuntu:20.04 
WORKDIR /app

RUN apt-get update
RUN apt-get install python3.8 python3.8-distutils curl -y
RUN curl https://bootstrap.pypa.io/get-pip.py | python3.8 - --user

COPY requirements.txt requirements

RUN python3.8 -m pip install --quiet --no-cache-dir -r requirements

CMD [ "python3.8", "insert_original_redfin.py"]
