web:gunicorn form_data:app
RUN pip update
RUN pip3 install ffmpeg libsm6 libxext6  -y
heroku ps: scale web = 1