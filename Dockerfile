#!/usr/bin/env -S docker image build -t vidins . -f

FROM python:3.10-slim-bullseye

ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
WORKDIR /app
ENTRYPOINT ["streamlit", "run"]
CMD ["main.py"]

RUN apt-get update && apt-get upgrade -y && apt-get install gcc -y
COPY . ./
RUN pip install -r requirements.txt
