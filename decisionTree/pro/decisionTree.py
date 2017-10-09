# -*- coding: utf-8 -*-

from math import log
import operator
import treePlotter
import numpy as np
import re


def splitDataSet_for_dec(dataSet, axis, value, small):
    returnSet = []
    for featVec in dataSet:
        if (small and featVec[axis] <= value) or ((not small) and featVec[axis] > value):
            retVec = featVec[:axis]
            retVec.extend(featVec[axis + 1:])
            returnSet.append(retVec)
    return returnSet

def DataSetPredo(decreteindex):
    '''
    预处理函数DataSetPredo，对数据集提前离散化
    '''
    dataSet=createDataSet()
    labels=getlabels()
    Entropy = calcShannonEnt(dataSet)
    DataSetlen = len(dataSet)
    for index in decreteindex:  # 对每一个是连续值的属性下标
        for i in range(DataSetlen):
            dataSet[i][index] = float(dataSet[i][index])
        allvalue = [vec[index] for vec in dataSet]
        sortedallvalue = sorted(allvalue)
        T = []
        for i in range(len(allvalue) - 1):  # 划分点集合
            T.append(float(sortedallvalue[i] + sortedallvalue[i + 1]) / 2.0)
        bestGain = 0.0
        bestpt = -1.0
        for pt in T:  # 对每个划分点
            nowent = 0.0
            for small in range(2):  # 化为正类负类
                Dt = splitDataSet_for_dec(dataSet, index, pt, small)
                p = len(Dt) / float(DataSetlen)
                nowent += p * calcShannonEnt(Dt)
            if Entropy - nowent > bestGain:
                bestGain = Entropy - nowent
                bestpt = pt
        labels[index] = str(labels[index] + "<=" + "%.3f" % bestpt)
        for i in range(DataSetlen):
            dataSet[i][index] = "是" if dataSet[i][index] <= bestpt else "否"
    return dataSet, labels

def calcShannonEnt(dataSet):
    """
    输入：数据集
    输出：数据集的香农熵
    描述：计算给定数据集的香农熵
    """
    numEntries = len(dataSet)
    labelCounts = {}
    for featVec in dataSet:
        currentLabel = featVec[-1]
        if currentLabel not in labelCounts.keys():
            labelCounts[currentLabel] = 0
        labelCounts[currentLabel] += 1
    shannonEnt = 0.0
    for key in labelCounts:
        prob = float(labelCounts[key])/numEntries
        shannonEnt -= prob * log(prob, 2)
    return shannonEnt

def splitDataSet(dataSet, axis, value):
    """
    输入：数据集，选择维度，选择值
    输出：划分数据集
    描述：按照给定特征划分数据集；去除选择维度中等于选择值的项
    """
    retDataSet = []
    for featVec in dataSet:
        if featVec[axis] == value:
            reduceFeatVec = featVec[:axis]
            reduceFeatVec.extend(featVec[axis+1:])
            retDataSet.append(reduceFeatVec)
    return retDataSet

def ID3Split(dataSet):
    """
    输入：数据集
    输出：最好的划分维度
    描述：选择最好的数据集划分维度
    """
    numFeatures = len(dataSet[0]) - 1
    baseEntropy = calcShannonEnt(dataSet)
    bestInfoGain = 0.0
    bestFeature = -1
    for i in range(numFeatures):
        featList = [example[i] for example in dataSet]
        uniqueVals = set(featList)
        newEntropy = 0.0
        for value in uniqueVals:
            subDataSet = splitDataSet(dataSet, i, value)
            prob = len(subDataSet)/float(len(dataSet))
            newEntropy += prob * calcShannonEnt(subDataSet)
        infoGain = baseEntropy - newEntropy
        if (infoGain > bestInfoGain):
            bestInfoGain = infoGain
            bestFeature = i
    return bestFeature

def C4_5Split(dataSet):
    """
    输入：数据集
    输出：最好的划分维度
    描述：选择最好的数据集划分维度
    """
    numFeatures = len(dataSet[0]) - 1
    baseEntropy = calcShannonEnt(dataSet)
    bestInfoGainRatio = 0.0
    bestFeature = -1
    for i in range(numFeatures):
        featList = [example[i] for example in dataSet]
        uniqueVals = set(featList)
        newEntropy = 0.0
        splitInfo = 0.0
        for value in uniqueVals:
            subDataSet = splitDataSet(dataSet, i, value)
            prob = len(subDataSet)/float(len(dataSet))
            newEntropy += prob * calcShannonEnt(subDataSet)
            splitInfo += -prob * log(prob, 2)
        infoGain = baseEntropy - newEntropy
        if (splitInfo == 0): # fix the overflow bug
            continue
        infoGainRatio = infoGain / splitInfo
        if (infoGainRatio > bestInfoGainRatio):
            bestInfoGainRatio = infoGainRatio
            bestFeature = i
    return bestFeature

