web:gunicorn form_data:app
RUN pip update
!apt update
!apt install ffmpeg libsm6 libxext6 -y
heroku ps: scale web = 1