from flask import Flask

app=Flask(__name__)

@app.route('/')
def message():
    return "Hello World"

@app.route('/hello')
def second_page():
    return "This testing api for routing."

@app.route('/hello/<name>')
def Dynamic_api(name):
    return "<h2>Hello {} </h2>".format(name)

if __name__=="__main__":
    app.run(debug=True)
