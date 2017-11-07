# -*- coding: utf-8 -*- 
'''
Created on 2017年10月18日

@author: zty
'''

import time
import re
# import httplib    #python 2.7 
import http.client as httplib  #python 3
import operator #python3
import urllib
import json
import string

'''
题目类型
'''
class KnowledgeType():
    INVALID = 0
    SINGLE_CHOICE = 1   # 单选题
    MULTI_CHOICE = 2    # 多选题
    JUDGE = 3           # 判断题

'''
单条题目
'''
class Knowledge():
    type = KnowledgeType.INVALID    # KnowledgeType
    id = 0
    question = ''
    answer = ''
    answers = []
    
    def __init__(self, question = '', type = KnowledgeType.INVALID, answer = ''):
        self.type = int(type)    # KnowledgeType
        self.id = 0
        self.question = question
        if self.type is KnowledgeType.MULTI_CHOICE:
            self.answers = answer.split('; ')
            self.answer = ''
        else:
            self.answers = []
            self.answer = answer
        
    '''
    get answer by type, multi-answers split by '#'.
    '''
    def getAnswerString(self):
        if self.type is KnowledgeType.MULTI_CHOICE:
            return '; '.join(self.answers)
        elif self.type is KnowledgeType.INVALID:
            return ""
        else:
            return self.answer
    
    '''
    
    '''
    def getAnswer(self):
        if type is KnowledgeType.MULTI_CHOICE:
            return self.answers
        elif type is KnowledgeType.INVALID:
            return None
        else:
            return self.answer
    
    '''
           获取题目所有信息的字符串 
    '''
    def getAllInfo(self):
        info = 'id:' + str(self.id) + ' '
        info += 'type:' + str(self.type) + '\n'
        info += 'question:' + self.question + '\n'
        info += 'answers:' + self.getAnswerString() + '\n'
        return info
        
'''
从文件解析多选题题库
'''
def parseMultiChoiceKnowledgeFromDoc(file_path, need_to_store = False):
    if file_path is None:
        print ('[parseMultiChoiceKnowledgeFromDoc] file path is none!')
        return
    original_file = open(file_path, 'rb')
    if original_file is None:
        print ('[parseMultiChoiceKnowledgeFromDoc] open knowledge file faild! file name:', file_path)
        return
    begin_time = time.time()
    
    file_buf = original_file.read()
        
    (total_count, success_count) = parseMultiChoiceKnowledgeFromString(file_buf, need_to_store)

    original_file.close()
    end_time = time.time()
    print ('[parseMultiChoiceKnowledgeFromDoc] parse original knowledge file successfully, total line: ' + str(total_count) + ', success count: ' + str(success_count))
    print ('[parseMultiChoiceKnowledgeFromDoc] cost time: ' + str(end_time - begin_time))


'''
从字符串解析出多选题问答组。
'''
def parseMultiChoiceKnowledgeFromString(buf, need_to_store = False):
    if buf is None:
        print ('[parseMultiChoiceKnowledgeFromString] buf is none!')
        return (0, 0)
    
    begin_index = 0
    total_count = 0
    success_count = 0
    end_index = len(buf) - 1
#     print ('[parseMultiChoiceKnowledgeFromString] buf:', buf.decode('utf8'), "\n length:", end_index + 1)
    
    # 单个多选题的正则表达式
#     re_str = r'\D*(\d+)\.(\S*)\s*A\.(\S*)\s*B\.(\S*)\s*C\.(\S*)\s*D\.(\S*)\s*(E\.(\S*)\s*)?#{3}([A-E]*)'
    re_str = r'\D*(\d+)[\. ]+([\u4e00-\u9fa5|、，。：；？！“”《》（） ]*)\s*A[\. ]*([\u4e00-\u9fa5|、，。：；？！“”《》（）]*)\s*B[\. ]*([\u4e00-\u9fa5|、，。：；？！“”《》（）]*)\s*C[\. ]*([\u4e00-\u9fa5|、，。：；？！“”《》（）]*)\s*D[\. ]*([\u4e00-\u9fa5|、，。：；？！“”《》（）]*)\s*(E[\. ]*([\u4e00-\u9fa5|、，。：；？！“”《》（）]*)\s*)?#{3}([A-E]*)'
    
    # 将正则表达式编译成Pattern对象
    pattern = re.compile(re_str)
    while begin_index <= end_index:
        # 使用Pattern匹配文本，获得匹配结果，无法匹配时将返回None
        match = pattern.match(buf.decode('utf8')[begin_index:])
        total_count += 1
        if match:
            knowledge = Knowledge()
            knowledge.id = int(match.group(1))
            knowledge.question = match.group(2)
            knowledge.type = KnowledgeType.MULTI_CHOICE
            answer = match.group(9)
            l = list(answer)
            for char in l:
                if char is 'A':
                    knowledge.answers.append(match.group(3))
                elif char is 'B':
                    knowledge.answers.append(match.group(4))
                elif char is 'C':
                    knowledge.answers.append(match.group(5))
                elif char is 'D':
                    knowledge.answers.append(match.group(6))
                elif char is 'E':
                    knowledge.answers.append(match.group(8))
                else:
                    print ('[parseMultiChoiceKnowledgeFromString] match invalid answer char:', char)
                     
            success_count += 1
            begin_index += int(match.end(9))
