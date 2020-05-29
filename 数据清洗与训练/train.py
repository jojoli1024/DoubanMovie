from gensim.models import word2vec
from sklearn.model_selection import train_test_split,cross_val_score,GridSearchCV

from sklearn.naive_bayes import GaussianNB as GNB
from sklearn.linear_model import LogisticRegression as LR
from sklearn.ensemble import RandomForestClassifier as RF

from sklearn.metrics import accuracy_score,f1_score,roc_auc_score,auc,roc_curve,plot_roc_curve

from dataProcess import remove_pun_and_stopWords
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# word2vec词向量训练，仅用影评来训练有的词频低于5，而影评又过短，导致该影评没有词向量
def train_word2vec():
    # 模型参数
    num_features = 300    # 是指特征向量的维度，默认为100                      
    min_word_count = 20   # 可以对字典做截断. 词频少于min_count次数的单词会被丢弃掉, 默认值为5                        
    num_workers = 4       # 控制训练的并行参数
    context = 10          # 表示当前词与预测词在一个句子中的最大距离是多少                                                                                    
    downsampling = 1e-3   # 高频词汇的随机降采样的配置阈值，默认为1e-3，范围是(0,1e-5)
    sentences = word2vec.Text8Corpus('切词后txt文件/comments3.txt')
    model = word2vec.Word2Vec(sentences, workers=num_workers, size=num_features, min_count=min_word_count, window=context, sample=downsampling)
    # model = word2vec.Word2Vec(sentences)
    model.save('word2vec模型/comments3.model')

# 随机 7:3 分出训练集和测试集（也许可以用分层）
# 改用分层抽样
# 好评数量与差评一致
def get_train_test_set(commentPath,trainPath, testPath):
    data = pd.read_csv(commentPath)
    # 将样本分为x表示特征（影评），y表示类别（分数）
    # x = data.loc[:,'comment']
    y = data.loc[:,'rank']
    # 测试集为30%，训练集为70%(?验证集为20%)
    # x_train,x_test,y_train,y_test = train_test_split(x,y,test_size=0.3,random_state=0,stratify=y)
    train,test = train_test_split(data,test_size=0.3,stratify=y)
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

def naive_bayes(train_data_features,label,test_data_features,y_true):
    # 分类器训练
    # 多项式贝叶斯不能有负值
    # 贝叶斯为二分类问题，把打分改为好评，差评
    model_NB = GNB()
    model_NB.fit(train_data_features,label)
    # K折交叉验证
    score = np.mean(cross_val_score(model_NB,train_data_features,label,cv=10,scoring='roc_auc'))
    print("高斯贝叶斯分类器10折交叉验证得分：",score)  
    y_pred = model_NB.predict(test_data_features)
    get_result(y_true,y_pred)
    plot_roc_curve(model_NB, test_data_features, y_true)
    plt.show()


def linear_model(train_data_features,label,test_data_features,y_true):
    model_LR = LR(max_iter=1000)
    model_LR.fit(train_data_features,label)
    # K折交叉验证
    score = np.mean(cross_val_score(model_LR,train_data_features,label,cv=10,scoring='roc_auc'))
    print("逻辑回归分类器10折交叉验证得分：",score)    
    y_pred = model_LR.predict(test_data_features)
    get_result(y_true,y_pred)

def random_forest(train_data_features,label,test_data_features,y_true):
    model_RF = RF(n_estimators = 20, n_jobs=5)
    model_RF.fit(train_data_features,label)
    # K折交叉验证
    score = np.mean(cross_val_score(model_RF,train_data_features,label,cv=10,scoring='roc_auc'))
    print("随机森林分类器10折交叉验证得分：",score)    
    y_pred = model_RF.predict(test_data_features)
    get_result(y_true,y_pred)

def get_result(y_true,y_pred):
    # 测试集准确率
    print('分类器准确率：',accuracy_score(y_true,y_pred))
    # 测试集F1
    print('分类器F1：',f1_score(y_true,y_pred))
    # 测试集AUC
    print('分类器AUC：',roc_auc_score(y_true,y_pred))

if __name__ == "__main__":
    # 训练词向量模型
    # train_word2vec()
    commentPath = '../csv文件/comments_V2_1.csv'
    trainPath = '../csv文件/训练集和测试集/train_data.csv'
    testPath = '../csv文件/训练集和测试集/test_data.csv'
    wv_name = 'word2vec模型/comments2.model'
    # 随机分出训练集和测试集
    get_train_test_set(commentPath,trainPath,testPath)

    train = pd.read_csv(trainPath)
    # 将train分为x表示特征（影评），label表示类别（分数）
    train_x,label = train.loc[:,'comment'],train.loc[:,'rank']
    model_wv = word2vec.Word2Vec.load(wv_name)
    # word2vec模型训练的size参数，默认为100
    num_features = 300
    train_data_features = getAvgFeatureVecs(train_x,model_wv,num_features)

    test = pd.read_csv(testPath)
    # 将test分为x表示特征（影评），y表示类别（分数）
    test_x,test_y = test.loc[:,'comment'],test.loc[:,'rank']
    test_data_features = getAvgFeatureVecs(test_x,model_wv,num_features)
    
    naive_bayes(train_data_features,label,test_data_features,test_y)
    # linear_model(train_data_features,label,test_data_features,test_y)
    # random_forest(train_data_features,label,test_data_features,test_y)