from flask import Flask,redirect,url_for

app=Flask(__name__)

@app.route('/admin')
def message_admin():
    return "Hello World"

@app.route('/user/<name>')
def message_user(name):
    return "Hello {}".format(name)

@app.route('/user/<name_admin>')
def message_user_admin(name_admin):
    if name_admin=="beril":
        return redirect(url_for(message_admin))
    else:
        return redirect(url_for(message_user,name=name_admin))

if __name__=="__main__":
    app.run(debug=True)