#             print ('!!!!parsed one QA pair:', knowledge.getAllInfo(), 'success count:', success_count)
            
            if need_to_store:
                putIntoES(knowledge)
        else:
#             print ('match none')
            break
        
    return (total_count, success_count)


'''
从文件解析判断题题库
'''
def parseJudgeKnowledgeFromDoc(file_path, need_to_store = False):
    if file_path is None:
        print ('[parseJudgeKnowledgeFromDoc] file path is none!')
        return
    original_file = open(file_path, 'rb')
    if original_file is None:
        print ('[parseJudgeKnowledgeFromDoc] open knowledge file faild! file name:', file_path)
        return
    begin_time = time.time()
    
    file_buf = original_file.read()
        
    (total_count, success_count) = parseJudgeKnowledgeFromString(file_buf, need_to_store)

    original_file.close()
    end_time = time.time()
    print ('[parseJudgeKnowledgeFromDoc] parse original knowledge file successfully, total line: ' + str(total_count) + ', success count: ' + str(success_count))
    print ('[parseJudgeKnowledgeFromDoc] cost time: ' + str(end_time - begin_time))


'''
从字符串解析出判断题问答组。
'''
def parseJudgeKnowledgeFromString(buf, need_to_store = False):
    if buf is None:
        print ('[parseJudgeKnowledgeFromString] buf is none!')
        return (0, 0)
    
    begin_index = 0
    total_count = 0
    success_count = 0
    end_index = len(buf) - 1
#     print ('[parseJudgeKnowledgeFromString] buf:', buf.decode('utf8'), "\n length:", end_index + 1)
    
    # 判断题的正则表达式
    re_str = r'\D*(\d+)[\. ]+([\u4e00-\u9fa5|、，。：；？！“”《》（）\(\) ]*)\s*#{3}([TF]{1})'
    
    # 将正则表达式编译成Pattern对象
    pattern = re.compile(re_str)
    while begin_index <= end_index:
        # 使用Pattern匹配文本，获得匹配结果，无法匹配时将返回None
        match = pattern.match(buf.decode('utf8')[begin_index:])
        total_count += 1
        if match:
            knowledge = Knowledge()
            knowledge.id = int(match.group(1))
            knowledge.question = match.group(2)
            knowledge.type = KnowledgeType.JUDGE
            knowledge.answer = match.group(3)
                                 
            success_count += 1
            begin_index += int(match.end(3))
#             print ('!!!!parsed one QA pair:', knowledge.getAllInfo(), 'success count:', success_count)
            
            if need_to_store:
                putIntoES(knowledge)
        else:
#             print ('match none')
            break
        
    return (total_count, success_count)

    
# 把问答知识数据存入ES
def putIntoES(knowledge, ip = '172.23.27.171', port = 9200, index = 'party', type = 'smart'):
    if knowledge.question and (knowledge.answer or knowledge.answers):
        json_data = {"question" : knowledge.question, "answer" : knowledge.getAnswerString(), "model": str(knowledge.type)}
        data = json.dumps(json_data) # Encode the json_data
        
        headers = {"Content-type": "text/plain;charset=UTF-8"}
        
        url = '/' + index + '/' + type
        conn = httplib.HTTPConnection(ip, port)
        
        conn.request('POST', url, data, headers)
        httpres = conn.getresponse()
        
        if httpres.status in [200, 201]:
