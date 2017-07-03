# 拉钩招聘网，数据可视化,技能词云



## Getting Started
```git clone https://github.com/weixiaohhh/lagou_data-Visualization/```
### Prerequisites and Installing

- 运行环境: Python 3 

- 数据库: MongoDb [官网](https://www.mongodb.com/download-center)

- 可视化: 用的百度的[Echarts](echarts.baidu.com/) 和 [echarts-python](https://github.com/yufeiminds/echarts-python)
- 词云： [wordcloud2](https://github.com/timdream/wordcloud2.js) 和 [jieba](https://github.com/fxsjy/jieba)

```
pip install requirements.txt
```


## Running 

first(下载数据):
```
python spider.py
```

![](http://upload-images.jianshu.io/upload_images/2176378-04a6bf5d61cb4542.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
注意：职位之间不能有空格

second(数据爬取完后):
```
python view.py
```
> 输入127.0.0.1/xxx     # 参数为你下载职位的名字


![](http://upload-images.jianshu.io/upload_images/2176378-84ee404be54f5a9d.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)


![](http://upload-images.jianshu.io/upload_images/2176378-399c7e1b6772a9ab.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
