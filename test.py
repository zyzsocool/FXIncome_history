#只测试实际使用时要用到的函数
import fxincome

# 1数据读入
exceladdress='./模板.xlsx'
[positionlist,hdplist]=fxincome.reading_excel(exceladdress)
myprofilo=fxincome.Portfolio(positionlist, hdplist)


# 2.1tpl算法
myprofilo.bsforcast_tpl()
# 2.2tpl蒙特卡洛算法（画图，不输入数字就默认模拟1000次）
myprofilo.bsforcast_tpl_plot()
# 2.3oci算法
myprofilo.bsforcast_oci()
# 2.4oci蒙特卡洛算法（画图，要算很久，不输入数字就默认模拟1000次）
myprofilo.bsforcast_oci_plot(1)