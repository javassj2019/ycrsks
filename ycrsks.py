import json
import requests
import re
import collections
import pymysql

###正文开始
##网站访问的基本信息
http = 'http://'
host = 'm.yc.lxsk.com'
loginurl = '/WebAppLogin/Index'
userinfo = '/UserInfo/Index'
desktop = '/MobileDesktop/Index'
saveurl = '/WebAppUser_Subject_Relation/SaveStudyRecord'

###网站访问的基本header

header1 = collections.OrderedDict()
header1['Host'] = host
header1['Connection'] = 'keep-alive'
header1['Cache-Control'] = 'max-age=0'
header1['Origin'] = http + host
header1['Upgrade-Insecure-Requests'] = '1'
header1[
    'User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
header1['Content-Type'] = 'application/x-www-form-urlencoded'
header1['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
header1['Referer'] = http + host + loginurl
header1['Accept-Encoding'] = 'gzip, deflate'
header1['Accept-Language'] = 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.5;q=0.4'
header1['Cookie'] = 'ASP.NET_SessionId=dskyxykydaqfboxcxzhzsm4r'
# 连接数据库并获取账户密码信息
conn = pymysql.connect(host='cdb-kce5k8kq.bj.tencentcdb.com', user='root', passwd='a159753A!', port=10264,
                       charset='utf8', db='ycrsks')
cur = conn.cursor(pymysql.cursors.DictCursor)  # 生成游标


# 录入新用户
def Typeuserid():
    print('请输入用户名：')
    userAccount = input()
    print('请输入密码：')
    userPassword = input()
    # 用户查重
    checkuid = cur.execute('select UserID from User where UserID = (%s)', (userAccount))
    #print(checkuid)
    if (checkuid == 0):
        cur.execute('insert into User(UserID,UserPassword,Study) VALUES (%s,%s,%s)', (userAccount, userPassword, 0))
        conn.commit()
        print('用户添加完成')
    else:
        print('用户已存在，无需再次添加')
# 考试答案与提交
def kaoshi ():
    # 获取考试必要信息
    tt = requests.get(http + host + '/WebAppUser_Subject_Relation/ExamIndex', headers=header2)
    r = 'id="hid_KeyId" value="(.*)"/>'
    keyid = re.findall(r, tt.text)
    apiurl = 'ycpxkswebapi.lxsk.com'
    tokenurl = '/api/token'
    tokendata = 'grant_type=password&username=' + username + '&password=' + userpasswd
    tt = requests.post(http + apiurl + tokenurl, data=tokendata)
    dd = json.loads(tt.text)
    access_token = dd['access_token']
    examurl = '/api/User_Subject_Relation/GetExamList?PageIndex=1&PageSize=100&User_ID=' + userid
    headertoken = {}
    headertoken['Authorization'] = 'bearer ' + access_token
    tt = requests.get(http + apiurl + examurl, headers=headertoken)
    dd = json.loads(tt.text)
    Subject_ID = dd['rows'][0]['cell'][1]
    PaperID = dd['rows'][0]['cell'][3]
    NumberNO = dd['rows'][0]['cell'][4]
    sjurl = '/api/Examing/PrepareTest?vSubjectId=' + Subject_ID + '&vNumberNO=' + NumberNO + '&vPaperID=' + PaperID + '&vUser_ID=' + userid
    tt = requests.post(http + apiurl + tokenurl, data=tokendata)
    dd = json.loads(tt.text)
    access_token = dd['access_token']
    headertoken['Authorization'] = 'bearer ' + access_token
    tt = requests.get(http + apiurl + sjurl, headers=headertoken)
    r = '"(.*)"'
    sjid = re.findall(r, tt.text)
    sjurl = '/api/PaperData/GetPaperData?_ApplyDetailID=' + sjid[0]
    tt = requests.get(http + apiurl + sjurl, headers=headertoken)

    date = tt.text
    dd = json.loads(date)
    for i in range(20):
        UUIDS = dd['Rubric_S_Info'][i]['ID']
        TITLES = dd['Rubric_S_Info'][i]['RubricTitle']
        ANSWERS = dd['Rubric_S_Info'][i]['OptionAnswer'].split('#', -1)
        TYPES = dd['Rubric_S_Info'][i]['RubricType']
        point = cur.execute('select uuid from yc where uuid =' + UUIDS)  # 查询UUID
        if point == 0:
            if len(ANSWERS) < 4:
                cur.execute("insert into yc(uuid,timu,A,B,C,type) VALUES (%s,%s,%s,%s,%s,%s)",(UUIDS, TITLES, ANSWERS[0], ANSWERS[1], ANSWERS[2], TYPES))
            else:
                cur.execute("insert into yc(uuid,timu,A,B,C,D,type) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                        (UUIDS, TITLES, ANSWERS[0], ANSWERS[1], ANSWERS[2], ANSWERS[3], TYPES))
            print('有一道单选题不存在，试题编号为' + UUIDS)
    for i in range(10):
        UUIDD = dd['Rubric_D_Info'][i]['ID']
        TITLED = dd['Rubric_D_Info'][i]['RubricTitle']
        ANSWERD = dd['Rubric_D_Info'][i]['OptionAnswer'].split('#', -1)
        TYPED = dd['Rubric_D_Info'][i]['RubricType']
        point = cur.execute('select uuid from yc where uuid =' + UUIDD)  # 查询UUID
        # print(UUIDD, TITLED, ANSWERD[0], ANSWERD[1], ANSWERD[2], ANSWERD[3], TYPED)
        if point == 0:
            if len(ANSWERD) < 4:
                cur.execute("insert into yc(uuid,timu,A,B,C,type) VALUES (%s,%s,%s,%s,%s,%s)",
                            (UUIDD, TITLED, ANSWERD[0], ANSWERD[1], ANSWERD[2], TYPED))
            else:
                cur.execute("insert into yc(uuid,timu,A,B,C,D,type) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                            (UUIDD, TITLED, ANSWERD[0], ANSWERD[1], ANSWERD[2], ANSWERD[3], TYPED))
            print('有一道多选题不存在，试题编号为' + UUIDD)
    for i in range(20):
        UUIDB = dd['Rubric_B_Info'][i]['ID']
        TITLEB = dd['Rubric_B_Info'][i]['RubricTitle']
        ANSWERB = dd['Rubric_B_Info'][i]['OptionAnswer'].split('#', -1)
        TYPEB = dd['Rubric_B_Info'][i]['RubricType']
        point = cur.execute('select uuid from yc where uuid =' + UUIDB)  # 查询UUID
        if point == 0:
            cur.execute("insert into yc(uuid,timu,A,B,type) VALUES (%s,%s,%s,%s,%s)",
                        (UUIDB, TITLEB, ANSWERB[0], ANSWERB[1], TYPEB))
            print('有一道判断题不存在，试题编号为' + UUIDB)
    conn.commit()

    begintesturl = '/api/Examing/BeginTest?vApplyDetailID=' + sjid[0]
    requests.get(http + apiurl + begintesturl, headers=headertoken)
    tt = requests.post(http + apiurl + tokenurl, data=tokendata)
    kk = json.loads(tt.text)
    access_token = kk['access_token']
    headertoken['Authorization'] = 'bearer ' + access_token
    savepaperurl = '/api/CheckPaper/SavePaper'
    danalistS = []
    for i in range(20):
        TITLES = dd['Rubric_S_Info'][i]['RubricTitle']
        TITLES = pymysql.escape_string(TITLES)
        UUIDS = dd['Rubric_S_Info'][i]['ID']
        point = cur.execute('select uuid from yc where timu = ' + '"' + TITLES + '"' + 'and type = "A"')
        if point == 0:
            print('有一道单选题答案不存在，试题编号为' + UUIDS)
        else:
            cur.execute('select answer from yc where timu = ' + '"' + TITLES + '"' + 'and type = "A"')
            daan = cur.fetchone()
            danalistS.insert(i, daan['answer'][0])
            # print(danalistS)
    danalistD = []
    for i in range(10):
        TITLED = dd['Rubric_D_Info'][i]['RubricTitle']
        TITLED = pymysql.escape_string(TITLED)
        UUIDD = dd['Rubric_D_Info'][i]['ID']
        point = cur.execute('select uuid from yc where timu = ' + '"' + TITLED + '"' + 'and type = "B"')
        if point == 0:
            print('有一道多选题答案不存在，试题编号为' + UUIDD)
        else:
            cur.execute('select answer from yc where timu = ' + '"' + TITLED + '"' + 'and type = "B"')
            daan = cur.fetchone()
            danalistD.insert(i, daan['answer'])
            #print(UUIDD,type(daan),danalistD)
    danalistB = []
    for i in range(20):
        TITLEB = dd['Rubric_B_Info'][i]['RubricTitle']
        TITLEB = pymysql.escape_string(TITLEB)
        UUIDB = dd['Rubric_B_Info'][i]['ID']
        point = cur.execute('select uuid from yc where timu = ' + '"' + TITLEB + '"' + 'and type = "C"')
        if point == 0:
            print('有一道判断题答案不存在，试题编号为' + UUIDB)
        else:
            cur.execute('select answer from yc where timu = ' + '"' + TITLEB + '"' + 'and type = "C"')
            daan = cur.fetchone()
            danalistB.insert(i, daan['answer'][0])
            # print(danalistB)
    applyid = 'ApplyDetailID=' + sjid[0]
    danxuan = '&RubricSWrite='
    duoxuan = '&RubricDWrite='
    panduan = '&RubricBWrite='
    for i in range(20):
        danxuan = danxuan + danalistS[i] + '%7C'
    for i in range(10):
        dx = danalistD[i]
        dx = dx.replace('#', '%23')
        duoxuan = duoxuan + dx + '%7C'
    for i in range(20):
        panduan = panduan + danalistB[i] + '%7C'
    header3 = {}
    header3['Host'] = apiurl
    header3['Connection'] = 'keep - alive'
    header3['Accept'] = '* / *'
    header3['Origin'] = 'http: // m.yc.lxsk.com'
    header3['User - Agent'] = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
    header3['DNT'] = '1'
    header3['Content - Type'] = 'application / x - www - form - urlencoded;charset = UTF - 8'
    header3['Accept - Encoding'] = 'gzip, deflate'
    header3['Accept - Language'] = 'zh - CN, zh;q = 0.9'

    tt = requests.post(http+apiurl+tokenurl,headers=header3 ,data = tokendata)
    kk = json.loads(tt.text)
    access_token = kk['access_token']
    headertoken['Authorization'] = 'bearer ' + access_token
    header4 = {}
    header4['Host'] = apiurl
    header4['Connection'] = 'keep - alive'
    header4['Access-Control-Request-Method'] = 'POST'
    header4['Accept'] = '* / *'
    header4['Origin'] = http + host
    header4['User - Agent'] = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
    header4['DNT'] = '1'
    header4['Accept - Encoding'] = 'gzip, deflate'
    header4['Accept - Language'] = 'zh - CN, zh;q = 0.9'
    header4['Access-Control-Request-Headers'] = 'authorization'
    requests.options(http + apiurl + savepaperurl,headers=header4)
    header5 = header4
    header5['Authorization'] = 'bearer ' + access_token
    header5['Content-Type'] = 'application/x-www-form-urlencoded;charset=UTF-8'
    tt = requests.post(http + apiurl + savepaperurl, headers=header5, data=applyid + danxuan + duoxuan + panduan)
    print(tt.text)
    #提交考试答案，提交即交卷
    #finshurl = '/api/CheckPaper/FinishedTest?vApplyDetailID=' + sjid[0]
    #requests.options(http + apiurl + finshurl,headers=header4)
    #tt = requests.get(http + apiurl + finshurl, headers=header5)
    #fenshu = tt.text
    #cur.execute('UPDATE User SET Exem = (%s) WHERE UserID = (%s)', (fenshu,username))
    conn.commit()
    #print('考试结束，分数已录入',fenshu)





print('需要添加新用户吗？Yes')
checktype = input()
if (checktype == 'Y'):
    i = 0
    while (i <= 100):
        Typeuserid()
        i = i + 1
s = 0
l = cur.execute('select UserID,UserPassword from User where Study = 0')
while (s < l):
    ###开始登陆过程
    print(s,l)
    k = cur.execute('select UserID,UserPassword from User where Study = 0')
    if l >= 1:
        cur.execute('select UserID,UserPassword from User where Study = 0')
        tt1 = cur.fetchone()
        username = tt1['UserID']
        passwd = tt1['UserPassword']
        logindata = 'UserName=' + username + '&Password=' + passwd + '&txtCheckCode=6455'
        requests.get(http + host + loginurl, headers=header1)
        requests.post(http + host + loginurl, headers=header1, data=logindata)
        tt = requests.get(http + host + userinfo, headers=header1)
        uid = '<input type="hidden" id="hid_User_ID"  value="(.*)"/>'
        upsw = '<input type="hidden" id="hid_Password" value="(.*)" />'
        userid = re.findall(uid, tt.text)[0]
        userpasswd = re.findall(upsw, tt.text)[0]
        tt = requests.get(http + host + desktop, headers=header1)
        # print(tt.text)
        name = '<font color="yellow">(.*)</font>'
        hyname = re.findall(name, tt.text)[0]
        print(hyname)

        ##开始学习过程(刷课时）
        header2 = collections.OrderedDict()
        header2['Host'] = host
        header2['Connection'] = 'keep-alive'
        header2['Accept'] = 'application/json, text/javascript, */*; q=0.01'
        header2['Origin'] = http + host
        header2['X-Requested-With'] = 'XMLHttpRequest'
        header2[
            'User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36 QBCore/4.0.1301.400 QQBrowser/9.0.2524.400 Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2875.116 Safari/537.36 NetType/WIFI MicroMessenger/7.0.5 WindowsWechat'
        header2['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
        header2['Accept-Encoding'] = 'gzip, deflate'
        header2['Accept-Language'] = 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.5;q=0.4'
        header2['Cookie'] = 'ASP.NET_SessionId=dskyxykydaqfboxcxzhzsm4r'
        sid = 3608
        while (sid <= 3616):
            savedata = 'vUserInfo_ID=' + str(userid) + '&vRefParentId=' + str(
                sid) + '&vCurrentPos=5000&myCurrentsession_time=01:01:45&random=99.7548329067212136'
            tt = requests.post(http + host + saveurl, headers=header2, data=savedata)
            sid = sid + 1

        cur.execute('UPDATE User SET Name = (%s) WHERE UserID = (%s)', (hyname, username))
        cur.execute('UPDATE User SET Study = 1 WHERE UserID = (%s)', (username))
        conn.commit()
        kaoshi()
        l = k - 1
print('库存学习人数已清零，请核查分数为零的问题考号')

cur.close()
conn.close()