#             print ('[storeIntoES] return ok.', httpres.status, httpres.reason)
            conn.close()
            return True
        else:
            print ('[storeIntoES] return not ok.', httpres.status, httpres.reason)
            conn.close()
            return False
    else:
        print ('[storeIntoES] the Knowledge is invalid! info:', knowledge.getAllInfo())
        return False

# 从ES中查找答案
def searchFromES(question, ip = '172.23.27.171', port = 9200, index = 'party', type = 'smart'):
    if question:
        question = removeHTMLSpace(question)
        json_data = {"query" : {"match" : {"question" : question}}}
        data = json.dumps(json_data) # Encode the json_data
        
        headers = {"Content-type": "text/plain;charset=UTF-8"}
        
        url = '/' + index + '/' + type + '/_search'
        conn = httplib.HTTPConnection(ip, port)
        
        conn.request('POST', url, data, headers)
        httpres = conn.getresponse()
        
        if httpres.status != 200:
            print ('[searchFromES] return not ok,', httpres.status, httpres.reason)
            conn.close()
            return None
        else:
            resdata = httpres.read()
            conn.close()
#             print ('[searchFromES] return ok')
            result = json.loads(resdata)   # dict
            hits = result['hits']
            total = hits['total']
            sub_hits = hits['hits']
            source = sub_hits[0]['_source']
            question = source['question']
            answer = source['answer']
            type = int(source['model'])
            knowledge = Knowledge(question, type, answer)
            print ('[searchFromES] parse the answer:', knowledge.getAllInfo())
            return knowledge
    else:
        print ('[searchFromES] the question is null!')
        return None
    

# 从ES中查找答案，使用整句查询
'''
{
      "query": {
        "multi_match" : {
            "query": "党员领导干部违反有关规定干预和插手（ ）等活动，造成重大损失或者不良影响的，给予警告或者严重警告处分;情节较重的，给予撤销党内职务或者留党察看处分;情节严重的，给予开除党籍处分。",
            "fields": ["question"],
            "type": "phrase",
            "slop": 3
        }
    }
}
'''
def searchFromES2(question, ip = '172.23.27.171', port = 9200, index = 'party', type = 'smart'):
    if question:
        question = removeHTMLSpace(question)
        json_data = {"query" : {"multi_match" : {"query" : question, "fields": ["question"], "type": "phrase", "slop": 3}}}
        data = json.dumps(json_data) # Encode the json_data
        
        headers = {"Content-type": "text/plain;charset=UTF-8"}
        
        url = '/' + index + '/' + type + '/_search'
        conn = httplib.HTTPConnection(ip, port)
        
        conn.request('POST', url, data, headers)
        httpres = conn.getresponse()
        
        if httpres.status != 200:
            print ('[searchFromES2] return not ok,', httpres.status, httpres.reason)
            conn.close()
            return None
        else:
            resdata = httpres.read()
            conn.close()
#             print ('[searchFromES2] return ok')
            result = json.loads(resdata)   # dict
            hits = result['hits']
            total = hits['total']
            sub_hits = hits['hits']
            source = sub_hits[0]['_source']
            question = source['question']
            answer = source['answer']
            type = int(source['model'])
            knowledge = Knowledge(question, type, answer)
            print ('[searchFromES2] parse the answer:', knowledge.getAllInfo())
            return knowledge
    else:
        print ('[searchFromES2] the question is null!')
        return None
    
'''
[
{question: [answers]},
...
]
'''
def searchList(questions):
    for pair in questions:
        if pair:
            pair.autoGetAnswers()
    return


# 将字符串中的&nbsp;及其前面的字符去掉
def removeHTMLSpace(text):    
    if text:
        index = text.rfind('&nbsp;')
        if index >= 0:
            return text[index + len('&nbsp;'):]
    return text

myPunctuation = string.punctuation + ' ，。、《》？；‘’：“”【】{}！@#￥%……&*（）——~'

# 将字符串中的中英文标点去除并返回
def removePunctuation(text):
    return text.translate(str.maketrans('','',myPunctuation))


