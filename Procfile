web:gunicorn form_data:app
heroku ps:scale web=1
RUN pip update
RUN pip install ffmpeg libsm6 libxext6  -y
