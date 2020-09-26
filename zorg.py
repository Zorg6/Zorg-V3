#postgresql might work
#discarded wtforms, which created the trouble
#features lost: password encryption, has to be changed everywhere
from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from passlib.hash import sha256_crypt
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
import csv
import os
#from wtforms import Form, StringField, TextAreaField, PasswordField, validators


app=Flask(__name__)

ENV = 'dev'

developer='Arjun'

if ENV=='dev':
    app.debug=True
    if developer=='Arjun':
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Postgre-arj4703@localhost/Zorg'
    elif developer=='Tarun':
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Tarun@postgresql@localhost/Zorg'
else:
    app.debug=False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://nodkzxyxsbqfdj:e12cbd58f24bb6ee6c9896c2731480a784a73b81fd860b2a245135b372c4f32@ec2-54-236-146-234.compute-1.amazonaws.com:5432/d2hmpp8n530vvp'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db=SQLAlchemy(app)

@app.route('/')
def home():
    return  render_template('index.html')

class RegisterMnmg(db.Model):
    __tablename__ = 'hospdetails'
    namehptl = db.Column(db.String(200))
    username = db.Column(db.String(200), primary_key=True)
    password = db.Column(db.String(20))
    pincode = db.Column(db.String(10))
    address = db.Column(db.Text())

    def __init__(self, namehptl, username, password, pincode, address):
        self.namehptl = namehptl
        self.username = username
        self.password = password
        self.pincode = pincode
        self.address = address
        
@app.route('/registermnmg', methods=['GET','POST'])
def registermnmg():
    if request.method == 'POST':
        namehptl = request.form['namehptl'] 
        username = request.form['username']
        password = request.form['password']
        pincode = request.form['pincode'] 
        address = request.form['address']
        if db.session.query(RegisterMnmg).filter(RegisterMnmg.username == username).count() == 0:
            data = RegisterMnmg(namehptl, username, password, pincode, address)
            db.session.add(data)
            db.session.commit()
            flash('you are now registered', 'success')
            return redirect(url_for('loginmanagement'))
        else:
            flash("Username already exists", 'danger')
    return render_template('remnmg.html')

class CustomerDet(db.Model):#changed the class name since it is getting confused between the class and the table name
    __tablename__ = 'custdetails'
    namecust = db.Column(db.String(200))
    username = db.Column(db.String(200), primary_key=True)
    password = db.Column(db.String(20))
    pincode = db.Column(db.String(10))
    address = db.Column(db.Text())
    gmail_id = db.Column(db.String(200))
    aadhar = db.Column(db.String(20), unique=True)
    age = db.Column(db.String(5))
    gender = db.Column(db.String(1))
    prevmedrcrds = db.Column(db.Text())
    def __init__(self, namecust, username, password, pincode, address, gmail_id, aadhar, age, gender, prevmedrcrds):
        self.namecust = namecust
        self.username = username
        self.password = password
        self.pincode = pincode
        self.address = address
        self.gmail_id = gmail_id
        self.aadhar = aadhar
        self.age = age
        self.gender = gender
        self.prevmedrcrds = prevmedrcrds

@app.route('/custdetails', methods=['GET','POST'])
def custdetails():
    if request.method == 'POST':
        namecust = request.form['namecust'] 
        username = request.form['username']
        password = request.form['password']
        gmail_id = request.form['gmail_id']
        address = ''
        pincode = ''
        aadhar = ''
        age = ''
        gender = ''
        prevmedrcrds = ''
        if db.session.query(CustomerDet).filter(CustomerDet.username == username).count() == 0:
            data = CustomerDet(namecust, username, password, pincode, address, gmail_id, aadhar, age, gender, prevmedrcrds)#needs all the columns to run without errors
            db.session.add(data)
            db.session.commit()
            flash('you are now registered', 'success')
            return redirect(url_for('logincustomer'))
        else:
            flash("Username already exists", 'danger')
    return render_template('recust.html')    

