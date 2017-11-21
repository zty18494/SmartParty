# -*- coding: utf-8 -*- 

'''
Created on 2017年10月19日

@author: zty
'''

import time
import re
import os
import string
from doc_parser import Question
from urllib import request  # Python 3

save_dir = os.path.dirname(os.path.realpath(__file__)) + '/html_data'

'''
从指定链接下载文档到本地
from_url:    url
dest_path:   文件保存路径
'''


def downloadUrlFile(from_url, dest_path):
    with request.urlopen(from_url) as web:
        # 为保险起见使用二进制写文件模式，防止编码错误
        with open(dest_path, 'wb') as outfile:
            outfile.write(web.read())


'''
从html文件解析题目
Return: total_count, success_count, answer_list[]
'''


def parseHTMLFileByUrl(file_url, need_to_answer=False):
    if file_url is None:
        print('[parseHTMLFileByUrl] file url is none!')
        return

    if os.path.exists(save_dir) is False:
        os.makedirs(save_dir)

    file_path = save_dir + '/' + file_url.split('/')[-1]
    downloadUrlFile(file_url, file_path)
    print('download html file succeed, path:', file_path)
    return parseHTMLFile(file_path, need_to_answer)


'''
从html文件解析题目
Return: total_count, success_count, answer_list[]
'''


def parseHTMLFile(file_path, need_to_answer=False):
    if file_path is None:
        print('[parseHTMLFile] file path is none!')
        return
    original_file = open(file_path, 'r', encoding='utf8')
    if original_file is None:
        print('[parseHTMLFile] open knowledge file faild! file name:', file_path)
        return

    file_buf = original_file.read()
    original_file.close()
    return parseHTMLBuf(file_buf, need_to_answer)


'''
将html文本字符串解析，并寻找答案

Return: total_count, success_count, answer_list[]
'''
def parseHTMLBuf(buf, need_to_answer=False):
    if buf is None:
        return 0, 0, []

    begin_time = time.time()

    pos_begin = 0
    pos_end = len(buf)
    total_count = 0
    success_count = 0
    answers = []
    while pos_begin < pos_end:
        question, next_begin = parseOneQuestionFromHTML(buf, pos_begin)
        total_count += 1
        if question is None:
            break
        else:
            success_count += int(question.autoGetAnswers())
            answers.append(question.getSubmitAnsersString())
        pos_begin = next_begin

    end_time = time.time()
    print('[parseHTMLBuf] cost time: ' + str(end_time - begin_time), ', total:', total_count, ', succees:',
          success_count)
    return total_count, success_count, answers


def parseHTMLBuf2(buf, need_to_answer=False):
    '''
    解析HTML buffer，返回字典列表
    :param buf:
    :param need_to_answer:
    :return: [{'answer':'AB'}, {'answer':'ABC', 'unfound':'wwwww'}]
    '''
    if buf is None:
        return 0, 0, []

    begin_time = time.time()

    pos_begin = 0
    pos_end = len(buf)
    total_count = 0
    success_count = 0
    answers = []
    while pos_begin < pos_end:
        question, next_begin = parseOneQuestionFromHTML(buf, pos_begin)
        total_count += 1
        if question is None:
            break
        else:
            success_count += int(question.autoGetAnswers())
            aw, ex = question.getSubmitAnsersPair()
            if ex:
                answer = {'answer': aw, 'unfound': ex}
            else:
                answer = {'answer': aw}
            answers.append(answer)
        pos_begin = next_begin

    end_time = time.time()
    print('[parseHTMLBuf] cost time: ' + str(end_time - begin_time), ', total:', total_count, ', succees:',
          success_count)
    return total_count, success_count, answers


'''
<dt>题目</dt>

<label>选项</label>

选项格式：
<input type="checkbox" value="c" name="radios1">故意违纪受处分后又因故意违纪应当受到党纪处分的
<input type="radio" value="b" name="radios21">错误

</div></dd>    一题结束

Return: (Question, next_begin_index)
'''


def parseOneQuestionFromHTML(buf, begin=0):
    if buf is None or begin >= len(buf):
        print('[parseOneQuestionFromHTML] buf is none, or begin index over limit!')
        return (None, None)

    pos_begin = begin
    pos_end = len(buf)

    # PARSE TITLE
    title_begin = buf.find("<dt>", pos_begin) + len("<dt>")
    title_end = buf.find("</dt>", pos_begin)

    if title_begin == -1 or title_end == -1:
        print('[parseOneQuestionFromHTML] cannot find <dt></dt>!')
        return (None, None)

    title = buf[title_begin: title_end]
    print('[title]:', title)
    pos_begin = title_end + len("</dt>")
    question = Question(title)  # new a Question object

    # PARSE OPTIONS
    option_count = 0
    while pos_begin != buf.find("</div></dd>", pos_begin):
        option_begin = buf.find("<label>", pos_begin) + len("<label>")
        option_end = buf.find("</label>", pos_begin)

        if option_begin == -1 or option_end == -1:
            print('[parseOneQuestionFromHTML] cannot find <label></label>!')
            return (None, None)

        big_option = buf[option_begin: option_end]
        option_string_begin = big_option.find('>') + 1
        option_string = big_option[option_string_begin:]

        option_type = ''
        option_type_begin = big_option.find("type=") + len("type=\"")
        if big_option.find("checkbox", option_type_begin, option_string_begin):
            option_type = 'choice'
        elif big_option.find("radio", option_type_begin, option_string_begin):
            option_type = 'judge'

        # option_value_begin = big_option.find("value=") + len("value=\"")

        #         option_value = ord(big_option[option_value_begin]) - ord('a')      ############## check
        #         option_dict[]

        question.options[option_count] = option_string
        question.question_type = option_type
        print('[option] index:', option_count, ', string:', option_string)
        option_count += 1
        pos_begin = option_end + len("</label>")

    return (question, pos_begin)


'''
============= unit tests ================
'''


def testParseHTMLFileByUrl():
    url = 'http://localhost:8000/qut.html'
    parseHTMLFileByUrl(url)


def testParseHTMLFile():
    #     file = './test3'
    file = './qut.html'
    parseHTMLFile(file)


if __name__ == '__main__':
    #     testParseHTMLFile()
    testParseHTMLFileByUrl()
