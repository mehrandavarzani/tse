FROM python36

COPY . /app

WORKDIR /app
RUN apt-get install -y python3-setuptools
RUN pip3 install --no-cache-dir -r requirements.txt
