#这个模块用来写从excel或者数据库输入资产与利率数据的函数
import openpyxl
import datetime
import FXIncome
def reading_excel(exceladdress):
    wb=openpyxl.load_workbook(exceladdress, data_only=True)





    ws=wb['hdp']
    hdplist=[]
    for i in ws.columns:

        if isinstance(i[0].value,datetime.datetime):
            date=i[0].value
            curve_mu = {
                '0': i[1].value,
                '3M': i[2].value,
                '6M': i[3].value,
                '9M': i[4].value,
                '1Y': i[5].value,
                '2Y': i[6].value,
                '3Y': i[7].value,
                '4Y': i[8].value,
                '5Y': i[9].value,
                '10Y': i[10].value,
                '20Y': i[11].value,
                '30Y': i[12].value}
            curve_flc = {
                '0': i[13].value,
                '3M': i[14].value,
                '6M': i[15].value,
                '9M': i[16].value,
                '1Y': i[17].value,
                '2Y': i[18].value,
                '3Y': i[19].value,
                '4Y': i[20].value,
                '5Y': i[21].value,
                '10Y': i[22].value,
                '20Y': i[23].value,
                '30Y': i[24].value}
            hdptem=FXIncome.Hdp(date,curve_mu,{},curve_flc)
            hdplist.append(hdptem)
    assementdate=hdplist[0].date
    curve=hdplist[0].curve_mu


    ws=wb['asset']
    assetlist=[]
    for i in ws.rows:
        if i[0].value=='债券代码':
            k=9
            buyselldic={}
            buyselllist=[]
            while True:
                buyselldic[i[k].value]={}
                buyselllist.append(i[k].value)
                k+=1
                try:
                    i[k].value
                except:
                    break
            times=len(buyselllist)
        else:
            code = i[3].value
            ctype = i[7].value
            initialdate = datetime.datetime.strptime(
                i[4].value.replace('-', ''), '%Y%m%d')
            enddate = datetime.datetime.strptime(
                i[5].value.replace('-', ''), '%Y%m%d')
            facevalue = i[1].value
            couponrate = i[6].value / 100
            frequency = i[8].value
            cleanprice = i[2].value
            asset = FXIncome.Bond(
                code,
                ctype,
                initialdate,
                enddate,
                facevalue,
                couponrate,
                assementdate,
                curve,
                frequency,
                cleanprice)
            assetlist.append(asset)
            for ii in range(0,times):
                if i[ii+9].value:
                    buyselldic[buyselllist[ii]][code]=i[ii+9].value
                    ii+=1
    for j in hdplist:
        j.buysell=buyselldic[j.date]
    return [assetlist,hdplist]

def reading_sql():
    pass

def reading_pd():
    pass
