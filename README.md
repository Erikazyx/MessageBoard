# 可以过滤异常留言的留言板

通过fingerprint获取浏览器ID，以此来分辨提交留言的用户。

如果5秒内多次尝试发表留言，得通过验证才能继续发表。
>使用方法:  
>1.安装pipenv、redis、mysql  
    2.pipenv shell  
    3.pipenv install   
    4.用mysql创建一个数据表，按自己情况修改config.py    
    5.运行

实例地址：http://149.28.78.176:500/