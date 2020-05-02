import csv
import re
from opencc import OpenCC
import json
import jieba

# 除去字符串中的表情
def delEmoji(str):
    try:
        # Wide UCS-4 build
        myre = re.compile(u'['
            u'\U0001F300-\U0001F64F'
            u'\U0001F680-\U0001F6FF'
            u'\u2600-\u2B55]+',
            re.UNICODE)
    except re.error:
        # Narrow UCS-2 build
        myre = re.compile(u'('
            u'\ud83c[\udf00-\udfff]|'
            u'\ud83d[\udc00-\ude4f\ude80-\udeff]|'
            u'[\u2600-\u2B55])+',
            re.UNICODE)
    return myre.sub('', str)

# 从movies.csv中提出打分和影评，并初步处理影评
# 除去影评的英文部分和表情和所含网站
# 除去过短影评，防止切词后为空词列表
def getComment():
    file = open('../csv文件/comments.csv', 'w', encoding='utf-8', newline='')
    writer = csv.writer(file)
    head = ['rank','comment']
    writer.writerow(head)
    with open('../csv文件/movies.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        # 跳过行首
        next(reader)
        count = 1
        for row in reader:
            rank = row[3]
            comment = row[6]
            zh_pattern = re.compile(u'[\u4e00-\u9fa5]+')
            # 删去没有打分的评论
            if rank == '-1' or rank == '':
                continue
            # 删去全英文的评论
            elif not zh_pattern.search(comment):
                continue
            # 过滤网址
            comment = re.sub(r'(https|http)?:\/\/(\w|\.|\/|\?|\=|\&|\%)*\b', '', comment)
            # 过滤英文
            comment = re.sub(r"[A-Za-z\!\,\.\"\ \'\:\’\n\t\～\~\/\?\(\)\>\<\_\-\^\←\●\★\☆]", '', comment)
            # 去掉表情符号
            comment = delEmoji(comment)
            #繁体转简体
            cc = OpenCC('t2s')
            comment = cc.convert(comment)
            # 判断处理后的评论是否有中文
            if not zh_pattern.search(comment):
                continue
            # 切词后为空，除掉过短影评
            if remove_pun_and_stopWords(comment)=='\n':
                continue
            data_row = [rank, comment]
            writer.writerow(data_row)
            print(str(count) + '\t' + comment)
            count += 1
    file.close()

# wiki中文语料库处理：繁体转为简体
def wikiProcess():
    cc = OpenCC('t2s')
    out_file = open("../AA/wiki", 'w', encoding='utf-8')
    with open('../AA/wiki_00', 'r', encoding='utf-8') as in_file:
        line = in_file.readline()
        while line:
            if line != '':
                print(line)
                newline = cc.convert(line)
                print(newline)
                out_file.write(newline)
            line = in_file.readline()
    out_file.close()

# 使用结巴切词后，除去停用词以及标点符号
def remove_pun_and_stopWords(line):
    # 停用词列表
    stopword_set = set()
    with open('hit_stopwords.txt', 'r', encoding='utf-8') as f:
        for stopword in f:
            stopword_set.add(stopword.strip('\n'))
    # print(stopword_set)
    # 去掉标点符号
    punctuation = re.compile(r"[A-Za-z0-9\n-~!@#$%^&*()_+`=\[\]\\\{\}\"|;':,./<>?·！∩@#￥%……&*（）——+【】、；‘：“”，。、《》？「『」』]")
    line = punctuation.sub('', line)
    line = delEmoji(line)
    words = jieba.cut(line, cut_all = False)
    newline = ''
    for word in words:
        if word not in stopword_set:
            newline += word + ' '
    return newline + '\n'

# 获得切词后的comments数据，存至comments.txt
def cut_comments():
    out_file = open('comments.txt', 'w', encoding='utf-8')
    commentPath = '../csv文件/comments.csv'
    with open(commentPath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        # 跳过行首
        next(reader)
        count = 1
        for row in reader:
            comment = row[1]
            print(str(count) + '\t' + comment)
            comment = remove_pun_and_stopWords(comment)
            print(str(count) + '\t' + comment)
            out_file.write(comment)
            count += 1
    out_file.close()

# 获得切词后的wiki数据
def cut_wiki():
    wikiPath = '../AA/wiki'
    out_file = open('wiki.txt', 'w', encoding='utf-8')
    with open(wikiPath, 'r', encoding='utf-8') as file:
        line = file.readline()
        i = 0
        while(line):
            if i % 5000 == 0:
                print("Review %d " % i)
            text = json.loads(line)['text']
            # print(line)
            text = remove_pun_and_stopWords(text)
            # print(text)
            out_file.write(text)
            i += 1
            line = file.readline()
    out_file.close()

if __name__ == "__main__":
    # 从豆瓣爬取的影评做初步处理
    getComment()
    # 从wiki获得的文本做繁体转换
    # wikiProcess()

    # 对文本做切词处理，去停用词和标点符号
    cut_comments()
    # cut_wiki()