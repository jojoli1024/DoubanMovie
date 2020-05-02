from gensim.models import word2vec
from dataProcess import remove_pun_and_stopWords
import csv

# 影评小于5个汉字的删去
def shoter_Comments():
    file = open('../csv文件/comments_cutShort.csv', 'w', encoding='utf-8', newline='')
    writer = csv.writer(file)
    head = ['rank','comment']
    writer.writerow(head)

    with open('../csv文件/comments.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        # 跳过行首
        next(reader)
        count = 0
        for row in reader:
            if count % 5000 == 0:
                print("Review %d " % count)
            rank = row[0]
            comment = row[1]
            review = ''.join(remove_pun_and_stopWords(comment).split(" ")[:-1])
            if len(review) < 6:
                print(count,comment)
                continue
            data_row = [rank, comment]
            writer.writerow(data_row)
            count += 1
    file.close()

# 影评分为两类
def divide_twoCategories():
    file = open('../csv文件/comments_cutShort_twoCategories.csv', 'w', encoding='utf-8', newline='')
    writer = csv.writer(file)
    head = ['rank','comment']
    writer.writerow(head)
    with open('../csv文件/comments_cutShort.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        # 跳过行首
        next(reader)
        count = 0
        for row in reader:
            if count % 5000 == 0:
                print("Review %d " % count)
            rank = row[0]
            comment = row[1]
            if int(rank) <= 3:
                rank = "差评"
            else:
                rank = '好评'
            data_row = [rank, comment]
            writer.writerow(data_row)
            count += 1
    file.close()

# 模型预测测试集分数
def compare():
    with open('../csv文件/test_gnb_word2vec.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        # 跳过行首
        next(reader)
        count = 0
        same = 0
        for row in reader:
            rank = row[0]
            result = row[1]
            if rank == result:
                same += 1
            count += 1
        print(same,count)
        print(same/count)
compare()