@app.route('/loginmanagement', methods=['GET','POST'])
def loginmanagement():
    if request.method == 'POST':
        usermnmg = request.form['username']
        password_candidate = request.form['password']
        user = db.session.query(RegisterMnmg).filter(RegisterMnmg.username == usermnmg).first()
        db.session.commit()
        if user is None:
            flash('No such username exists', 'danger')
            return render_template('lomnmg.html')
        else:
            if password_candidate == user.password:
                session['logged_in'] = True
                session['username'] = usermnmg
                session['name'] = user.namehptl
                session['pincode'] = user.pincode
                flash('You are now logged in','success')
                return redirect(url_for('dashboardmnmg'))
            else:
                flash('Incorrect password','danger')
                return render_template('lomnmg.html')
    else:
        return render_template('lomnmg.html')

@app.route('/logincustomer', methods=['GET','POST'])
def logincustomer():
    if request.method == 'POST':
        usercust = request.form['username']
        password_candidate = request.form['password']
        user = db.session.query(CustomerDet).filter(CustomerDet.username == usercust).first()
        db.session.commit()
        if user is None:
            flash('No such username exists', 'danger')
            return render_template('locust.html')
        else:
            if password_candidate == user.password:
                session['logged_in'] = True
                session['username'] = usercust
                session['name'] = user.namecust
                session['pincode'] = user.pincode
                flash('You are now logged in','success')
                return redirect(url_for('dashboard'))
            else:
                flash('Incorrect password','danger')
                return render_template('locust.html')
    else:
        return render_template('locust.html')

def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('UNAUTHORISED, Please Login','danger')
            return redirect(url_for('home'))
    return wrap

@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out','success')
    return redirect(url_for('home'))

@app.route('/dashboard', methods=['GET','POST'])
@is_logged_in
def dashboard():
    username = session['username']
    custdata = db.session.query(CustomerDet).filter(CustomerDet.username == username).first()
    db.session.commit()
    if custdata.aadhar == '' or custdata.age == '' or custdata.gender == '' or custdata.prevmedrcrds == '' or custdata.address == '' or custdata.pincode == '':
        flash("Please fill these details","danger")
        return redirect(url_for('add_profile'))
    else:
        for i in custdata:
            if i[1] == username:
                return render_template('dashboard.html', profile = i.query.all())
    return render_template('dashboard.html')    

@app.route('/add_profile', methods=['GET','POST'])
@is_logged_in
def add_profile():
    username = session['username']
    if request.method =='POST':
        aadhar = request.form['aadhar']
        age = request.form['age']
        gender = request.form['gender']
        prevmedrcrds = request.form['prevmedrcrds']
        address = request.form['address']
        pincode = request.form['pincode']
        if db.session.query(CustomerDet).filter(CustomerDet.username == username).count() == 1:
            update = db.session.query(CustomerDet).filter(CustomerDet.username == username).first()
            update.aadhar = aadhar
            update.age = age
            update.gender = gender
            update.prevmedrcrds = prevmedrcrds
            update.address = address
            update.pincode = pincode
            db.session.commit()
            flash('Profile Created', 'success')
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('editprofile'))
    return render_template('add_profile.html')

@app.route('/editprofile', methods=['GET','POST'])
@is_logged_in
def editprofile():
    username = session['username']
    user = db.session.query(CustomerDet).filter(CustomerDet.username == username).first()
    db.session.commit()
    if request.method == 'POST':
        aadhar = request.form['aadhar']
        if aadhar != '':
            user.aadhar = aadhar
        age = request.form['age']
        if age != '':
            user.age = age
        prevmedrcrds = request.form['prevmedrcrds']
        if prevmedrcrds != '':
            user.prevmedrcrds = prevmedrcrds
        address = request.form['address']
        if address != '':
            user.address = address
        pincode = request.form['pincode']
        if pincode != '':
            user.pincode = pincode
        gmail_id = request.form['gmail_id']
        if gmail_id != '':
            user.gmail_id = gmail_id
        db.session.commit()
        flash('Profile Updated','success')
        return redirect(url_for('dashboard'))
    return render_template('editprofile.html',profile = user.query.all())

