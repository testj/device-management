#coding:utf-8

from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import desc,text,or_,and_
from flask import Flask
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
db.text_factory = str

def str_to_date(date_str,format="%Y-%m-%d %H:%M"):
    return datetime.strptime(date_str,format) if date_str is not None and len(date_str) != 0 else None

def date_to_str(dt,format="%Y-%m-%d %H:%M"):
    if dt is None or dt == '':
        return None
    elif not isinstance(dt,datetime):
        return None
        # raise TypeError('param is not a datetime object')
    return dt.strftime(format)

class Device(db.Model):
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    device_brand = db.Column(db.String(30),nullable=False)
    device_model = db.Column(db.String(40),nullable=False)
    system = db.Column(db.String(10),default="android")
    system_version = db.Column(db.String(10))
    amount = db.Column(db.Integer,default=1)
    create_time = db.Column(db.DateTime)
    screen_size = db.Column(db.String(10))
    resolution = db.Column(db.String(20))
    network_type = db.Column(db.String(30))
    remark = db.Column(db.Text)

    def __init__(self,_device_brand,_device_model,_system=None,
                 _system_version=None,_amount=None,_create_time=None,_screen_size=None,
                 _resolution = None,_network_type = None,_remark=None):
        self.device_brand = _device_brand
        self.device_model = _device_model
        self.system = _system
        self.system_version = _system_version
        self.amount = _amount
        self.create_time = _create_time
        self.screen_size = _screen_size
        self.resolution = _resolution
        self.network_type = _network_type
        self.remark = _remark

    def __repr__(self):
        return '<Device %r:%r>'%(self.device_brand,self.device_model)

class BorrowRecord(db.Model):
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    device_id = db.Column(db.Integer,nullable=False)
    tenant = db.Column(db.String(30),nullable=False)
    borrow_time = db.Column(db.DateTime,nullable=False)
    return_time = db.Column(db.DateTime)
    remark = db.Column(db.Text)

    def __init__(self,_device_id,_tenant,_borrow_time=None,_return_time=None,_remark=None):
        self.device_id = _device_id
        self.tenant = _tenant
        self.borrow_time = _borrow_time if _borrow_time is not None else datetime.now()
        self.return_time = _return_time
        self.remark = _remark

    def __repr__(self):
        return '<BorrowRecord %r:%r>'%(self.device_id,self.tenant)

if __name__ == '__main__':
    # device = Device("xiaomi","M1","android","4.0.2",1)
    # record = BorrowRecord(1,"tom",datetime.now())
    # db.session.add(record)
    # db.session.commit()
    # devices = Device.query.all()[0].id
    # print type(devices)
    # record=db.session.query(BorrowRecord).filter_by(id=1).first()
    # record.return_time=str_to_date('2016-07-10 12:03')
    # db.session.commit()
    # print Device.query.group_by(Device.system).all()
    # api.create(SQLALCHEMY_MIGRATE_REPO, 'database repository')
    print db.session.query(BorrowRecord).from_statement(
            text("SELECT * FROM borrow_record WHERE device_id=:id AND return_time \
            is NULL ORDER BY borrow_time DESC")).params(id=4).first().tenant
