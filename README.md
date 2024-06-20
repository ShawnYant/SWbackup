# SWbackup
==============================================
===============For internal usage=============
==============================================

To manage the backup operation of both Cisco & 
Huawei devices. Also, firewall devices can be
included also. Servers are not concerned in 
this version.

This is Version One, it still comes with 
original codes. UI and further interaction 
interface are still in progress.

The results are shown in the auto-created fil-
es, also, there will be a auto-created file 
named'backup_failures.txt', to record the mis-
aligned info and mistakes.
================================================
===================CUG-ShanwYan=================
================================================

Python version-----3.X.X
Other plugins will need 
pip3 install XXXXX
you will find them in the headline of the script file. 
================================================
================================================
Operational steps
操作步驟：
1.按照==IP==Port==Username==Password==DeviceType=
格式建立Excel表格，一共四列；命名格式请按照
Location_CloudName_Device并存到SWBackupList里
2.文件
国产设备两个脚本都可以用；其它设备用Cisco+Other.py(还没测试过);
3.选择正确文件后，
将文件中def main()函数中的desktop_path填入
相应的本地地址（不是相对地址），默认存在backup
里面（如果不想换地方儿存就不用动它）；
将文件中def main()函数中的excel_path填入Excel
表格所在的本地地址（不是相对地址）；
4.确认以上操作无误后，打开Terminal(Crtl+Shift+`),
摁F5开始调试运行程序。
5.程序运行完成后会自动生成文件夹，将会和被读取的Excel
表格同名称，并会自动加上备份的日期。
==================================================
==================================================
Notice：
同一天备份同一份Excel表格，数据会直接覆盖在自动生成的
文件夹里。

相对地址是指相对脚本所在根目录的路径。我的脚本（.py文件）
所在的目录为根目录，而同时你的目标文件（Excel表格或者保
存路径的文件夹）又和脚本在同一个文件夹里（或者该根目录的
子文件夹里）的话，就可以不用‘绝对地址’（比如D:/hd/da.xlsx），
可以使用‘相对地址’（比如/SWBackupList/XXXX.xlsx，这种
情况‘/SWBackUpList’之前的‘D:/SWBACKUP’就可以省略。
因为脚本在SWBACKUP文件夹里，Python脚本会默认这个文件夹
为根目录）。
==================================================
==================================================