class Orders(db.Model):
    __tablename__ = 'orders'
    number = db.Column(db.Integer, primary_key=True)
    hptl_username_in_vicinity = db.Column(db.String(200))
    username_cust = db.Column(db.String(200))
    type = db.Column(db.String(50))
    address = db.Column(db.Text())
    age = db.Column(db.String(5))
    gender = db.Column(db.String(1))
    prevmedrcrds = db.Column(db.Text())
    result = db.Column(db.String(1))
    def __init__(self, hptl_username_in_vicinity, username_cust, type, address, age, gender, prevmedrcrds, result):
        self.hptl_username_in_vicinity = hptl_username_in_vicinity
        self.username_cust = username_cust
        self.type = type
        self.address = address
        self.namecust = namecust
        self.aadhar = aadhar 
        self.age = age
        self.gender = gender
        self.prevmedrcrds = prevmedrcrds
        self.result = result

@app.route('/accident')
@is_logged_in
def accident():
    username = session['username']
    pincode = session['pincode']
    list_of_hosp_to_send_message = []
    profile = db.session.query(CustomerDet).filter(CustomerDet.username == username).first()
    db.session.commit()
    if profile is not None:
        if db.session.query(Orders).filter(Orders.username_cust == username).count() == 0:
            type='accident'
            total_num_of_hosp = db.session.query(RegisterMnmg).filter(RegisterMnmg.pincode == pincode).all()
            for i in range (len(total_num_of_hosp)):
                list_of_hosp_to_send_message.append(total_num_of_hosp[i][1])
            #send to all hospitals at the same time
            for hptl_username_in_vicinity in list_of_hosp_to_send_message:
                data = Orders(hptl_username_in_vicinity, username, type, profile.address, profile.name, profile.aadhar, profile.age, profile.gender, profile.prevmedrcrds)
                db.session.add(data)
                db.session.commit()
            return render_template('request_sent.html')
        else:
            flash('you have already sent a request, kindly wait till it is processed','danger')
            return render_template('request_sent.html')
    else:
        flash('please fill in your details so that we can send it to the hospitals','danger')
        return redirect(url_for('add_profile'))
    return render_template('request_sent.html')

@app.route('/heartattack')
@is_logged_in
def heartattack():
    username = session['username']
    pincode = session['pincode']
    list_of_hosp_to_send_message = []
    profile = db.session.query(CustomerDet).filter(CustomerDet.username == username).first()
    db.session.commit()
    if profile is not None:
        if db.session.query(Orders).filter(Orders.username_cust == username).count() == 0:
            type='heart attack'
            total_num_of_hosp = db.session.query(RegisterMnmg).filter(RegisterMnmg.pincode == pincode).count()
            for i in range(total_num_of_hosp):
                list_of_hosp_to_send_message.append(hospital.username)
            #send to all hospitals at the same time
            for hptl_username_in_vicinity in list_of_hosp_to_send_message:
                data = Orders(hptl_username_in_vicinity, username, type, profile.address, profile.name, profile.aadhar, profile.age, profile.gender, profile.prevmedrcrds)
                db.session.add(data)
                db.session.commit()
            return render_template('request_sent.html')
        else:
            flash('you have already sent a request, kindly wait till it is processed','danger')
            return render_template('request_sent.html')
    else:
        flash('please fill in your details so that we can send it to the hospitals','danger')
        return redirect(url_for('add_profile'))
    return render_template('request_sent.html')

@app.route('/otherailments')
@is_logged_in
def otherailments():
    username = session['username']
    pincode = session['pincode']
    list_of_hosp_to_send_message = []
    profile = db.session.query(CustomerDet).filter(CustomerDet.username == username).first()
    db.session.commit()
    if profile is not None:
        if db.session.query(Orders).filter(Orders.username_cust == username).count() == 0:
            type='other ailments'
            total_num_of_hosp = db.session.query(RegisterMnmg).filter(RegisterMnmg.pincode == pincode).count()
            for i in range(total_num_of_hosp):
                list_of_hosp_to_send_message.append(hospital.username)
            #send to all hospitals at the same time
            for hptl_username_in_vicinity in list_of_hosp_to_send_message:
                data = Orders(hptl_username_in_vicinity, username, type, profile.address, profile.name, profile.aadhar, profile.age, profile.gender, profile.prevmedrcrds)
                db.session.add(data)
                db.session.commit()
            return render_template('request_sent.html')
        else:
            flash('you have already sent a request, kindly wait till it is processed','danger')
            return render_template('request_sent.html')
    else:
        flash('please fill in your details so that we can send it to the hospitals','danger')
        return redirect(url_for('add_profile'))
    return render_template('request_sent.html')


