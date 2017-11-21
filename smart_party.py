# -*- coding: utf-8 -*-
'''
Created on 2017年10月19日

@author: zty
'''

from http.server import BaseHTTPRequestHandler, HTTPServer
from os import path
from urllib.parse import urlparse
import json
import html_parser

curdir = path.dirname(path.realpath(__file__))
sep = '/'
print('curdir:', curdir)

# MIME-TYPE
mimedic = [
    ('.html', 'text/plain'),
    ('.js', 'application/javascript'),
    ('.json', 'application/json'),
    ('.txt', 'text/plain'),
    ('', 'text/plain')
]

def errorResp(code = -1, reason = 'UNKNOWN ERROR'):
    '''
    返回通用异常响应json字符串
    :param code:
    :param reason:
    :return:
    '''
    resp_json = {'errorCode': code, 'errorReason': reason}
    return json.dumps(resp_json)


def handleGiveMeAnswer(post_body):
    '''
    根据url下载html文件，返回供web端显示的答案
    :param post_body:
    :return:
    '''
    print('[giveMeAnswer] receive body:', post_body)
    req_json = json.loads(post_body)
    if req_json:
        file_url = req_json['file_url']
        if not file_url:
            return errorResp(reason='FILE URL INVALID')
        total_count, success_count, answer_list = html_parser.parseHTMLFileByUrl(file_url)
        print('[giveMeAnswer] succeed to deal file:', file_url, ', total:', total_count, ', success:',
              success_count)
        answer_str = ''
        for i in range(0, len(answer_list)):
            answer_str += str(i + 1) + '. '
            answer_str += answer_list[i] + '<br/>'
        resp_json = {'total': total_count - 1, 'success': success_count, 'answer': answer_str}
        return json.dumps(resp_json)
    else:
        return errorResp(reason='BODY INVALID')

def handleGiveMeAnswerByBuf(post_body):
    '''
    POST请求消息体包含html文件全部内容，返回答案列表
    :param post_body:
    :return:
    '''
    if post_body:
        total_count, success_count, answer_list = html_parser.parseHTMLBuf2(post_body.decode('utf-8'))
        print('[handleGiveMeAnswerByBuf] succeed to deal buf:', post_body, ', total:', total_count, ', success:',
              success_count)
        resp_json = {'total': total_count - 1, 'success': success_count, 'answer': answer_list}
        return json.dumps(resp_json)
    else:
        return errorResp(reason='BODY INVALID')

class MyHttpRequestHandler(BaseHTTPRequestHandler):
    # GET
    def do_GET(self):
        querypath = urlparse(self.path)
        filepath, query = querypath.path, querypath.query

        if filepath.endswith('/'):
            filepath += 'index.html'

        filename, fileext = path.splitext(filepath)
        mimetype = None
        for e in mimedic:
            if e[0] == fileext:
                mimetype = e[1]

        if True:
            try:
                with open(path.realpath(curdir + sep + filepath), 'rb') as f:
                    content = f.read()
                    self.send_response(200)
                    if mimetype:
                        self.send_header('Content-type', mimetype)
                    self.end_headers()
                    self.wfile.write(content)
            except IOError:
                self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        querypath = urlparse(self.path)
        interface_path = querypath.path
        print('interface:', interface_path)

        path_split = interface_path.split('/')

        if len(path_split) <= 0:
            resp_body = errorResp(reason='URL INVALID')
        elif path_split[-1] == 'giveMeAnswer':
            content_len = int(self.headers.get('content-length', 0))
            post_body = self.rfile.read(content_len)
            print('[giveMeAnswer] receive body:', post_body)
            resp_body = handleGiveMeAnswer(post_body)
        elif path_split[-1] == 'giveMeAnswerByBuf':
            content_len = int(self.headers.get('content-length', 0))
            post_body = self.rfile.read(content_len)
            print('[giveMeAnswerByBuf] receive body:', post_body)
            resp_body = handleGiveMeAnswerByBuf(post_body)
        else:
            resp_body = errorResp(reason='UNKNOWN REQUEST')

        try:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(resp_body.encode())
        except IOError:
            self.send_error(500, 'io wrong')


def run():
    port = 8000
    print('starting server, port', port)
    # Server settings
    server_address = ('', port)
    httpd = HTTPServer(server_address, MyHttpRequestHandler)
    print('running server...')
    httpd.serve_forever()



if __name__ == '__main__':
    run()
