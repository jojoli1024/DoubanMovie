from sklearn.feature_extraction.text import TfidfVectorizer as TFIDF 
from dataProcess import remove_pun_and_stopWords
import pandas as pd 
from sklearn.naive_bayes import MultinomialNB as MNB
from sklearn.model_selection import cross_val_score
from sklearn.metrics import accuracy_score,f1_score,roc_auc_score
import numpy as np
from train import linear_model,random_forest,get_result,get_train_test_set

def naive_bayes(train_data_features,label,test_data_features,y_true):
    model_NB = MNB()
    model_NB.fit(train_data_features, label)
    MNB(alpha=1.0, class_prior=None, fit_prior=True)
    # K折交叉验证
    score = np.mean(cross_val_score(model_NB,train_data_features,label,cv=10,scoring='roc_auc'))
    print("高斯贝叶斯分类器10折交叉验证得分：",score)  
    y_pred = model_NB.predict(test_data_features)
    get_result(y_true,y_pred)

if __name__ == "__main__":
    commentPath = '../csv文件/comments_V2_1.csv'
    trainPath = '../csv文件/train_data.csv'
    testPath = '../csv文件/test_data.csv'

    get_train_test_set(commentPath,trainPath,testPath)

    train = pd.read_csv(trainPath)
    test = pd.read_csv(testPath)
    train_x,train_y = train.loc[:,'comment'],train.loc[:,'rank']
    test_x,test_y = test.loc[:,'comment'],test.loc[:,'rank']
    train_data = []
    for i in train_x:
        train_data.append(" ".join(remove_pun_and_stopWords(i).split(" ")[:-1]))
    test_data = []
    for i in test_x:
        test_data.append(" ".join(remove_pun_and_stopWords(i).split(" ")[:-1]))
    tf_idf = TFIDF(min_df=2,        # 最小支持度为2
            max_features=None,
            strip_accents='unicode',
            analyzer='word',
            ngram_range=(1, 3),  # 二元文法模型
            use_idf=1,
            smooth_idf=1,
            sublinear_tf=1)      #token_pattern=r'\w{1,}',
    data_all = train_data + test_data
    len_train = len(train_data)

    tf_idf.fit(data_all)
    data_all = tf_idf.transform(data_all)
    # 恢复成训练集和测试集部分
    train_x = data_all[:len_train]
    test_x = data_all[len_train:]
    print('TF-IDF处理结束.')

    naive_bayes(train_x,train_y,test_x,test_y)
    linear_model(train_x,train_y,test_x,test_y)
    random_forest(train_x,train_y,test_x,test_y)