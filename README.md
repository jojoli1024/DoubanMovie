# DoubanMovie
## 用于学习Python的豆瓣影评爬虫

- 豆瓣影评有短评和长篇的影评，为了方便后面的自然语言处理，选择了对短评进行爬取


- 预计需获取的内容有：用户名、打分、影评、点赞数、时间

- 短评的html文件格式如下
```
<div class="comment">  
    <h3>  
        <span class="comment-vote">  
            <span class="votes">
                2060
            </span>  
            <input type="hidden" value="2090658493">  
                <a class="j a_show_login" href="javascript:;" onclick="">
                    有用
                </a>  
            </input>
        </span>  
        <span class="comment-info">  
            <a class="" href="https://www.douban.com/people/nezhaboy/">
                哪吒男
            </a>  
            <span>
                看过
            </span>  
            <span class="allstar50 rating" title="力荐"></span>  
            <span class="comment-time" title="2019-12-19 00:12:06">  
                2019-12-19  
            </span>  
        </span>  
    </h3>  
    <p class="">  
        <span class="short">
            女同电影的开始，大多源于共担苦难；男同电影的开始，大多源于分享放逐。有的人被赋权，有的人被剥权，没有人自由，在这样的世界里我们凝视惊涛骇浪，不够勇敢，蜷缩回庸常的生活，然而不自由的生活，安逸也如坐针毡。祝每一个你，你们，携手乘风破浪。
        </span>  
    </p>  
</div>
```

- 用BeautifulSoup库解析HTML文件时，关于标签未知的情况下如何解析，[参考了这篇博客](https://blog.csdn.net/u013005025/article/details/64441189)

- 03/12 数据爬取成果

|idNum|movie_name|userName|rank|likes|time|comment|
|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
1|肖申克的救赎|犀牛|5|15244|2005-10-28|当年的奥斯卡颁奖礼上，....
2|肖申克的救赎|kingfish|5|26936|2006-03-22|不需要女主角的好电影
3|肖申克的救赎|如小果|5|16421|2008-02-27|恐惧让你沦为囚犯，希望让你重获自由。——《肖申克的救赎》
4|肖申克的救赎|文泽尔|4|2424|2008-01-14|人的生命不过是从一个洞穴通往另一个世界..然后在那个世界的雨中继续颤抖.i hope

- 豆瓣需要登陆才能查看200条评论之后的短评，[参考了这篇博客](https://blog.csdn.net/u014044812/article/details/96484905)

- 爬虫/getSubjects.py用来获取豆瓣Top250电影的url，爬虫/main.py用于从网上获取影评数据

## 自然语言预处理

- 对影评进行了如下处理：删去了没有打分的评论、过滤英文部分、所含网站和表情符号

- 如何删去影评中的表情符号，[参考了这篇博客](https://segmentfault.com/a/1190000007594620)

- 一个问题：选的是Top250，一星二星的影评太少了

- 从[Wiki中文语料库](https://link.zhihu.com/?target=https%3A//dumps.wikimedia.org/zhwiki/latest/zhwiki-latest-pages-articles.xml.bz2)获得zhwiki-latest-pages-articles.xml.bz2，用[wikiextractor](https://link.zhihu.com/?target=https%3A//github.com/attardi/wikiextractor)解压语料文本到AA文件夹。
```
git clone https://github.com/attardi/wikiextractor wikiextractor
cd wikiextractor
# 应该是html格式
python WikiExtractor.py -b 1024M -o extracted zhwiki-latest-pages-articles.xml.bz2
# 形成json格式
python WikiExtractor -o extracted --process 2 -b 2048M --json zhwiki-latest-pages-articles.xml.bz2
```

- 用[opencc](https://github.com/BYVoid/OpenCC)繁体转简体，使用[参照了这篇博客](https://clay-atlas.com/blog/2019/09/24/python-chinese-tutorial-opencc/)
```
pip install opencc-python-reimplemented
```

- 使用jieba分词后，去掉停用词和标点符号，再使用word2vec训练词向量（[停用词表](https://github.com/goto456/stopwords)）

## 词向量

- 使用gensim的word2vec包，[参数说明](https://blog.csdn.net/szlcw1/article/details/52751314)

## 朴素贝叶斯分类器

- 将comments.csv分为train_data.csv和test_data.csv，使用sklearn.model_selection的train_test_split

- 在sklearn中，提供了3中朴素贝叶斯分类算法：GaussianNB(高斯朴素贝叶斯)、MultinomialNB(多项式朴素贝叶斯)、BernoulliNB(伯努利朴素贝叶斯)，先试用了多项式朴素贝叶斯。

- 词向量模型训练好后，把train_data.csv的影评导入模型中，先把每个影评切词得该影评得一系列词列表，把在词列表里且在模型的所有词向量求平均值，用这个平均值代表这个影评。如下图：
![训练文本怎么使用词向量](https://github.com/jojoli1024/picture_for_md/raw/master/img/训练文本如何使用词向量.png)

- 一个问题，影评太短，切词后，词列表为空！（comments.csv处理添加一步：小于6个汉字影评删去）

## 结果

|word2vec模型|K折交叉验证|得分|测试集得分|
|:--:|:--:|:--:|:--:|
|影评|5|0.70306|0.67775|
|影评|10|0.70144||
|影评+wiki|5|0.67206||
