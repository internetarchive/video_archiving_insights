#!/usr/bin/env -S docker image build -t vidins . -f

FROM python:3

ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
WORKDIR /app
ENTRYPOINT ["streamlit", "run"]
CMD ["main.py"]

RUN pip install streamlit pandas numpy matplotlib wordcloud sumgram langdetect

COPY . ./
