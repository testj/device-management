#coding:utf-8
import os
from app import app
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

def runserver():
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(7000)
    IOLoop.instance().start()
    # port = int(os.environ.get('PORT', 6000))
    # flask_option=dict(
    #     host='0.0.0.0',
    #     debug=True,
    #     port=port,
    #     threaded=True
    # )
    # app.run(**flask_option)

if __name__ == '__main__':
    runserver()