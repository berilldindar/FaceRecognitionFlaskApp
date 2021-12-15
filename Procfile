web: gunicorn --bind 0.0.0.0:$PORT form_data:app
heroku ps:scale web=1
RUN update
RUN install -y libgl1-mesa-glx


