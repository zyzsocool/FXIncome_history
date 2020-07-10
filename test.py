import FXIncome
exceladdress='C:\\Users\\zyzse\\Desktop\\模板.xlsx'
[assetlist,hdplist]=FXIncome.reading_excel(exceladdress)
myprofilo=FXIncome.Profolio(assetlist,hdplist)


#1.tpl算法
myprofilo.bsforcast_tpl()
#2.tpl蒙特卡洛算法（画图，不输入数字就默认模拟1000次）
myprofilo.bsforcast_tpl_plot()
#3.oci算法
myprofilo.bsforcast_oci()
#4.oci蒙特卡洛算法（画图，要算很久，不输入数字就默认模拟1000次）
myprofilo.bsforcast_oci_plot(100)