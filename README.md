# SmartParty
smart tool to answer questions in monthly exam of party


## doc_parser.py
题库解析模块，包括多选题和判断题
* test1：  多选题测试文件
* test2：  判断题测试文件

## html_parser.py
问题（试卷）解析模块
* qut.html： 试卷测试文件

## http_server.py
http服务器，监听8000端口，并提供一个接口用以查询某试卷的答案

**接口示例**

POST http://172.23.195.106:8000/giveMeAnswer

{

"file_url":"http://172.23.195.106:9102/upload/others/2017-11/07/17477172216602303926272.html"

}

200 OK

{

    "total": 25,
    
    "success": 25,
    
    "answer": "1. abcd<br/>2. acd<br/>3. abcd<br/>4. abcd<br/>5. abd<br/>6. abcd<br/>7. abcd<br/>8. abcd<br/>9. abc<br/>10. bcd<br/>11. abcd<br/>12. abcd<br/>13. abcd<br/>14. abcd<br/>15. abcd<br/>16. T<br/>17. F<br/>18. F<br/>19. T<br/>20. T<br/>21. T<br/>22. T<br/>23. F<br/>24. T<br/>25. F<br/>"
    
}
