
import requests
import threading
import json
import re
from flask import Flask, jsonify, render_template, abort
from collections import defaultdict
from echarts import Echart, Legend, Bar, Axis, Toolbox, Tooltip,Line
from MongodbClient import MongodbClient as MC
from bs4 import BeautifulSoup as bs
from time import sleep
from bdb import bar
app = Flask(__name__)


def save_as_mongodb(name,dict):
    db = MC(name, '127.0.0.1', 27017)
    db.put(dict)


# 初始化薪水与资历的字典
def init_dict(name, workyear):
    db = MC(name, '127.0.0.1', 27017)
    
    data_name = ['salary_1_5', 'salary_6_10', 'salary_11_15', 'salary_16_20', 'salary_21_25', 'salary_26_30', 'salary_up_30'] 
    total_salary = [] 
    # 初始化字典        
    year = {}
    for i in data_name:
        year[i] = 0    
    for info in db.find({'workyear':workyear}):
        salary = info['salary']
        average = sum(int(i) for i in re.sub('[A-Za-z\u4e00-\u9fa5]+','',salary).split('-'))/2 
        total_salary.append(int(average))
        if 1<=average<=5:
            year['salary_1_5']+=1
        elif 6<=average<=10:
            year['salary_6_10']+=1
        elif 11<=average<=15:
            year['salary_11_15']+=1
        elif 16<=average<=20:
            year['salary_16_20']+=1
        elif 21<=average<=25:
            year['salary_21_25']+=1
        elif 26<=average<=30:
            year['salary_26_30']+=1
        elif 30<=average:
            year['salary_up_30']+=1    
    
    return year,total_salary
       

# 获取职位相应的城市数量
def get_city_info(name):
    db = MC(name, '127.0.0.1', 27017)
    results = db.find()
    city = defaultdict(int) 
    for result in results:     
            city[result['city']] += 1 
    info = dict(sorted(city.items(), key=lambda d:d[1], reverse=True)[:6]) #排序后，取前面6个城市
    chart = Echart(name,'城市职位数量分布图')
    chart.use(Toolbox(show='true',feature={'show':'true','saveAsImage':{'show':'true'}}))
    chart.use(Tooltip())
    chart.use(Bar('jobCount', list(info.values())))
    chart.use(Legend(['jobCount']))
    chart.use(Axis('category', 'bottom',data=list(info.keys())))
    return chart.json

# 获取职位词云技能表
def get_wordcloud(name):
    db = MC(name+'_wordcut', '127.0.0.1', 27017)
    results = db.find()[0]
    results.pop('_id') # 去掉mongodb 中的 '_id' key
    dict_data = results
    return dict_data
  
def get_workyear_about_salary_info(name):
    
    year_down_1, total_salary_1 = init_dict(name, '应届毕业生')
    year_1_3, total_salary_2 = init_dict(name, '1-3年')
    year_3_5, total_salary_3 = init_dict(name, '3-5年')
    year_5_10, total_salary_4 = init_dict(name, '5-10年')
    year_no_limit, total_salary_5 = init_dict(name, '不限')
    
  
    info = zip(
             list(year_down_1.values()),
             list(year_1_3.values()),
             list(year_3_5.values()),
             list(year_5_10.values()),
             list(year_no_limit.values())
            )  
    bar_data = [i for i in info]   

    line_data = [
                 round(sum(total_salary_1)/len(total_salary_1), 2),
                 round(sum(total_salary_2)/len(total_salary_2), 2),
                 round(sum(total_salary_3)/len(total_salary_3), 2),
                 round(sum(total_salary_4)/len(total_salary_4), 2),
                 round(sum(total_salary_5)/len(total_salary_5), 2), 
                  ] 

            
    chart = Echart(name,'工作资历与收入分布', right='auto', bottom='auto', padding='5')
    chart.use(Toolbox(show='true',feature={'show':'true','saveAsImage':{'show':'true'}}))
    chart.use(Tooltip())
    chart.use(Bar('1-5K', list(bar_data[0])))
    chart.use(Bar('6-10K', list(bar_data[1])))
    chart.use(Bar('11-15K', list(bar_data[2])))
    chart.use(Bar('16-20K', list(bar_data[3])))
    chart.use(Bar('21-25K', list(bar_data[4])))
    chart.use(Bar('26-30K', list(bar_data[5])))
    chart.use(Bar('大于30K', list(bar_data[6])))
    chart.use(Line('平均收入(K)', line_data , yAxisIndex=1, markPoint={'data':[
                    {'type': 'max', 'name': '最大值'},
                    {'type': 'min', 'name': '最小值'}
                ]}, markLine={
                'data': [
                    {'type': 'average', 'name': '平均值'}
                ]}
                   ))
    chart.use(Legend(['1-5K', '6-10K', '11-15K', '16-20K', '21-25K', '大于30K', '平均收入(K)']))
    chart.use(Axis('category', 'bottom',data=['1年以下', '1-3年', '3-5年', '5-10年', '不限']))
    chart.use(Axis('value', 'left',name='count',  min=0, boundaryGap=[0.2, 0.2]))
    chart.use(Axis('value', 'right',name='收入', max=40, min=0, boundaryGap=[0.2, 0.2]))
    return chart.json

@app.route('/')
def home():
    return "<a href='\大数据'>大数据</a> <a href='\爬虫'>爬虫</a>" 


@app.route('/<name>')
def index(name):

    db = MC(name, '127.0.0.1', 27017)
    if not db:
        abort(404)
        
    echart_data1 = get_city_info(name)
    echart_data2= get_workyear_about_salary_info(name)
    wordcloud_data = get_wordcloud(name)
    return render_template('index.html', echart_data1=echart_data1, echart_data2=echart_data2, wordcloud_data=wordcloud_data)

if __name__ == '__main__':
    app.run()
