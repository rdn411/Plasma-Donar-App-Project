from flask import Flask, render_template, request, redirect, url_for, session
import ibm_db
import json
import requests


app = Flask(__name__)

conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=824dfd4d-99de-440d-9991-629c01b3832d.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=30119;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=wqm60817;PWD=kXBmmeCfbDyfBnGA",'','')

@app.route('/registration')
def home():
    return render_template('register.html')

@app.route('/register',methods=['POST'])
def register():
    x = [x for x in request.form.values()]
    print(x)
    name=x[0]
    email=x[1]
    phone=x[2]
    city=x[3]
    infect=x[4]
    blood=x[5]
    password=x[6]
    sql = "SELECT * FROM user WHERE email =?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt,1,email)
    ibm_db.execute(stmt)
    account = ibm_db.fetch_assoc(stmt)
    print(account)
    if account:
        return render_template('register.html', pred="You are already a member, please login using your details")
    else:
        insert_sql = "INSERT INTO  user VALUES (?, ?, ?, ?, ?, ?, ?)"
        prep_stmt = ibm_db.prepare(conn, insert_sql)
        ibm_db.bind_param(prep_stmt, 1, name)
        ibm_db.bind_param(prep_stmt, 2, email)
        ibm_db.bind_param(prep_stmt, 3, phone)
        ibm_db.bind_param(prep_stmt, 4, city)
        ibm_db.bind_param(prep_stmt, 5, infect)
        ibm_db.bind_param(prep_stmt, 6, blood)
        ibm_db.bind_param(prep_stmt, 7, password)
        ibm_db.execute(prep_stmt)
        return render_template('register.html', pred="Registration Successful, please login using your details")
       
           
        

@app.route('/')    
@app.route('/login')
def login():
    return render_template('login.html')
    
@app.route('/loginpage',methods=['POST'])
def loginpage():
    user = request.form['user']
    passw = request.form['passw']
    sql = "SELECT * FROM user WHERE email =? AND password=?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt,1,user)
    ibm_db.bind_param(stmt,2,passw)
    ibm_db.execute(stmt)
    account = ibm_db.fetch_assoc(stmt)
    print (account)
    print(user,passw)
    if account:
            return redirect(url_for('stats'))
    else:
        return render_template('login.html', pred="Login unsuccessful. Incorrect username / password !") 
      
        
@app.route('/stats')
def stats():
    sql = "SELECT count(*) FROM user WHERE infect ='infected' "
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt)
    count = ibm_db.fetch_assoc(stmt)
    print(count)
    no_of_donors=count['1']
    sql1 = "SELECT blood, count(blood),infect FROM user GROUP BY blood,infect"
    stmt1 = ibm_db.prepare(conn, sql1)
    ibm_db.execute(stmt1)
    count1 = ibm_db.fetch_assoc(stmt1)
    print(count1)
    Opos_count=0
    Apos_count=0
    Bpos_count=0
    ABpos_count=0
    Oneg_count=0
    Aneg_count=0
    Bneg_count=0
    ABneg_count=0
    while count1 != False:
         print(count1)
         if count1["BLOOD"] == 'O Positive' and count1["INFECT"]== 'infected':
            Opos_count=count1['2']
         elif count1["BLOOD"] == "A Positive" and count1["INFECT"]== 'infected':
            Apos_count=count1['2']
         elif count1["BLOOD"] == "B Positive" and count1["INFECT"]== 'infected':
            Bpos_count=count1['2']  
         elif count1["BLOOD"] == "AB Positive" and count1["INFECT"]== 'infected':
            ABpos_count=count1['2']
         elif count1["BLOOD"] == "O Negative" and count1["INFECT"]== 'infected':
            Oneg_count=count1['2']
         elif count1["BLOOD"] == "A Negative" and count1["INFECT"]== 'infected':
            Aneg_count=count1['2']
         elif count1["BLOOD"] == "B Negative" and count1["INFECT"]== 'infected':
            Bneg_count=count1['2'] 
         elif count1["BLOOD"] == "AB Negative" and count1["INFECT"]== 'infected':
            ABneg_count=count1['2']                 
         count1 = ibm_db.fetch_assoc(stmt1)
    
    return render_template('stats.html',b=no_of_donors,b1=Opos_count,b2=Apos_count,b3=Bpos_count,b4=ABpos_count,b5=Oneg_count,b6=Aneg_count,b7=Bneg_count,b8=ABneg_count)
@app.route('/requester')
def requester():
    return render_template('request.html')


@app.route('/requested',methods=['POST'])
def requested():
    bloodgrp = request.form['bloodgrp']
    address = request.form['address']
    print(address)
    sql = "SELECT * FROM user WHERE blood=?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt,1,bloodgrp)
    ibm_db.execute(stmt)
    data = ibm_db.fetch_assoc(stmt)
    msg = "Need Plasma of your blood group for: "+address
    while data != False:
        print ("The Phone is : ", data["PHONE"])
        url="https://www.fast2sms.com/dev/bulk?authorization=xCXuwWTzyjOD2ARd1EngbH3a7tKIq5PklJ8YSf0Lh4FQZecs9iNI1dSvuqprxFwCKYJXA5amQkBE36Rl&sender_id=FSTSMS&message="+msg+"&language=english&route=p&numbers="+str(data["PHONE"])
        result=requests.request("GET",url)
        print(result)
        data = ibm_db.fetch_assoc(stmt)
    return render_template('request.html', pred="Your request is sent to the concerned people.")
    

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)

