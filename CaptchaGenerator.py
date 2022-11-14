import math
from PIL import Image as PilImage, ImageDraw,ImageFont,ImageTk
from tkinter import *
from tkinter import messagebox
import requests
from bs4 import BeautifulSoup
import threading
import time
import random
import json

keepLoggedIn = True

def requestRouterLoginPage(url="https://internet.lpu.in/24online/webpages/client.jsp?fromlogout=false"):
    try:
        resp = requests.get(url,verify=False)
        return resp.text
    except requests.exceptions.ConnectionError as e:
        return False
    
    
def loadCredentials():
    global usernameFieldData
    global passwordFieldData
    try:
        with open("credentials.dat") as f:
            data = f.read()
            if(data != ""):
                credentials = json.loads(data)
                usernameFieldData.set(credentials["username"])
                passwordFieldData.set(credentials["password"])
    except Exception as e:
        usernameFieldData.set("")
        passwordFieldData.set("")
    
    
    
    
def generateCaptcha():
    limit1 = random.randint(2,99)
    limit2 = random.randint(2,99)
    while(limit1%limit2 != 0):
        limit1 = random.randint(2,99)
        limit2 = random.randint(2,99)
    operation = random.choice(["-","+","÷","×"])
    if(operation == "-"):
        return [limit1-limit2,operation,str(limit1)+"-"+str(limit2)]
    elif(operation == "+"):
        return [limit1+limit2,operation,str(limit1)+"+"+str(limit2)]
    elif(operation == "÷"):
        return [limit1/limit2,operation,str(limit1)+"÷"+str(limit2)]
    else:
        if(limit1*limit2<300):
            return [limit1*limit2,operation,str(limit1)+"×"+str(limit2)]
        else:
            return [limit1/limit2,operation,str(limit1)+"÷"+str(limit2)]
    

    
    
    
    
    
def routerLoginFinal(sendingData,url = "https://internet.lpu.in/24online/servlet/E24onlineHTTPClient"):
    try:
        resp = requests.post(url,data=sendingData,verify=False)
        if(resp.status_code == 200):
            if("Wrong username/password" in resp.text):
                return "CredentialError"
            elif("You are not allowed to logged in into multiple devices at same time,Disconnect your previous session before creating new session" in resp.text):
                return "alreadyConnected"
            elif("NOTE:- Dear Users, Please Logout your current session properly before moving to new location." in resp.text):
                return "LoggedOut"
            else:
                return "ok"
        else:
            return "RouterUnReachable"
    except Exception as e:
        return "RouterUnReachable"
    
    
    
    
    

def checkInternet(url="https://ipinfo.io/ip"):
    try:
        resp = requests.get(url,timeout=2)
        if(resp.status_code==200):
            return True
        else:
            return False
    except Exception as e:
        return False
    
    
    
    
    
    

def generateCaptchaImage(captchaCode):
    # create line image
    img = PilImage.new("RGB", (220,50),color = (185, 201, 238))
    img1 = ImageDraw.Draw(img)  
    font = ImageFont.truetype("arial.ttf", 30)
    img1.text((65, 10), captchaCode, fill =(255, 0, 0),font=font)
    img1.line((20,14,180, 34), fill=(0, 192, 192),width=3)
    img1.line((20,44,180, 10), fill=(0, 192, 192),width=3)
    return img
    
    
    
    
    
    
