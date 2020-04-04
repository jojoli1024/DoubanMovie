import requests
from bs4 import BeautifulSoup as bs
import csv

# 获取Top250电影的url和name
def getItem(start):
    url = 'https://movie.douban.com/top250?start=' + str(start) + '&filter='
    headers = {'user-agent': 'Mozilla/5.0'}
    r = requests.get(url,headers = headers)
    html_data = r.text
    soup = bs(html_data, 'html.parser')
    # 解析html内容
    subject_list = soup.find_all('div', class_='pic')
    # 编码ID: count
    count = start + 1
    for item in subject_list:
        print(count)
        movie_url = item.find_all('a')[0]['href']
        print(movie_url)
        for subject in item.find_all('img'):
            movie_name = subject['alt']
            print(movie_name)
        # 写入csv文件中
        data_row = [count, movie_name, movie_url]
        write_csv(data_row)
        count += 1

# 写入文件中
def write_csv(data_row):
    path = '../csv文件/Top250MovieList.csv'
    with open(path, 'a+', encoding='utf-8', newline='') as file:
        csv_write = csv.writer(file)
        csv_write.writerow(data_row)

csv_head = ['id', 'movie_name', 'movie_url']
write_csv(csv_head)
start = 0
while(start <= 250):
    getItem(start)
    start += 25