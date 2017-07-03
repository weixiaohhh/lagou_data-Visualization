
import requests
import threading
import json
import jieba
import re
import urllib.parse

from collections import defaultdict
from echarts import Echart, Legend, Bar, Axis, Toolbox, Tooltip
from MongodbClient import MongodbClient as MC
from bs4 import BeautifulSoup as bs
from time import sleep




def save_as_mongodb(name,dict):
    db = MC(name, '127.0.0.1', 27017)
    db.put(dict)
    
# 多线程 
class myThread (threading.Thread):  
    def __init__(self,name):
        threading.Thread.__init__(self)
        self.name = name
 
    def run(self):                   
        print("Starting " +self.name) 
        print("Exiting " + self.name)
        
     # job 详细信息    
    def get_detail(self, dict_data, tabale_name):
        try:

            #  添加职位描述
            url = 'https://m.lagou.com/jobs/{}.html'.format(dict_data['positionId'])
            print(url)
            headers = {
                'Host': 'm.lagou.com',
                'Referer': 'https://m.lagou.com/',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.76 Mobile Safari/537.36',
                'Cookie':'user_trace_token=20170701163704-343a0879-e937-4ebf-b95b-05e5e72d4fe3; LGUID=20170701163705-761c14df-5e38-11e7-a0dc-5254005c3644; SEARCH_ID=bb413ef0d5404f17a985665ad52a1ddd; TG-TRACK-CODE=search_banner; JSESSIONID=ABAAABAAADEAAFI9C62904D335555A5A59FC32BA6E30770; _gid=GA1.2.1303497647.1498898080; _gat=1; _ga=GA1.2.912010882.1498898079; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1498898079; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1498970898; LGSID=20170702125045-029282da-5ee2-11e7-b965-525400f775ce; PRE_UTM=; PRE_HOST=; PRE_SITE=; PRE_LAND=https%3A%2F%2Fwww.lagou.com%2F; LGRID=20170702125045-0292842c-5ee2-11e7-b965-525400f775ce; index_location_city=%E5%85%A8%E5%9B%BD'           }
            html = requests.get(url, headers=headers).text
            soup = bs(html, "html.parser")
            positiondesc = soup.find_all('div',{'class':'content'})[0].text
            workyear = soup.find_all('span',{'class':'workyear'})[0].text.strip()
            education = soup.find_all('span',{'class':'education'})[0].text.strip()
            temptation = soup.find_all('div',{'class':'temptation'})[0].text.strip()
            info = re.sub('  ', '',soup.find_all('p',{'class':'info'})[0].text.strip())
            dict_data['workyear'] = workyear # 工作年数
            dict_data['education'] = education # 学历
            dict_data['temptation'] = temptation #职位诱惑
            dict_data['info'] = info # 公司信息
            dict_data['positiondesc'] = positiondesc # 职位描述
            save_as_mongodb(tabale_name, dict_data) # 保存到mongodb
        except:
            print('this is error')

# 获取JSON 数据    
def get_json(pageNum, positionName):
    # 手机端爬取
    positionName = urllib.parse.quote(positionName, encoding='utf8')
    print(positionName)
    raw_url ='https://m.lagou.com/search.json?city=%E5%85%A8%E5%9B%BD&positionName={positionName}&pageNo={pageNo}&pageSize=15'.format(positionName=positionName, pageNo=pageNum)

    info = requests.get(raw_url).json()
    # 判断是否还有数据要获取
    if len(info['content']['data']['page']['result']) == 0:
        return None
    
    return info['content']['data']['page']['result']
    
    
def get_data_to_mongodb(job):

    pageNum = 1
    while 1:
        
        data = get_json(pageNum, job)
        if data == None:
            break
        i = 1
        for dict_data in data:
            sleep(2)
            thread = myThread(i)
            thread.start()
            thread.get_detail(dict_data, job)
            i+=1
        pageNum+=1
        sleep(2)
        

# 得到职位 需要的技能词云
def get_wordcut(job):
    result = []
    db = MC(job, '127.0.0.1', 27017)
    for info in db.find():
        a = info['positiondesc'].strip(' ')
        wordcuts = a.split('\n')
        for i in wordcuts:
            try:
                seg_list = jieba.cut(i) 
                for j in seg_list:
                    if len(''.join(x for x in j if ord(x) < 256))>=2:
                        result.append(j.lower())
            except: print("some wrong")
        
    dict_result = defaultdict(int)
    for i in result:
        dict_result[i]+=1
    dict_result=sorted(dict_result.items(),key=lambda asd:asd[1],reverse=True)[:32]

    save_as_mongodb(job+'_wordcut',dict(dict_result))    #保存词云
       

if __name__ == '__main__':
    job = input('请输入你要爬取得职位:')
    db = MC(job, '127.0.0.1', 27017)
    db.clean()  #保证每次爬取前，存在的数据库清空
    db = MC(job+'_wordcut', '127.0.0.1', 27017)
    db.clean()  #保证每次爬取前，存在的词云数据库清空
    get_data_to_mongodb(job)
    get_wordcut(job)
