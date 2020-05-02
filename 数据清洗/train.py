from gensim.models import word2vec
from sklearn.model_selection import train_test_split,cross_val_score
import numpy as np
import pandas as pd
from dataProcess import remove_pun_and_stopWords

# word2vec词向量训练，仅用影评来训练有的词频低于5，而影评又过短，导致该影评没有词向量
# 影评和wiki一起训练词向量
def train():
    sentences = word2vec.Text8Corpus('comments_wiki.txt')
    model = word2vec.Word2Vec(sentences)
    model.save('comments_wiki.model')

# 随机 7:3 分出训练集和测试集（也许可以用分层）
def get_train_test_set(commentPath,trainPath, testPath):
    data = pd.read_csv(commentPath)
    # 将样本分为x表示特征（影评），y表示类别（分数）
    # x,y = data.loc[:,'comment'],data.loc[:,'rank']
    # 测试集为30%，训练集为70%(?验证集为20%)
    # x_train,x_test,y_train,y_test = train_test_split(x,y,test_size=0.3,random_state=0)
    # print(x_train)
    # 测试集为30%，训练集为70%，需要验证集吗？
    train,test = train_test_split(data,test_size=0.3)
    # 将训练集与数据集的数据分别保存为CSV文件
    train.to_csv(trainPath,index=False)
    test.to_csv(testPath,index=False)

# 词向量取平均值
# 对段落中的所有词向量进行取平均操作
def makeFeatureVec(wordList, model, num_features):
    featureVec = np.zeros((num_features,), dtype="float32")
    count = 0
    # Index2word包含了词表中的所有词，为了检索速度，保存到set中
    index2word_set = set(model.wv.index2word)
    for word in wordList:
        if word in index2word_set:
            count += 1
            featureVec = np.add(featureVec, model.wv[word])
            # featureVec += model.wv[word]
    # 取平均
    # 除法遇到无效值
    # featureVec = np.divide(featureVec, count)
    if count == 0:
        print(wordList)
    featureVec /= count
    # 如果有nan值，取行平均值
    # featureVec[np.isnan(featureVec)] = np.nanmean(featureVec)
    return featureVec

# 给定一个文本列表，每个文本由一个词列表组成，返回每个文本的词向量平均值
def getAvgFeatureVecs(reviews, model, num_features):
    counter = 0
    reviewFeatureVecs = np.zeros((len(reviews), num_features), dtype="float32")
    for review in reviews:
        if counter % 5000 == 0:
            print("Review %d of %d" % (counter, len(reviews)))
        # 预处理，变为词列表
        comment = remove_pun_and_stopWords(review).split(" ")[:-1]
        reviewFeatureVecs[counter] = makeFeatureVec(comment, model, num_features)
        counter = counter + 1
    return reviewFeatureVecs

# 训练词向量模型
# train()

commentPath = '../csv文件/comments_cutShort_twoCategories.csv'
trainPath = '../csv文件/train_data.csv'
testPath = '../csv文件/test_data.csv'


# 随机分出训练集和测试集
get_train_test_set(commentPath,trainPath, testPath)


# 分类器训练
# 在sklearn中，提供了3中朴素贝叶斯分类算法：GaussianNB(高斯朴素贝叶斯)、MultinomialNB(多项式朴素贝叶斯)、BernoulliNB(伯努利朴素贝叶斯)
from sklearn.naive_bayes import GaussianNB as GNB

train = pd.read_csv(trainPath)

# 将train分为x表示特征（影评），label表示类别（分数）
train_x,label = train.loc[:,'comment'],train.loc[:,'rank']
model_wv = word2vec.Word2Vec.load('comments1.model')
# word2vec模型训练的size参数，默认为100
num_features = 100
# print(type(train_x))
train_data_features = getAvgFeatureVecs(train_x,model_wv,num_features)

# 多项式贝叶斯不能有负值
# 贝叶斯为二分类问题，把打分改为好评，差评
model_NB = GNB()
model_NB.fit(train_data_features,label)
# K折交叉验证
score = np.mean(cross_val_score(model_NB,train_data_features,label,cv=5,scoring='roc_auc'))
print("多项式贝叶斯分类器5折交叉验证得分：",score)

test = pd.read_csv(testPath)

# 将test分为x表示特征（影评），y表示类别（分数）
test_x,test_y = test.loc[:,'comment'],test.loc[:,'rank']
test_data_features = getAvgFeatureVecs(test_x,model_wv,num_features)
result = model_NB.predict(test_data_features)
output = pd.DataFrame( data={"rank":test.loc[:,"rank"], "result":result} )
output.to_csv( "test_gnb_word2vec.csv", index=False, quoting=3 )