'''
寻找答案的问题类
'''
class Question():
    question = ''
    options = []
    question_type = ''
    rst_answers = []    #所有正确的答案
    rst_type = KnowledgeType.INVALID
    
    submit_choices = [] #选择题答案
    submit_judge = ''   #判断题答案
    unfound_list = []   #没能找到序号的答案
    
    def __init__(self, question = ''):
        self.question = question
        self.options = ['', '', '', '', '']
        self.question_type = ''
        self.rst_answers = []
        self.rst_type = KnowledgeType.INVALID
        self.submit_choices = []
        self.submit_judge = ''
        self.unfound_list = []
    
    '''
    从知识库找到正确的答案字符串
    '''
    def autoGetAnswers(self):
        knowledge = searchFromES2(self.question)
        if knowledge:
            self.rst_type = knowledge.type
            if knowledge.type is KnowledgeType.MULTI_CHOICE:
                self.rst_answers = knowledge.answers
            elif knowledge.type is KnowledgeType.SINGLE_CHOICE:
                self.rst_answers.append(knowledge.answer)
            elif knowledge.type is KnowledgeType.JUDGE:
                self.rst_answers.append(knowledge.answer)
            else:
                print ('[autoGetAnswers] get invalid knowledge typ:', str(knowledge.type))
            self.findSubmitAnswers()
            return True
        else:
            print ('[autoGetAnswers] cannot get the ansewr of', self.question)
            return False

    '''
    将答案字符串与选项匹配，得出答案选项，或记录未找到的正确答案
    '''
    def findSubmitAnswers(self):
        if self.rst_answers is None or self.options is None:
            print ('[findSubmitAnswers] answers or options is none!')
            return
        
        if self.rst_type in [KnowledgeType.MULTI_CHOICE, KnowledgeType.SINGLE_CHOICE]:
            
            for r in self.rst_answers:
                found = False
                o_index = -1
                for i in range(0, len(self.options) - 1):
                    if operator.eq(removePunctuation(self.options[i]), removePunctuation(r)):               ############ TODO:
                        self.submit_choices.append(chr(97 + i))
                        print('(', str(i), ')find choice:', chr(97 + i))
                        found = True
                        break
                    
                if found is False:
                    self.unfound_list.append(r)
                    
        elif self.rst_type is KnowledgeType.JUDGE:
            self.submit_judge = self.rst_answers[0]
        
        print('[findSubmitAnswers] submit_choice:', self.getSubmitAnsersString(), '\n\n')

    '''
    组装出最终答案选项
    '''
    def getSubmitAnsersString(self):
        s = ''
        if self.rst_type is KnowledgeType.JUDGE:
            s = self.submit_judge;
        elif self.rst_type in [KnowledgeType.MULTI_CHOICE, KnowledgeType.SINGLE_CHOICE]:
            self.submit_choices.sort()
            s = ''.join(self.submit_choices)
            if len(self.unfound_list) > 0:
                s += '，补充答案：'
                for unfound in self.unfound_list:
                    s += '； '.join(self.unfound_list)
                    
        return s
        
if __name__ == '__main__':
#     parseMultiChoiceKnowledgeFromDoc('./test1', True)
#     parseJudgeKnowledgeFromDoc('./test2', True)

#     k = Knowledge()
#     k.question = '今天天气是不是很好呀'
#     k.answer = 'sss'
#     k.type = KnowledgeType.SINGLE_CHOICE
#     putIntoES(k)

#     s = "中国共产党是中国工人阶级的先锋队，同时是中国人民和中华民族的先锋队，是中国特色社会主义事业的领导核心。"
#     searchFromES(s)
#     s = "党的十八大报告中提出的“坚定理想信念，坚守共产党人精神追求”要抓住的三个重要方面是（）"
#     searchFromES(s)
#     s = "十八大报告强调，要教育引导党员、干部模范践行社会主义荣辱观，讲党性、重品行、作表率，做（），以实际行动彰显共产党人的人格力量。"
#     searchFromES(s)
    
    q1 = "中国共产党是中国工人阶级的先锋队，同时是中国人民和中华民族的先锋队，是中国特色社会主义事业的领导核心。"
    option1 = ['正确', '错误']
    pair1 = Question(q1, option1)
    
    q2 = "违反有关规定从事营利活动，下列哪些行为情节较轻的，给予警告或者严重警告处分；情节较重的，给予撤销党内职务或者留党察看处分；情节严重的，给予开除党籍处分？"
    option2 = ['经商办企业或者从事有偿中介活动的', '拥有非上市公司（企业）的股份或者证券的', '买卖股票或者进行其他证券投资的', '在国（境）外注册公司或者投资入股的']
    pair2 = Question(q2, option2)
    
    searchList([pair1, pair2])
