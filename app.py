# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, abort, redirect, flash, url_for,session
import requests
from user_agents import parse
from werkzeug.contrib.cache import SimpleCache
cache = SimpleCache()

from utils import *
from filter import *
from datetime import datetime

import sys
reload(sys)
sys.setdefaultencoding('utf8')

#configuration
DEBUG = True
SECRET_KEY = 's<S>sda*(,112'
USERNAME = 'admin'
PASSWORD = 'YZtest,123'

app = Flask(__name__)
app.config.from_object(__name__)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html')

@app.route('/login',methods=['GET','POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME'] or request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid username or password'
        else:
            session['logged_in'] = True
            flash('You are login success')
            return redirect(url_for('show_devices'))
    return render_template('login.html',error =error)

@app.route('/logout')
def logout():
    session.pop('logged_in',None)
    flash('You were logged out')
    return redirect(url_for('show_devices'))

@app.route('/')
@app.route('/show_devices',methods=['GET','POST'])
def show_devices():
    if request.method == 'GET':
        result = Device.query.order_by(Device.system).all()
    elif request.method == 'POST':
        keyword = request.form.get('kw',None)
        print "keyword is",keyword,type(keyword)
        result = db.session.query(Device).from_statement(
            text("SELECT * FROM device WHERE device_brand like :kw or system_version like :kw or system like :kw \
            or screen_size like :kw or resolution like :kw or network_type like :kw")).\
            params(kw=u'%{}%'.format(keyword)).all()
    is_null=lambda x:x.tenant if x is not None else None
    devices = [dict(
        id=row.id,
        device_brand=row.device_brand,
        device_model=row.device_model,
        system=row.system,
        system_version=row.system_version,
        amount=row.amount,
        create_time=date_to_str(row.create_time),
        screen_size=row.screen_size,
        resolution=row.resolution,
        network_type=row.network_type,
        remark=row.remark,
        last_borrow = is_null(db.session.query(BorrowRecord).from_statement(
            text("SELECT * FROM borrow_record WHERE device_id=:id AND return_time \
            is NULL ORDER BY borrow_time DESC")).params(id=row.id).first())
    ) for row in result]
    return render_template('show_devices.html', devices=devices,now=date_to_str(datetime.now()))

@app.route('/add_device',methods=['POST'])
def add_device():
    not_null_dict = dict(device_brand=request.form['device_brand'],
                         device_model=request.form['device_model'],
                         system=request.form['system'],
                         system_version=request.form['system_version'],
                         amount=request.form['amount']
                         )
    check_null = not_null_filter(not_null_dict)
    if not check_null:
        device = Device(
            _device_brand=request.form['device_brand'],
            _device_model=request.form['device_model'],
            _system=request.form['system'],
            _system_version=request.form['system_version'],
            _amount=request.form['amount'],
            _create_time=str_to_date(request.form['create_time']),
            _screen_size=request.form['screen_size'],
            _resolution=request.form['resolution'],
            _network_type=request.form['network_type'],
            _remark=request.form['remark'],
        )
        db.session.add(device)
        db.session.commit()
        flash("New device create success posted!")
        return redirect(url_for('show_devices'))
    else:
        return redirect(url_for('show_devices'))

@app.route('/get_device/<device_id>',methods=['GET'])
def get_device(device_id):
    _device = Device.query.filter_by(id=device_id).first()
    device = dict(
        id=_device.id,
        device_brand=_device.device_brand,
        device_model=_device.device_model,
        system=_device.system,
        system_version=_device.system_version,
        amount=_device.amount,
        create_time=date_to_str(_device.create_time),
        screen_size=_device.screen_size,
        resolution=_device.resolution,
        network_type=_device.network_type,
        remark=_device.remark
    )
    return render_template('edit_devices.html', device=device)

@app.route('/update_device',methods=['POST'])
def update_device():
    _device = db.session.query(Device).filter_by(id=request.form['device_id']).first()
    _device.device_brand = request.form.get('device_brand',None)
    _device.device_model = request.form.get('device_model',None)
    _device.system = request.form.get('system',None)
    _device.system_version = request.form.get('system_version',None)
    _device.amount = request.form.get('amount',None)
    _device.create_time = str_to_date(request.form.get('create_time',None))
    _device.screen_size = request.form.get('screen_size',None)
    _device.resolution = request.form.get('resolution',None)
    _device.network_type = request.form.get('network_type',None)
    _device.remark = request.form.get('remark',None)
    db.session.commit()
    flash("Device has update success!")
    return redirect(url_for('show_devices'))


@app.route('/delete_device',methods=['POST'])
def delete_device():
    device = db.session.query(Device).filter_by(id=request.form['device_id'])
    device.delete()
    db.session.commit()
    flash("Delete Device success!")
    return redirect(url_for('show_devices'))

@app.route('/show_borrow_record/<device_id>',methods=['GET'])
def show_borrow_record(device_id):
    form = BorrowRecordForm(device_id=device_id,borrow_time=date_to_str(datetime.now()))
    result = BorrowRecord.query.filter_by(device_id=device_id).order_by(desc(BorrowRecord.borrow_time)).limit(3).all()
    if len(result) == 0:
        return render_template('show_borrow_record.html',records=[],form=form)
    records = [dict(
        id=cur.id,
        device_id=cur.device_id,
        tenant=cur.tenant,
        borrow_time=date_to_str(cur.borrow_time),
        return_time=date_to_str(cur.return_time),
        remark=cur.remark
    ) for cur in result]
    return render_template('show_borrow_record.html',records=records,form=form)

@app.route('/add_borrow_record',methods=['POST'])
def add_borrow_record():
    form = BorrowRecordForm(request.form)
    if request.method == 'POST' and form.validate():
        borrow_record = db.session.query(BorrowRecord).from_statement(
            text("SELECT * FROM borrow_record WHERE device_id=:device_id AND return_time IS NULL ORDER BY borrow_time DESC").\
            params(device_id=request.form.get('device_id'))
        ).first()
        print borrow_record
        if borrow_record:
            add_return_record(record_id=borrow_record.id)
        record = BorrowRecord(
            _device_id=form.device_id.data,
            _tenant=form.tenant.data,
            _borrow_time=str_to_date(form.borrow_time.data),
            _remark=form.remark.data
                              )
        db.session.add(record)
        db.session.commit()
        flash("New borrow record was success posted!")
        return redirect(url_for('show_borrow_record',device_id=request.form.get('device_id')))
    flash(str(form.errors.values().pop().pop()),category='error')
    return redirect(url_for('show_borrow_record',device_id=request.form.get('device_id')))


# @app.route('/add_borrow_record',methods=['POST'])
# def add_borrow_record():
#     not_null_dict = dict(device_id=request.form['device_id'],
#                          tenant=request.form['tenant'],
#                          borrow_time=str_to_date(request.form['borrow_time'])
#                          )
#     check_null = not_null_filter(not_null_dict)
#     if not check_null:
#         borrow_record = db.session.query(BorrowRecord).from_statement(
#             text("SELECT * FROM borrow_record WHERE device_id=:device_id AND return_time IS NULL").\
#             params(device_id=request.form.get('device_id'))
#         ).first()
#         print borrow_record
#         if borrow_record:
#             add_return_record(record_id=borrow_record.id)
#         record = BorrowRecord(
#             _device_id=request.form['device_id'],
#             _tenant=request.form['tenant'],
#             _borrow_time=str_to_date(request.form['borrow_time']),
#             _remark=request.form['remark']
#                               )
#         db.session.add(record)
#         db.session.commit()
#         flash("New borrow record was success posted!")
#         return redirect(url_for('show_borrow_record',device_id=request.form['device_id']))
#     else:
#         return redirect(url_for('show_borrow_record',device_id=request.form['device_id']))

@app.route('/delete_borrow_record/<device_id>/<record_id>',methods=['GET','DELETE'])
def delete_borrow_record(device_id,record_id):
    record = db.session.query(BorrowRecord).filter_by(id=record_id)
    record.delete()
    db.session.commit()
    flash("Delete borrow record success!")
    return redirect(url_for('show_borrow_record',device_id=device_id))

def add_return_record(record_id):
    record=db.session.query(BorrowRecord).filter_by(id=record_id).first()
    record.return_time=datetime.now()
    db.session.commit()
    print "update return time"

@app.route('/getprice',methods=['POST'])
def getprice():
    if request.method == "POST":
        sku_id = request.form['goodsId']
        sku_info = cache.get(sku_id)
        if sku_info is None:
            url = 'http://p.3.cn/prices/mgets?skuIds=J_{0}&type=1'.format(sku_id)
            r = requests.get(url)
            results = str(r.content)
            return results

if __name__ == '__main__':
    app.run(debug=True)
