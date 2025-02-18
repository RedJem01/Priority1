FROM python:latest
WORKDIR /Priority1
COPY . /Priority1
RUN pip3 install -r requirements.txt
ENV FLASK_APP=main
ENV AWS_REGION=''
ENV P1_QUEUE=''
ENV ACCESS_KEY=''
ENV SECRET_ACCESS_KEY=''
ENV TEAMS_WEBHOOK=''
EXPOSE 8000
CMD ["flask", "run", "--host", "0.0.0.0", "--port", "8000"]