def CARTSplit(dataSet):
    """
    输入：数据集
    输出：最好的划分维度
    描述：选择最好的数据集划分维度
    """
    numFeatures = len(dataSet[0]) - 1
    bestGini = 999999.0
    bestFeature = -1
    for i in range(numFeatures):
        featList = [example[i] for example in dataSet]
        uniqueVals = set(featList)
        gini = 0.0
        for value in uniqueVals:
            subDataSet = splitDataSet(dataSet, i, value)
            prob = len(subDataSet)/float(len(dataSet))
            subProb = len(splitDataSet(subDataSet, -1, 'N')) / float(len(subDataSet))
            gini += prob * (1.0 - pow(subProb, 2) - pow(1 - subProb, 2))
        if (gini < bestGini):
            bestGini = gini
            bestFeature = i
    return bestFeature

def majorityCnt(classList):
    """
    输入：分类类别列表
    输出：子节点的分类
    描述：数据集已经处理了所有属性，但是类标签依然不是唯一的，
          采用多数判决的方法决定该子节点的分类
    """
    classCount = {}
    for vote in classList:
        if vote not in classCount.keys():
            classCount[vote] = 0
        classCount[vote] += 1
    sortedClassCount = sorted(classCount.items(), key=operator.itemgetter(1), reverse=True)
    return sortedClassCount[0][0]

def createTree(dataSet, labels,chooseBestFeatureToSplit):
    """
    输入：数据集，特征标签
    输出：决策树
    描述：递归构建决策树，利用上述的函数
    """
    classList = [example[-1] for example in dataSet]
    if classList.count(classList[0]) == len(classList):
        # 类别完全相同，停止划分
        return classList[0]
    if len(dataSet[0]) == 1:#分完了，没有属性了
        # 遍历完所有特征时返回出现次数最多的
        return majorityCnt(classList)
    bestFeat = chooseBestFeatureToSplit(dataSet)
    bestFeatLabel = labels[bestFeat]
    myTree = {bestFeatLabel:{}}
    del(labels[bestFeat])
    # 得到列表包括节点所有的属性值
    featValues = [example[bestFeat] for example in dataSet]
    uniqueVals = set(featValues)
    for value in uniqueVals:
        subLabels = labels[:]
        myTree[bestFeatLabel][value] = createTree(splitDataSet(dataSet, bestFeat, value), subLabels,chooseBestFeatureToSplit)
    return myTree


def classify(inputTree, featLabels, testVec):
    """
    输入：决策树，分类标签，测试数据
    输出：决策结果
    描述：跑决策树
    """
    firstStr = list(inputTree.keys())[0]
    secondDict = inputTree[firstStr]
    featIndex = featLabels.index(firstStr)
    classLabel = '否'
    for key in secondDict.keys():
        if testVec[featIndex] == key:
            if type(secondDict[key]).__name__ == 'dict':
                classLabel = classify(secondDict[key], featLabels, testVec)
            else:
                classLabel = secondDict[key]
    return classLabel

def classifyAll(inputTree, featLabels, testDataSet):
    """
    输入：决策树，分类标签，测试数据集
    输出：决策结果
    描述：跑决策树
    """
    print('classifying:')
    classLabelAll = []
    accuracy=0
    for testVec in testDataSet:
        className=classify(inputTree, featLabels, testVec)
        print(str(testVec[:-1]) + ' is classified as ' + className + ' ,and it\'s class is ' + testVec[-1])
        classLabelAll.append(className)
        if testVec[-1]==className:
            accuracy+=1
    return classLabelAll,float(accuracy/len(testDataSet))

def storeTree(inputTree, filename):
    """
    输入：决策树，保存文件路径
    输出：
    描述：保存决策树到文件
    """
    import pickle
    fw = open(filename, 'wb')
    pickle.dump(inputTree, fw)
    fw.close()

def grabTree(filename):
    """
    输入：文件路径名
    输出：决策树
    描述：从文件读取决策树
    """
    import pickle
    fr = open(filename, 'rb')
    return pickle.load(fr)

def getlabels():
    '''
    获取属性名
    '''
    # labels=['Clump Thickness','Uniformity of Cell Size','Uniformity of Cell Shape','Marginal Adhesion',
    #         'Single Epithelial Cell Size','Bare Nuclei','Bland Chromatin','Normal Nucleoli','Mitoses','Class']
    f=open(r'names.txt','r')
    labels=[w for w in f.readlines()[0].strip('\n').split(',')[1:]]
    return labels

def createDataSet():
    '''
    获取dataset
    '''
    f=open(r'traindata.txt','r')
    dataSet=[]
    raw=f.readlines()
    for line in raw:
        dataSet.append([w for w in line.strip('\n').split(',')[1:]])
    return dataSet

def createTestSet():
    f=open(r'testdata.txt','r')
    testSet=[]
    raw=f.readlines()
    for line in raw:
        testSet.append([w for w in line.strip('\n').split(',')[1:]])
    return testSet

def main():
    dataSet,labels= DataSetPredo([6,7])
    #labels=getlabels()
    labels_tmp = labels[:]  # 拷贝，createTree会改变labels
    desicionTree = createTree(dataSet, labels_tmp, ID3Split)
    #desicionTree = createTree(dataSet, labels_tmp, C4_5Split)
    #desicionTree = createTree(dataSet, labels_tmp, CARTSplit)
    print('desicionTree:\n', desicionTree)
    treePlotter.createPlot(desicionTree)
    testSet = createTestSet()
    print('classifyResult:\n', classifyAll(desicionTree, labels, testSet))

if __name__ == '__main__':
    main()