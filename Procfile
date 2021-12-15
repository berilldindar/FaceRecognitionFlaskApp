web: gunicorn --bind 0.0.0.0:$PORT form_data:app
heroku ps:scale web=1
RUN apt-get update
RUN apt install -y libgl1-mesa-glx


