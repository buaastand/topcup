import os
from wsgiref.simple_server import make_server


def application(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/html')])
    # os.system('git add -A')
    # os.system('git commit -m "merge"')
    os.system("python ../manage.py collectstatic")
    os.system('git pull origin master')
    os.system('uwsgi --reload ~/uwsgi/uwsgi.pid')
    print('git pull finish')
    return [b'Hello, webhook!']

httpd = make_server('', 8001, application)
print('Serving HTTP on port 8001...')
# 开始监听HTTP请求:
httpd.serve_forever()
