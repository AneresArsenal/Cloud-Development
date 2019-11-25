FROM python:3.7
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .
ENV PORT=8000
ENV GOOGLE_APPLICATION_CREDENTIALS='./hw8-tays-docker-7541c195e0c1.json'
EXPOSE ${PORT}
CMD [ "python", "main.py"]
