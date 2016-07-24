# -*- coding: utf-8 -*-

from datetime import datetime
from wtforms import Form,TextField,validators,StringField,ValidationError

def DateRequired(form,field,_format="%Y-%m-%d %H:%M"):
    try:
        datetime.strptime(field.data,_format)
    except Exception:
        raise ValidationError(u"日期格式错误,格式为[{}]".format(_format))

class NotNullError(Exception):
    def __init__(self,key,value):
        self.key = key
        self.value = value
    def __str__(self):
        return repr("{} can not be empty!".format(self.key))

def not_null_filter(params_dict=None):
    for key,value in params_dict.items():
        if isinstance(value,basestring):
            if value is None or value.strip() == '':
                return "{} can not be empty!".format(key)
        else:
            if value is None:
                return "{} can not be empty!".format(key)
    return False

class BorrowRecordForm(Form):
    device_id = StringField(u'设备ID',[validators.DataRequired(message=u"设备id不能为空")])
    tenant = StringField(u'租用者',[validators.Length(min=2,max=20,message=u"租用者姓名长度过短")])
    borrow_time = StringField(u'借用时间',[DateRequired])
    remark = StringField(u'备注')

if __name__ == '__main__':
    form = BorrowRecordForm(device_id="a",tenant="aa",borrow_time="19")
    print form.validate(),form.errors


