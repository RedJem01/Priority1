FROM python:3.12-slim
WORKDIR /Priority1
COPY . /Priority1
RUN pip3 install -r requirements.txt
ENV FLASK_APP=main
ENV PYTHONUNBUFFERED=1
ENV AWS_REGION=''
ENV P1_QUEUE=''
ENV ACCESS_KEY=''
ENV SECRET_ACCESS_KEY=''
ENV TEAMS_WEBHOOK=''
EXPOSE 8000
CMD ["gunicorn", "--bind","0.0.0.0:8000", "main:app"]