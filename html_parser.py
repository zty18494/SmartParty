# -*- coding: utf-8 -*- 

'''
Created on 2017年10月19日

@author: zty
'''

import time
import re
import string
from doc_parser import Question

'''
从html文件解析题目
'''
def parseHTMLFile(file_path, need_to_answer = False):
    if file_path is None:
        print ('[parseHTMLFile] file path is none!')
        return
    original_file = open(file_path, 'r')
    if original_file is None:
        print ('[parseHTMLFile] open knowledge file faild! file name:', file_path)
        return
    begin_time = time.time()
    
    file_buf = original_file.read()
    total, success = parseHTMLBuf(file_buf, need_to_answer)

    original_file.close()
    end_time = time.time()
    print ('[parseHTMLFile] cost time: ' + str(end_time - begin_time), ', total:', total, ', succees:', success)


def parseHTMLBuf(buf, need_to_answer = False):
    if buf is None:
        return 0, 0
    
    pos_begin = 0    
    pos_end = len(buf)
    total_count = 0
    success_count = 0
    while pos_begin < pos_end:
        question, next_begin = parseOneQuestionFromHTML(buf, pos_begin)
        total_count += 1
        if question is None:
            break
        else:
            success_count += int(question.autoGetAnswers())
        pos_begin = next_begin
    
    return total_count, success_count


'''
<dt>题目</dt>

<label>选项</label>

选项格式：
<input type="checkbox" value="c" name="radios1">故意违纪受处分后又因故意违纪应当受到党纪处分的
<input type="radio" value="b" name="radios21">错误

</div></dd>    一题结束

Return: (Question, next_begin_index)
'''
def parseOneQuestionFromHTML(buf, begin = 0):
    if buf is None or begin >= len(buf):
        print ('[parseOneQuestionFromHTML] buf is none, or begin index over limit!')
        return (None, None)
    
    pos_begin = begin
    pos_end = len(buf)
    
    # PARSE TITLE
    title_begin = buf.find("<dt>", pos_begin) + len("<dt>")
    title_end = buf.find("</dt>", pos_begin)
    
    if title_begin == -1 or title_end == -1:
        print ('[parseOneQuestionFromHTML] cannot find <dt></dt>!')
        return (None, None)
    
    title = buf[title_begin : title_end]
    print ('[title]:', title)
    pos_begin = title_end + len("</dt>")
    question = Question(title)  # new a Question object
    
    # PARSE OPTIONS
    while pos_begin != buf.find("</div></dd>", pos_begin):
        option_begin = buf.find("<label>", pos_begin) + len("<label>")
        option_end = buf.find("</label>", pos_begin)
        
        if option_begin == -1 or option_end == -1:
            print ('[parseOneQuestionFromHTML] cannot find <label></label>!')
            return (None, None)
        
        big_option = buf[option_begin : option_end]
        option_string_begin = big_option.find('>') + 1
        option_string = big_option[option_string_begin : ]
        
        option_type = ''
        option_type_begin = big_option.find("type=") + len("type=\"")
        if big_option.find("checkbox", option_type_begin, option_string_begin):
            option_type = 'choice'
        elif big_option.find("radio", option_type_begin, option_string_begin):
            option_type = 'judge'
            
        option_value_begin = big_option.find("value=") + len("value=\"")
        option_value = ord(big_option[option_value_begin]) - ord('a')      ############## check
        
        question.options.insert(option_value - 1, option_string)
        question.question_type = option_type
        
        print ('[option] value:', str(option_value), 'string:', option_string)
        pos_begin = option_end + len("</label>")
        
    return (question, pos_begin)
    
if __name__ == '__main__':
    parseHTMLFile('./test3')
    