class PastOrders(db.Model):
    __tablename__ = 'pastorders'
    number = db.Column(db.Integer, primary_key=True)
    name_of_hptl_accepting_responsibilty = db.Column(db.String(200))
    username_cust = db.Column(db.String(200))
    type = db.Column(db.String(50))
    address = db.Column(db.Text())
    namecust = db.Column(db.String(200))
    aadhar = db.Column(db.String(20))
    age = db.Column(db.String(5))
    gender = db.Column(db.String(1))
    prevmedrcrds = db.Column(db.Text())

    def __init__(self, name_of_hptl_accepting_responsibilty, username_cust, type, address, namecust, aadhar, age, gender, prevmedrcrds):
        self.name_of_hptl_accepting_responsibilty = name_of_hptl_accepting_responsibilty
        self.username_cust = username_cust
        self.type = type
        self.address = address
        self.namecust = namecust
        self.aadhar = aadhar
        self.age = age
        self.gender = gender
        self.prevmedrcrds = prevmedrcrds

@app.route('/dashboardmnmg')
@is_logged_in
def dashboardmnmg():
    username = session['username']
    hospdata = db.session.query(Orders).all()
    db.session.commit()
    if hospdata is not None:
        for i in hospdata:
            return render_template('dashboardmnmg.html', profile = i.query.all())#statement is wrong
    else:
        return redirect(url_for('dashboardmnmg.html'))
    return render_template('dashboardmnmg.html') 

@app.route('/accepted/<username>')
@is_logged_in
def accepted(username):
    if db.session.query(Orders).filter(Orders.username_cust == username).count() > 0:
        acc_or_dec = "a"
        name_of_hptl_result = session['name']
        username_cust = username

        #send mail to that person!!!!! important
        user = db.session.query(CustomerDet).filter(CustomerDet.username == username).first()
        gmail_id = user.gmail_id

        smtp_ssl_host = 'smtp.gmail.com'
        smtp_ssl_port = 465
        username = 'zorg123546@gmail.com'
        password = 'zorg87654321'

        from_addr = 'zorg123546@gmail.com'
        to_addrs = gmail_id

        message = MIMEText(name_of_hptl_result+' has accepted to help you. They will arrive to your place soon.')
        message['subject'] = username
        message['from'] = from_addr
        message['to'] = ''.join(to_addrs)

        server = smtplib.SMTP_SSL(smtp_ssl_host, smtp_ssl_port)
        server.login(username, password)
        server.sendmail(from_addr, to_addrs, message.as_string())
        server.quit()

        #delete data from orders
        #add data to past orders
        data = PastOrders()
        flash('you have accepted to save '+username, 'success')
    return render_template('dashboardmnmg.html')

@app.route('/declined/<username>')
@is_logged_in
def declined(username):
    if db.session.query(Orders).filter(Orders.username_cust == username).count() > 0:
        acc_or_dec = "d"
        name_of_hptl_result = session['name']
        username_cust = username

        #send mail to that person!!!!! important
        user = db.session.query(CustomerDet).filter(CustomerDet.username == username).first()
        gmail_id = user.gmail_id

        smtp_ssl_host = 'smtp.gmail.com'
        smtp_ssl_port = 465
        username = 'zorg123546@gmail.com'
        password = 'zorg87654321'

        from_addr = 'zorg123546@gmail.com'
        to_addrs = gmail_id

        message = MIMEText(name_of_hptl_result+' has declined to help you. We are very sorry.')
        message['subject'] = username
        message['from'] = from_addr
        message['to'] = ''.join(to_addrs)

        server = smtplib.SMTP_SSL(smtp_ssl_host, smtp_ssl_port)
        server.login(username, password)
        server.sendmail(from_addr, to_addrs, message.as_string())
        server.quit()

        #delete data from orders
        flash('you have declined to save '+username, 'danger')
    return render_template('dashboardmnmg.html')

if __name__=='__main__':
    app.secret_key='secret123'
    app.run()

'''needed htmls
1)dashboardmnmg.html
2)not sure if we need accepted/declined.html
3)saved.html
4)not_saved.html
'''