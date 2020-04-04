# 燃烧女子的肖像的短评受数据保护，只能爬取前25页，每页20条，共
# 需获取的内容有：用户名、打分、影评、点赞数、时间

import requests
from bs4 import BeautifulSoup as bs
import re
import time
import csv
import json

# 生成Session对象，用于保存Cookie
s = requests.Session()

# 登录豆瓣
def login_douban():
    login_url = 'https://accounts.douban.com/j/mobile/login/basic'
    headers = {'user-agent': 'Mozilla/5.0', 'Referer': 'https://accounts.douban.com/passport/login?source=movie'}
    data = {'name': '198****3996',
            'password': '*********',
            'remember':'false'}
    r = s.post(login_url, headers = headers, data = data)
    # r.raise_for_status()
    # 打印请求结果
    print(r.text)
    # str转为dict
    result = json.loads(r.text)['status']
    if result == 'failed':
        print('登录失败！')
        return False
    else:
        return True
        
 
# url = 'https://movie.douban.com/subject/30257175/comments?status=P'
# 爬取一页（共20条）影评
def get_html_data(movie_url, start):
    url = movie_url + 'comments?start=' + str(start)+ '&limit=20' 
    print('url = ' + url)
    head = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'}
    try:
        # requests获得html内容
        resp = s.get(url,headers=head)
        resp.raise_for_status()
        html_data = resp.text
        return html_data
        # parser_html(html_data, start)
    except: 
        print('爬取失败，start=' + str(start))
        return 'fail'
    # parser_html(html_data, start)
    

# 解析html内容
def parser_html(movie_name, movie_list, start):
    # 拆分影评信息
    # 需获取的内容有：用户名、打分、影评、点赞数、时间
    # path = r'../燃烧女子的肖像.csv'
    with open('../csv文件/movies.csv', 'a+', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        for index in range(len(movie_list)): 
            movie = movie_list[index]
            # id
            idNum = start + index + 1
            # 用户名
            userName = movie.find('a' ,class_='').text
            # 打分
            # 在标签值未知的情况下怎么使用BeautifulSoup
            # 异常：用户没有打分！
            try:
                rank_label = movie.find(name='span', attrs={'class':True, 'title':True})
                rank_str = rank_label['class'][0]
                # 在字符串中提取数字
                rank = re.findall(r'\d', rank_str)[0]
            except:
                rank = '-1'
            # 影评
            comment = movie.find('span' ,class_="short").text
            # 该影评的点赞
            likes = movie.find('span' ,class_='votes').text
            # 时间
            time_str = movie.find('span' ,class_="comment-time").text
            time = re.findall(r'\d{4}-\d{1,2}-\d{1,2}', time_str)[0]
            print('idNum = ' + str(idNum) + ' userName = ' + userName + ' rank = ' + rank + ' likes = ' + likes + ' time = ' + time + '\ncomment = ' + comment)
            print('-------------------------------------')
            # 写入csv文件中
            data_row = [idNum, movie_name, userName, int(rank), int(likes), time, comment]
            writer.writerow(data_row)
            # write_csv(data_row)

# 写入文件中
# 问题：多次打开关闭文件 PermissionError: [Errno 13] Permission denied: '../燃烧女子的肖像.csv'
def write_csv(data_row):
    path = r'../csv文件/movies.csv'
    with open(path, 'a+', encoding='utf-8', newline='') as file:
        csv_write = csv.writer(file)
        # 编码出现了问题：UnicodeEncodeError: 'gbk' codec can't encode character '\xab' in position 186: illegal multibyte sequence
        csv_write.writerow(data_row)

def spider(movie_name, movie_url):
    num = 0
    while num >= 0:
        start = num * 20
        # print('start = ' + str(start))
        html_data = get_html_data(movie_url, start)
        # print(html_data)
        # 获取html内容成功
        if html_data != 'fail':
            # 解析HTML内容
            soup = bs(html_data, 'html.parser')
            movie_list = soup.find_all('div', class_='comment')
            # print(movie_list)
            # 到第25页，movie_list为空
            if movie_list:
                # 获取电影的影评等信息
                parser_html(movie_name, movie_list, start)
            else:
                print('movie_list is empty!')
                break
        time.sleep(1)
        # num = 11时，无权限访问网页
        # 因为豆瓣在没有登录状态情况下只允许你查看前200条影评，之后就需要登录才能查看，这也算是一种反扒手段
        num += 1
        # print('num = ' + str(num)) 


if __name__ == "__main__":
    # 写入行头
    # csv_head = ['idNum', 'movie_name', 'userName', 'rank', 'likes', 'time', 'comment']
    # write_csv(csv_head)
    if login_douban():
        # 登录成功再爬取
        with open('../csv文件/Top250MovieList.csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            # 跳过行首
            next(reader)
            for row in reader:
                print(row[1])
                # 账号被锁定
                num = int(row[0])
                # 看不见的客人
                if num >= 66:
                    spider(row[1], row[2])
                    # break