def checkAndLogin(username,password):
    global keepLoggedIn
    while keepLoggedIn:
        if(checkInternet()):
            offlineCheck.config(bg="green")
        else:
            offlineCheck.config(bg="red")
            response = requestRouterLoginPage()
            if(response):
                soup = BeautifulSoup(response,'html.parser')
                inputFields = soup.find_all("input")
                sendingData = {}
                for fields in inputFields:
                    if(fields.has_attr("name")):
                        try:
                            sendingData[fields["name"]] = fields["value"]
                        except Exception as e:
                            sendingData[fields["name"]] = ""

                sendingData["saveinfo"] = "saveinfo"
                sendingData["isAccessDenied"] = "false"
                sendingData["checkClose"] = 1
                sendingData["username"] = sendingData["loggedinuser"] = username
                sendingData["password"] = password
                
                is_login_true = routerLoginFinal(sendingData)
                if (is_login_true == "CredentialError"):
                    submitButton["state"] = "normal"
                    messagebox.showinfo("Incorrect Credential", "Incorrect username or Password")
                    return
                elif(is_login_true == "RouterUnReachable"):
                    submitButton["state"] = "normal"
                    messagebox.showinfo("Unreachable", "Router is not reachable! Kindly connect to LPU network or contact network administrator")
                    return
                elif(is_login_true == "alreadyConnected"):
                    submitButton["state"] = "normal"
                    messagebox.showinfo("Unreachable", "Other device connected log out and then log in from here")
                    return
            else:
                submitButton["state"] = "normal"
                messagebox.showinfo("Unreachable", "Router is not reachable! Kindly connect to LPU network or contact network administrator")
                return
        time.sleep(3)

        
        
        
        
        
        
def connectToInternet():
    global offlineCheck
    saveCredentials()
    if(captcha_verification_entry.get() != "" and generated_captcha[0]==int(captcha_verification_entry.get())):
        if(usernameField.get() != "" and passwordField.get() != ""):
            username = usernameField.get()+"@lpu.com"
            password = passwordField.get()
            submitButton["state"] = "disabled"
            th1 = threading.Thread(target=checkAndLogin,args=(username,password))
            th1.daemon=True
            th1.start()
        elif():
            messagebox.showinfo("Invalid User Info", "Kindly fill the username and password correctly")
    else:
        messagebox.showinfo("Incorrect Captcha", "Kindly Solve the captcha correctly")
    
    
    
    
    
    
    
    
    
def refreshCaptcha():
    global generated_captcha
    generated_captcha = generateCaptcha()
    captchaImage = ImageTk.PhotoImage(generateCaptchaImage(generated_captcha[2]))#Generate image of ImageTk class
    captchaLabel.configure(image=captchaImage)
    captchaLabel.image=captchaImage
    
    
def saveCredentials():
    credentials = json.dumps({"username":usernameField.get(),"password":passwordField.get()})
    with open("credentials.dat","w") as f:
        f.write(str(credentials))


win = Tk()#Creating Tkinter object
win.title("LPU INTERNET LOGIN")
win.geometry("800x400")
win.minsize(800,400)
win.maxsize(800,400)
usernameFieldData = DoubleVar()
passwordFieldData = DoubleVar()
Label(win,text="Enter username",font=("Airel",13)).grid(row=0,column=0)#Label for the username
usernameField = Entry(win,text="username",font=("Ariel",13),textvariable = usernameFieldData)
usernameField.grid(row=0,column=1,pady=20,padx=10,ipadx=100,ipady=15)#Entry for the username
Label(win,text="Enter password",font=("Airel",13)).grid(row=1,column=0)
passwordField = Entry(win,show="*",text="password",font=("Ariel",13),textvariable = passwordFieldData)
passwordField.grid(row=1,column=1,pady=20,padx=10,ipadx=100,ipady=15)
offlineCheck = Label(win,bg="red")
offlineCheck.grid(row=0,column=2,ipadx=40,ipady=15)
generated_captcha = generateCaptcha()
loadCredentials()
captchaImage = ImageTk.PhotoImage(generateCaptchaImage(generated_captcha[2]))#Generate image of ImageTk class
captchaLabel = Label(image=captchaImage)
captchaLabel.grid(row=2,column=0)
captcha_verification_entry = Entry(win,font=("Ariel",13))
captcha_verification_entry.grid(row=2,column=1,ipadx=100,ipady=15,pady=20,padx=10)
captcha_refresh_button = Button(win,text="Refresh Captcha",font=("Ariel",13),command=refreshCaptcha)
captcha_refresh_button.grid(row=2,column=2,padx=10,pady=20)

submitButton = Button(win,text="Login To LPU Internet",font=("Ariel",13),command=connectToInternet)
submitButton.grid(row=3,column=0,padx=10,pady=20,columnspan=2)

win.mainloop()#Mainloop to launch graphical interface