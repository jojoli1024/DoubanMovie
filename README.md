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

- getSubjects.py用来获取豆瓣Top250电影的url，main.py用于从网上获取影评数据