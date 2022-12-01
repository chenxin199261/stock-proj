import pickle
import numpy as np
import baostock as bs
import pandas as pd
from datetime import datetime
from union_find import *
import itertools as it

def spearmanCC_CORE(X,Y):
    temp = X.argsort()
    ranksX = np.empty_like(temp)
    ranksX[temp] = np.arange(len(X))
    
    temp = Y.argsort()
    ranksY = np.empty_like(temp)
    ranksY[temp] = np.arange(len(Y)) 
    return( 1 - ( 6 * np.sum( (ranksY-ranksX)**2) )/(len(X)*(len(X)**2 -1  ))   )

def spearmanCC(T1,T2,price1,price2):

#  T1,T2         : [t1,t2,t3]
#  price1,price2 : dictionary, {t1:price}
#
    T1 = set(T1)
    T2 = set(T2)
    T = list(T1&T2)
    T.sort(key=lambda date: datetime.strptime(date, "%Y-%m-%d"))
    X = np.array([price1[k] for k in T])
    Y = np.array([price2[k] for k in T])
    return(spearmanCC_CORE(X,Y))


def transDicToSeries(Seriesdic):
# In {Time1:data1,Time2:data2,...}
# Out [[T1,D1],[T2,D2]]
    T = []
    Y = []
    for key in Seriesdic:
        T.append(key)
        Y.append(float(Seriesdic[key]))
    T.reverse()
    Y.reverse()
    return(T,np.array(Y))



def Ana_cluster(Rec_price,Rec_selected):
    import networkx as nx
    import networkx.algorithms.community as nx_comm
    from networkx.drawing.nx_pydot import write_dot
    # Get close price
    CodeList=[]
    for icode in Rec_selected:
        closePrice = Rec_price[icode]['close']
        T,closePriceL = transDicToSeries(closePrice)
        Rec_selected[icode].append(T)
        Rec_selected[icode].append(closePrice)
        CodeList.append(icode)
        
    # Rec_selected add price record
    # icode:[Name,+%,-%,MeanOpen,MRQ,currentPrice,T,priceRec]

    G = nx.Graph()

    CodeList = CodeList[0:120]
    Nstock = len(CodeList)
    LinkMart = np.eye(Nstock)
    # Add stock to graph:
    for istock in  CodeList:
        G.add_node(istock)

    
    for i in range(Nstock-1):
        for j in range(i+1,Nstock):
            X = Rec_selected[CodeList[i]]
            Y = Rec_selected[CodeList[j]]
            CC = spearmanCC(X[6],Y[6],X[7],Y[7])
            #Add edges:
            if(CC>0.5):
                G.add_edge(CodeList[i], CodeList[j],weight=CC)
            
            #Build linked martrix
            if(CC>0.9): #print(i,j,X[0],Y[0],CodeList[i],CodeList[j],CC)
                LinkMart[i][j] = 1
                LinkMart[j][i] = 1
            if(CC<-0.9): print(i,j,X[0],Y[0],CodeList[i],CodeList[j],CC)

    write_dot(G,"corr.dot")
    T = nx_comm.louvain_communities(G, seed=123,weight='weight',resolution=1.5)
    print(T)
    print("======1.3")
    for community in T:
        print(community)
        for a,b in it.combinations(community, 2):
            if(G.has_edge(a,b)): 
                print(a,b,G[a][b]["weight"])
            else:
                print(a,b,"   no")
#    T=nx.minimum_spanning_tree(G)
#    print(sorted(T.edges(data=True)))
  
    '''
    mask_block = np.full((Nstock,Nstock), 0.1)
    LinkMart_TF =   LinkMart > mask_block 
    uf = groupSplit(LinkMart_TF)
    stockBatch = uf.components()
    nBatch = len(stockBatch)
    print(nBatch)
    for batch in stockBatch:
        for i in batch:
            code = CodeList[i]
            print(Rec_selected[code][0:6],code)
        print("=========")
    '''



if __name__ == "__main__": 
    print("Loading Stocks HS300 and ZZ500:'2020-05-05' to '2022-05-05'")
    FpickleR=open("History.pl",'rb')
    Restore = pickle.load(FpickleR)
    print(len(Restore)," stock prices loaded")

    # Load Selected stocks
    Fselected = open("stock_selected.pl",'rb')
    selectedStock = pickle.load(Fselected)
    print(len(selectedStock)," selected stocks loaded")

    Ana_cluster(Restore,selectedStock)
