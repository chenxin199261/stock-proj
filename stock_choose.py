import pickle
import numpy as np
import baostock as bs
import pandas as pd

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
    stackTY = np.stack((T, Y), axis=-1)
    
    return(stackTY)

def checkMRQ(icode):
    lg = bs.login()
    rs = bs.query_history_k_data_plus( icode ,
        "open,high,low,close,pbMRQ,psTTM",
            start_date='2022-08-05', end_date='2022-08-05',
                frequency="d", adjustflag="3")
    result_list = []
    while (rs.error_code == '0') & rs.next():
        result_list.append(rs.get_row_data())
    #print(result_list)
    return(float(result_list[0][4]),float(result_list[0][5]),float(result_list[0][3]))

    bs.logout()


#
#  Get the name of the stock according to the code.
#
def checkName(icode):

    lg = bs.login()
    rs = bs.query_stock_basic(code=icode)

    data_list = []
    while (rs.error_code == '0') & rs.next():
         data_list.append(rs.get_row_data())

    bs.logout()
    return(data_list[0][1])




def stasticMeanMaxMin(data):

    selectStock={}
    # icode:[Name,+%,-%,MeanOpen,MRQ,currentPrice]
    #
    #
    for istock in data:
        OpenData = Restore[istock]['open']
        TimeSeriesOpen = transDicToSeries(OpenData)
        DataSeries = np.array(TimeSeriesOpen[:,1]).astype(float)
        MaxOpen =  DataSeries.max()
        MinOpen =  DataSeries.min()
        MeanOpen = DataSeries.mean()
        PositiveDerive = (MaxOpen-MeanOpen)/(MeanOpen)*100
        NegativeDerive = (MeanOpen-MinOpen)/(MeanOpen)*100
        if(PositiveDerive<43  and NegativeDerive<43 and len(DataSeries)>430 ):
            Name = checkName(istock)
            MRQ,TTM,PRC = checkMRQ(istock)
            selectStock[istock] = [Name,PositiveDerive,NegativeDerive,MeanOpen,MRQ,PRC]
            print(istock,Name,":   %5.2f      %5.2f     %5.2f   %5.2f     %5.2f" \
                    % (PositiveDerive,NegativeDerive,MeanOpen,MRQ,PRC))

    Fpickleindex=open("stock_selected.pl",'wb')
    pickle.dump(selectStock,Fpickleindex)
    Fpickleindex.close()  



if __name__ == "__main__": 
    print("Loading Stocks HS300 and ZZ500:'2020-05-05' to '2022-05-05'")
    FpickleR=open("History.pl",'rb')
    Restore = pickle.load(FpickleR)
    print(len(Restore)," stocks loaded")
    stasticMeanMaxMin(Restore)
    
