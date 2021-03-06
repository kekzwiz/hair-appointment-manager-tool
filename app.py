import os
import re
from flask import Flask, request, render_template 
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = '' #heroku postgresql uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

headings = ("Client Name", "Phone Number", "Payment Method", "Date", "Time", "Service", "Stylist")

clients = []
numbers = []
paymentmethods = []
dates = []
times = []
services = []
stylists = []


class Client(db.Model):
    __tablename__ = 'client'
    cid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    phone_number = db.Column(db.String(10))
    payment_method = db.Column(db.String(6))

    def __init__(self, name, phone_number, payment_method):
        self.name = name
        self.phone_number = phone_number
        self.payment_method = payment_method

class Appointment(db.Model):
    __tablename__ = 'appointment'
    apid = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date())
    time = db.Column(db.Time())
    service = db.Column(db.String(20))

    def __init__(self, date, time, service):
        self.date = date
        self.time = time
        self.service = service

class Schedules(db.Model):
    __tablename__ = 'schedules'
    id = db.Column(db.Integer, primary_key=True)
    cid = db.Column(db.Integer, db.ForeignKey(Client.cid))
    apid = db.Column(db.Integer, db.ForeignKey(Appointment.apid))
    
    def __init__(self, cid, apid):
        self.cid = cid
        self.apid = apid

class Stylist(db.Model):
    __tablename__ = 'stylist'
    sid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    expertise = db.Column(db.String(50))

    def __init__(self, sid, name, expertise):
        self.sid = sid
        self.name = name
        self.expertise = expertise 

class Scheduled(db.Model):
    __tablename__ = 'scheduled'
    id = db.Column(db.Integer, primary_key=True)
    sid = db.Column(db.Integer, db.ForeignKey(Stylist.sid))
    apid = db.Column(db.Integer, db.ForeignKey(Appointment.apid))

    def __init__(self, sid, apid):
        self.sid = sid
        self.apid = apid

class Service(db.Model):
    __tablename__ = 'service'
    serid = db.Column(db.Integer, primary_key=True)
    style = db.Column(db.String(20))

    def __init__(self, serid, style):
        self.serid = serid
        self.style = style

class Offers(db.Model):
    __tablename__ = 'offers'
    id = db.Column(db.Integer, primary_key=True)
    sid = db.Column(db.Integer, db.ForeignKey(Stylist.sid))
    serid = db.Column(db.Integer, db.ForeignKey(Service.serid))

    def __init__(self, sid, serid):
        self.sid = sid
        self.serid = serid

class Haircut(db.Model):
    __tablename__ = 'haircut'
    serid = db.Column(db.Integer, primary_key=True)
    style = db.Column(db.String(20))

    def __init__(self, serid, style):
        self.serid = serid
        self.style = style

class ColoringSession(db.Model):
    __tablename__ = 'coloringsession'
    serid = db.Column(db.Integer, primary_key=True)
    materials = db.Column(db.String(200))

    def __init__(self, serid, materials):
        self.serid = serid
        self.materials = materials


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def back():
    return render_template('index.html')

@app.route('/add', methods=['POST'])
def add():
    return render_template('add.html')

@app.route('/delete', methods=['POST'])
def delete():
    return render_template('delete.html')

@app.route('/deleted', methods=['POST'])
def deleted():
    if request.method == 'POST':
        client = request.form['client']
        number = request.form['phone_number']
        print('does it work?')
        delete = Client.query.filter_by(phone_number=number).delete()
        db.session.commit()
        print('working yet?')
        for i in numbers:
            if (numbers[i] == number):
                clients.remove(i)
                numbers.remove(i)
                paymentmethods.remove(i)
                dates.remove(i)
                times.remove(i)
                services.remove(i)
                stylists.remove(i)
        print('now?')
        if client == '' or number == '':
            return render_template('home.html', alert='Enter the required fields to progress')
        return render_template('deleted.html', len=len(clients), headings=headings, clients=clients,
        numbers=numbers, paymentmethods=paymentmethods, dates=dates, times=times,
        services=services, stylists=stylists)

@app.route('/complete', methods=['POST'])
def complete():
    if request.method == 'POST':
        client = request.form['client']
        phone_number = request.form['phone_number']
        payment_method = request.form['payment_method']
        print(client, phone_number, payment_method)
        client_data = Client(client, phone_number, payment_method)
        db.session.add(client_data)
        db.session.commit()

        clients.append(client)
        numbers.append(phone_number)
        paymentmethods.append(payment_method)

        date = request.form['date']
        time = request.form['time']

        dates.append(date)
        times.append(time)
        
        if (int(request.form['service']) >= 401 and int(request.form['service']) <= 405):
            service = 'Haircut'
            serid = int(request.form['service'])
        elif (int(request.form['service']) >= 501 and int(request.form['service']) <= 505):
            service = 'ColoringSession'
            serid = int(request.form['service'])

        services.append(service)

        appointment_data = Appointment(date, time, service)
        db.session.add(appointment_data)
        db.session.commit()

        get_client_id = Client.query.filter_by(name=client).first()
        get_appointment_id = Appointment.query.filter_by(date=date).first()

        schedules_data = Schedules(get_client_id.cid, get_appointment_id.apid)
        db.session.add(schedules_data)
        db.session.commit()

        if (int(request.form['stylist']) == 201):
            stylist = 'Clowney Pennywise'
            sid = 201
        if (int(request.form['stylist']) == 202):
            stylist = 'Edward S. Hands'
            sid = 202
        if (int(request.form['stylist']) == 203):
            stylist = 'Stylist Joe'
            sid = 203
        if (int(request.form['stylist']) == 301):
            stylist = 'John Bows'
            sid = 301
        if (int(request.form['stylist']) == 302):
            stylist = 'Miranda Cosgrove'
            sid = 302
        if (int(request.form['stylist']) == 303):
            stylist = 'Missy Andrews'
            sid = 303

        stylists.append(stylist)

        print(date, time, service, stylist, sid)

        scheduled_data = Scheduled(sid, get_appointment_id.apid)
        db.session.add(scheduled_data)
        db.session.commit()

        offers_data = Offers(sid, serid)
        db.session.add(offers_data)
        db.session.commit()

        if client == '' or phone_number == '' or payment_method == '' or date == '' or stylist == '':
            return render_template('home.html', alert='Enter the required fields to progress')
        return render_template('complete.html', len=len(clients), headings=headings, clients=clients,
        numbers=numbers, paymentmethods=paymentmethods, dates=dates, times=times,
        services=services, stylists=stylists)


if __name__ == '__main__':
    app.run(debug=True)
