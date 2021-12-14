import json,time
from camera import VideoCamera
from flask import Flask, render_template, request, Response,redirect,url_for
import requests
import cv2

app=Flask(__name__)
output=[]

@app.route('/')
def home_page():
    return render_template("IY_Home_page.html",result=output)

@app.route('/login')
def about_page():
    return render_template("login.html",result=output)

@app.route('/contact')
def contact_page():
    return render_template("contact.html",result=output)

@app.route('/signup')
def signup_page():
    return render_template("signup.html",result=output)

@app.route('/cam')
def sign_page():
    return render_template("camera.html")


@app.route('/camera',methods=['POST'])
def camera():
    cap=cv2.VideoCapture(0)
    while True:
        ret,img=cap.read()
        img=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        cv2.imwrite("static/cam.png",img)

        # return render_template("camera.html",result=)
        time.sleep(0.1)
        return json.dumps({'status': 'OK', 'result': "static/cam.png"})
        if cv2.waitKey(0) & 0xFF ==ord('q'):
            break
    cap.release()

    return json.dumps({'status': 'OK', 'result': "static/cam.png"});

def gen(camera):
    while True:
        data= camera.get_frame()

        frame=data[0]
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()), mimetype='multipart/x-mixed-replace; boundary=frame')

database={"Bitirme":"Projesi","Beril":"Dindar"}
@app.route('/success/<name>/<passwrd>')
def Success(name,passwrd):
    if name in database.keys():
       if passwrd==database[name]:
          return "<h1>Welcome to Kırıkkale University!</h1>"
       else:
           return "<h1>Invalid Username or password!</h1>"
    else:
        return "<h1>Username doesn't exists!</h1>"


@app.route('/fetch_data',methods=['POST','GET'])
def FetchData():
    if request.method=='POST':
        user=request.form['nm']
        password = request.form['pw']
        return redirect(url_for('Success',name=user,passwrd=password))
    else:
        user = request.args.get('nm')
        password = request.args.get('pw')
        return redirect(url_for('Success', name=user,passwrd=password))

@app.route('/registered/<name>/<passwrd>/<cnfpass>')
def Registered(name,passwrd,cnfpass):
    if passwrd==cnfpass:
        database.update({name:passwrd})
        return render_template("signup.html",message="You have successfully signed up !")
    else:
        return render_template("signup.html",message="Password didn't matched !")


@app.route('/signup',methods=['POST','GET'])
def SignUp():
    if request.method=='POST':
        user=request.form['snm']
        password = request.form['spw']
        cpassword = request.form['scpw']
        return redirect(url_for('Registered',name=user,passwrd=password,cnfpass=cpassword))
    else:
        user = request.args.get('snm')
        password = request.args.get('spw')
        cpassword = request.args.get('scpw')
        return redirect(url_for('Registered', name=user,passwrd=password,cnfpass=cpassword))

@app.route('/result',methods=["POST","GET"])
def Result():
    if request.method=="POST":
        print(list(request.form.values()))
        result=list(request.form.values())[0]
        if result.lower()=="restart":
            output.clear()
        else:
            try:
                r = requests.post('http://localhost:5002/webhooks/rest/webhook', json={"message": result})
                print("Bot says, ")
                for i in r.json():
                    bot_message = i['text']
                    print(f"{i['text']}")
                output.extend([("message parker",result),("message stark",bot_message)])
            except:
                output.extend([("message parker", result), ("message stark", "We are unable to process your request at the moment. Please try again...")])

        print(output)
        return render_template("IY_Home_page.html",result=output)

if __name__=="__main__":
    app.run(debug=True)