'''
Created on 2019年5月22日
2019年6月10日：更新到V0.3增加专题班学习功能

@author: WangBowen
'''
import sys
import re
from PIL import Image 
import requests
import js2py
import json
import random
import time
import datetime
from io import BytesIO
from bs4 import BeautifulSoup 
from PyQt5.QtCore import pyqtSignal,QThread
from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, 
    QTextEdit, QGridLayout, QApplication, QPushButton)
from PyQt5.QtGui import  QPixmap,QIcon
from PIL.ImageQt import ImageQt

class FormGridLayout(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        self.usr = QLabel('用户名：')
        self.pwd = QLabel('密码：')
        self.yzm = QLabel('验证码：')
        self.yzmPic = QLabel('')
        self.log = QLabel('日志')
        self.bt1 = QPushButton('登录')
        self.bt1.clicked.connect(self.tryLogin)
        self.bt2 = QPushButton('学习必修课')
        self.bt2.clicked.connect(self.startLearnBx)
        self.bt3 = QPushButton('学习选修课')
        self.bt3.clicked.connect(self.startLearnXx)
        self.bt4 = QPushButton('学习专题班')
        self.bt4.clicked.connect(self.startLearnZt)

        self.usrEdit = QLineEdit()
        self.pwdEdit = QLineEdit()
        self.yzmEdit = QLineEdit()
        self.logEdit = QTextEdit()

        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(self.usr, 1, 0)
        grid.addWidget(self.usrEdit, 1, 1)
        grid.addWidget(self.pwd, 1, 2)
        grid.addWidget(self.pwdEdit, 1, 3)
        
        grid.addWidget(self.yzm, 2, 0)
        grid.addWidget(self.yzmEdit, 2, 1)
        grid.addWidget(self.yzmPic, 2, 2)
        grid.addWidget(self.bt1, 2, 3)
        
        grid.addWidget(self.bt2, 3, 1)
        grid.addWidget(self.bt3, 3, 3)
        
        grid.addWidget(self.bt4, 4, 1)

        grid.addWidget(self.log, 5, 0)
        grid.addWidget(self.logEdit, 5, 1, 5, 3)

        self.setLayout(grid) 

        self.setGeometry(300, 300, 450, 350)
        self.setWindowTitle('安徽干部教育在线--学习辅助系统V0.3--作者：wbw')  
        self.setWindowIcon(QIcon('bw.png'))  
        self.show()
        self.bt2.setDisabled(True)
        self.bt3.setDisabled(True)
        self.bt4.setDisabled(True)
        self.getYzm()
        
    def appendLog(self, str1):
        self.logEdit.append(str1)
        if(str1 == '学习结束，请到www.ahgbjy.gov.cn进行考试~'):
            self.bt2.setDisabled(False)
            self.bt3.setDisabled(False)
            self.bt4.setDisabled(False)
        QApplication.processEvents()
        
    def getYzm(self):
        global browser,headers
        browser = requests.session()
        url = 'http://www.ahgbjy.gov.cn/CheckCode.aspx?id=%d' %(random.randint(333333333,699999999))#验证码地址
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
        resp = browser.get(url, headers=headers)
        #把图片转化成流，用Image打开，再保存为QImage，最后使用QPixmap显示到界面，规避了保存图片文件的步骤
        BytesIOObj = BytesIO()
        BytesIOObj.write(resp.content)
        img = Image.open(BytesIOObj)
        img = img.convert("RGBA")
        qim = ImageQt(img)
        pixmap = QPixmap.fromImage(qim)
#         img.save('yzm.png')
#         print(img)
#         pixmap = QPixmap()
#         pixmap.load('yzm.png')
#       pixmap.loadFromData(resp.content)#打包成exe不生效
        self.yzmPic.setPixmap(pixmap)
        
    #登录系统
    def tryLogin(self):
        self.logEdit.append("----------开始登录----------")
        self.bt1.setDisabled(True)
        self.logEdit.append("用户名："+self.usrEdit.text()+"，密码："+self.pwdEdit.text()+",验证码："+self.yzmEdit.text())
        if(self.usrEdit.text().strip() == ''):
            self.appendLog("----------登录失败，用户名不能为空----------")
            self.bt1.setDisabled(False)
            return
        if(self.pwdEdit.text().strip() == ''):
            self.appendLog("----------登录失败，密码不能为空----------")
            self.bt1.setDisabled(False)
            return
        if(self.yzmEdit.text().strip() == ''):
            self.appendLog("----------登录失败，验证码不能为空----------")
            self.bt1.setDisabled(False)
            return
        url = 'http://www.ahgbjy.gov.cn/Login.aspx'#登录地址
        #登录信息会变，目前还没找到规律
        #从网站先获取__VIEWSTATE和__VIEWSTATE1等状态位
        resp = browser.get(url, headers = headers).content.decode('utf-8')
        soup = BeautifulSoup(resp,'html.parser')
        __VIEWSTATEFIELDCOUNT = soup.select('#__VIEWSTATEFIELDCOUNT')[0]['value']
        if(__VIEWSTATEFIELDCOUNT == '2'):
            form = {
            '__VIEWSTATEFIELDCOUNT':__VIEWSTATEFIELDCOUNT,
            '__VIEWSTATE':soup.select('#__VIEWSTATE')[0]['value'],
            '__VIEWSTATE1':soup.select('#__VIEWSTATE1')[0]['value'],
            'ctl00$ContentPlaceHolder1$txt_UserAccount':self.getDes(self.usrEdit.text().strip()),
            'ctl00$ContentPlaceHolder1$txt_Password':self.getDes(self.pwdEdit.text().strip()),
            'ctl00$ContentPlaceHolder1$CheckCode':self.yzmEdit.text().strip(),
            'ctl00$ContentPlaceHolder1$btn_Login':'登录'
            }
        elif(__VIEWSTATEFIELDCOUNT == '3'):
            form = {
            '__VIEWSTATEFIELDCOUNT':__VIEWSTATEFIELDCOUNT,
            '__VIEWSTATE':soup.select('#__VIEWSTATE')[0]['value'],
            '__VIEWSTATE1':soup.select('#__VIEWSTATE1')[0]['value'],
            '__VIEWSTATE2':soup.select('#__VIEWSTATE2')[0]['value'],
            '__VIEWSTATEGENERATOR':soup.select('#__VIEWSTATEGENERATOR')[0]['value'],
            'ctl00$ContentPlaceHolder1$txt_UserAccount':self.getDes(self.usrEdit.text().strip()),
            'ctl00$ContentPlaceHolder1$txt_Password':self.getDes(self.pwdEdit.text().strip()),
            'ctl00$ContentPlaceHolder1$CheckCode':self.yzmEdit.text().strip(),
            'ctl00$ContentPlaceHolder1$btn_Login':'登录'
            }
        else:
            self.appendLog("----------登录失败，请联系软件作者----------")
            return
        #开始执行登录，成功则获取用户姓名
        resp = browser.post(url, headers = headers,data=form).content.decode('utf-8')
        url = 'http://www.ahgbjy.gov.cn/'
        resp = browser.get(url, headers = headers).content.decode('utf-8')
        soup = BeautifulSoup(resp,'html.parser')
        xm = soup.select('strong.username')
        if(len(xm) > 0):
            self.appendLog("----------登录成功，姓名：%s----------"%(xm[0].text))
            self.bt2.setDisabled(False)
            self.bt3.setDisabled(False)
            self.bt4.setDisabled(False)
            self.usrEdit.setDisabled(True)
            self.pwdEdit.setDisabled(True)
            self.yzmEdit.setDisabled(True)
        else:
            self.appendLog("----------登录失败，请核对信息后重试----------")
            print(resp)
            self.bt1.setDisabled(False)
            self.getYzm()
            return
            
    #开始自动学习必修课
    def startLearnBx(self):
        self.appendLog("\r----------获取必修课程----------")
        url = 'http://lms.ahgbjy.gov.cn/Personal/AnnualPlan'
        resp = browser.get(url, headers = headers).content.decode('utf-8')
        soup = BeautifulSoup(resp,'html.parser')
        table = soup.find('div', id='table_BX')
        if table is None:
            self.appendLog("----------没有必修课程----------")
            return
        a_bx_list = table.findAll('a',href=re.compile('http:\/\/static.ahgbjy'))
        course_bx_list = []
        for a in a_bx_list:
            self.appendLog(a['title'])
            course_bx_list.append(Course(a['title'],a['href']))
        self.appendLog("\r----------开始自动学习必修课----------")
        self.bt2.setDisabled(True)
        self.bt3.setDisabled(True)
        self.bt4.setDisabled(True)
        self.learnThread = LearnThread(course_bx_list)
        self.learnThread.trigger.connect(self.appendLog)
        self.learnThread.start()
        
    #开始自动学习必修课
    def startLearnXx(self):
        self.appendLog("\r----------获取选修课程----------")
        url = 'http://lms.ahgbjy.gov.cn/Personal/AnnualPlan'
        resp = browser.get(url, headers = headers).content.decode('utf-8')
        soup = BeautifulSoup(resp,'html.parser')
        table = soup.find('div', id='table_XX')
        if table is None:
            self.appendLog("----------没有选修课程----------")
            return
        a_xx_list = table.findAll('a',href=re.compile('http:\/\/static.ahgbjy'))
        course_xx_list = []
        for a in a_xx_list:
            self.appendLog(a['title'])
            course_xx_list.append(Course(a['title'],a['href']))
        self.appendLog("\r----------开始自动学习选修课----------")
        self.bt2.setDisabled(True)
        self.bt3.setDisabled(True)
        self.bt4.setDisabled(True)
        self.learnThread = LearnThread(course_xx_list)
        self.learnThread.trigger.connect(self.appendLog)
        self.learnThread.start()

    #开始自动学习专题班
    def startLearnZt(self):
        self.appendLog("\r----------获取专题班课程----------")
        url = 'http://www.ahgbjy.gov.cn/Class/'
        resp = browser.get(url, headers = headers).content.decode('utf-8')
        soup = BeautifulSoup(resp,'html.parser')
        div = soup.find('div', id='ctl00_ContentPlaceHolder1_my_Class')
        ztb_list = div.findAll('a', href=re.compile('http:\/\/lms\.ahgbjy\.gov\.cn\/Class\/loadclass'))
        course_zt_list = []
        if len(ztb_list) == 0:
            self.appendLog("----------没有已选专题班----------")
            return
        for ztb in ztb_list:
            self.appendLog('专题班：%s——————'%ztb.text)
            resp = browser.get(ztb['href'], headers=headers).content.decode('utf-8')
            soup = BeautifulSoup(resp,'html.parser')
            a_zt_list = soup.findAll('a',href=re.compile('http:\/\/static.ahgbjy'))
            for a in a_zt_list:
                self.appendLog(a['title'])
                course_zt_list.append(Course(a['title'],a['href']))
        self.appendLog("\r----------开始自动学习专题班----------")
        self.bt2.setDisabled(True)
        self.bt3.setDisabled(True)
        self.bt4.setDisabled(True)
        self.learnThread = LearnThread(course_zt_list)
        self.learnThread.trigger.connect(self.appendLog)
        self.learnThread.start()
    
    #因网站使用了自有的加密算法，故利用js2py插件包直接使用原网站的js代码进行加密
    #js2py的用法为在js末端加入要执行的主函数及参数，调用eval_js即可
    def getDes(self,pwd):
        url = 'http://www.ahgbjy.gov.cn/Js/des.js'
        resp = browser.get(url, headers=headers).content.decode('utf-8')
        js = resp + "\r encMe('" + pwd + "','')"
        return js2py.eval_js(js)

        
class Course:
    def __init__(self, name, url):
        self.name = name
        self.url = url

# 增加了一个继承自QThread类的类，重新写了它的run()函数
# run()函数即是新线程需要执行的：执行一个循环；发送计算完成的信号。
class LearnThread(QThread):
    trigger = pyqtSignal(str)
    def __init__(self, course_list):
        super().__init__()
        self.course_list = course_list
    def run(self):
        #self.appendLog("学习:%s----------" %(course_bx_list[0].name))
        # 循环完毕后发出信号
        for j in range(len(self.course_list)):
            self.trigger.emit("学习:%s----------" %(self.course_list[j].name))
            finish = 1 #标志位，是否学习完成，0为完成，1未完成
            count_100 = 0 #当前课程章节学习完成数
            global totalTime
            pxbid = re.search('(?<=pxbid\=).*', self.course_list[j].url)
            while finish == 1: #无限循环，每次学习后重新获取学习进度，直到全部学完，主动break
                resp = browser.get(self.course_list[j].url, headers = headers)
                #print(resp.content.decode('utf-8'))
                soup = BeautifulSoup(resp.content.decode('utf-8'),'html.parser')
                table = soup.find('table',class_='comments_on')
                #如果没有子课程，执行如下（改版后好像没有这种情况了）
                if table is None:
                    p100 = re.search('(?<=<span id=\"sp_Progress\">).*?(?=<\/span>)', resp.content.decode('utf-8')).group(0)
                    self.trigger.emit('当前进度为——%s'%(p100))
                    if(p100.strip() == '100%'):
                        self.trigger.emit("----------%s学习完成----------" %(self.course_list[j].name))
                        break
                    totalTime = '300'#网站改版，暂时设置为5分钟总时长
                    bcid = re.search('(?<=keyID = \").*?(?=\";)', resp.content.decode('utf-8')).group(0)
                    cid = '00000000-0000-0000-0000-000000000000'
                    self.playVideo(bcid,cid)
                    continue #继续执行下一轮学习
                #如果有子课程，执行如下
                tr_list = table.findAll('tr')
                if(count_100 ==(len(tr_list)-1)): #当所有章节为100%，退出无限循环
                    self.trigger.emit("----------%s学习完成----------" %(self.course_list[j].name))
                    break
                count_100 = 0 #当前课程章节学习完成数，清零
                for tr in tr_list: #获取所有章节情况，跳过标题th行
                    flag = 1#用于跳过th行
                    td_list = tr.findAll('td')
                    if(len(td_list) == 0):
                        flag = 0
                    for i in range(len(td_list)):
                        if(i==1):
                            self.trigger.emit('学习章节——%s'%(td_list[i].text.strip()))
                        if(i==2):
                            m = re.search('\d*?(?=分钟)', td_list[i].text.strip()).group(0)
                            h = re.search('\d*?(?=小时)', td_list[i].text.strip())
                            if h is not None:
                                totalTime = str(int(m) + int(h.group(0))*60)
                            else:
                                totalTime = str(random.randint(30,int(m)*60))
                        if(i==5):
                            self.trigger.emit('章节总时间为——%s分钟，当前进度为——%s'%(m, td_list[i].text.strip()))
                            if(td_list[i].text.strip() == '100%'):
                                self.trigger.emit('学习已完成，跳过此章节')
                                flag = 0
                                count_100 += 1
                    if(flag == 0):
                        continue
                    course_open_str = re.search('javascript:openCourse(.*?);', str(tr)).group(0)
                    #print(course_open_str)
                    bcid = re.search('(?<=\(\').*?(?=\'\,)', course_open_str).group(0)
                    cid = re.search('(?<=\,\').*?(?=\'\))', course_open_str).group(0)
                    self.playVideo(bcid,cid,pxbid)
        self.trigger.emit('学习结束，请到www.ahgbjy.gov.cn进行考试~')
    
    
    #模拟打开视频学习页面
    def playVideo(self,bcid,cid,pxbid):
        if pxbid is None:
            url = 'http://static.ahgbjy.gov.cn/LMS/CoursePlayer1.aspx?bcid=%s&cid=%s' %(bcid,cid)
        else:
            url = 'http://static.ahgbjy.gov.cn/Class/LMS/CoursePlayer1.aspx?bcid=%s&cid=%s&pxbid=%s' %(bcid,cid,pxbid.group(0))
        
        resp = browser.get(url, headers = headers).content.decode('utf-8')
        sid = re.search('(?<=sectionId = \").*?(?=\";)', resp).group(0)
        aid = re.search('(?<=activityId = \").*?(?=\";)', resp).group(0)
        cid = re.search('(?<=courseId = \").*?(?=\";)', resp).group(0)
        pxbid = re.search('(?<=pxbid=).*?(?=\")', resp)
        r = random.random()
        #让服务器获得一个本次学习开始时间
        if pxbid is None:
            url = 'http://static.ahgbjy.gov.cn/LMS/ScoDoIt.aspx?flag=get&sid=%s&cid=%s&aid=%s&r=%s'%(sid,cid,aid,r)
        else:
            url = 'http://static.ahgbjy.gov.cn/Class/LMS/ScoDoIt.aspx?flag=get&sid=%s&cid=%s&aid=%s&r=%s'%(sid,cid,aid,r)
        resp = browser.get(url ,headers=headers).content.decode('utf-8')
        data1 = json.loads(resp)
#                     if('completed' == data1['status']):
#                         sleeptime = random.randint(300,600)
#                         self.trigger.emit('学习已完成，%s秒后跳过此章节'%(sleeptime))
#                         for k in range(0,sleeptime):
#                             time.sleep(1)
#                         self.submitCourse(data1)
#                         break
#                     else:

        # 每次随机学习5-15分钟，计时结束，触发 提交学习进度，服务器会根据本次学习开始时间累加到章节学习时间中
        sleeptime = random.randint(500,1100)
        self.trigger.emit('本次计划学习%s秒，预计于 %s结束'%(sleeptime, datetime.datetime.strftime(datetime.datetime.now()+datetime.timedelta(seconds=sleeptime),'%H:%M:%S')))
        for k in range(1,sleeptime):
            if k%300 == 0:
                self.updateTime(data1,pxbid)
            time.sleep(1)
        self.submitCourse(data1,pxbid)   
        #专题班专用提交学习进度   
        if pxbid is not None:
            form = {'t':'4','aid':aid,'cid':cid,'pxbid':pxbid.group(0),'_':''}
            url = 'http://static.ahgbjy.gov.cn/Class/LMS/Ajax.aspx'
            resp = browser.post(url, headers=headers, data=form)
    
    #每5分钟更新一次学习进度
    def updateTime(self,data1,pxbid):
        form={
        'flag':'updendtime',
        'logid':data1['logid']
        }
        if pxbid is None:
            url = 'http://static.ahgbjy.gov.cn/LMS/ScoDoIt.aspx'
        else:
            url = 'http://static.ahgbjy.gov.cn/Class/LMS/ScoDoIt.aspx'
        resp = browser.post(url, headers=headers, data=form)
    
    #提交学习进度   
    def submitCourse(self,data1,pxbid):
        if pxbid is None:
            url = 'http://static.ahgbjy.gov.cn/LMS/ScoDoIt.aspx'
        else:
            url = 'http://static.ahgbjy.gov.cn/Class/LMS/ScoDoIt.aspx'
        form={
        'flag':'set',    
#         'location':data1['location'],
        'location':totalTime,
        'status':data1['status'],
        'score':data1['score'],
        'suspenddata':data1['suspenddata'],
        'logid':data1['logid'],
        'abnormal':'true'
        }
        resp = browser.post(url, headers=headers, data=form)
        self.trigger.emit('本次计划学习完成！')
    
if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = FormGridLayout()
    sys.exit(app.exec_())