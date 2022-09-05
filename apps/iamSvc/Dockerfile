FROM python:slim

# set working directory
WORKDIR /api

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1 # Prevents writing pyc files to disc
ENV PYTHONUNBUFFERED 1 # Prevents Python from buffering stdout and stderr

# install dependencies
RUN pip install --upgrade pip

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# copy project
COPY . .

EXPOSE 5050


ENTRYPOINT ["python3"]
CMD [ "gunicorn", "-w", "4", "--bind", "0.0.0.0:5050", "app:app"]
