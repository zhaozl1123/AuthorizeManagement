# 主要功能

用于3DS <sup>TM</sup> 产品的授权和认证过程的调用：

  > 接口描述详细文档与测试用例见: https://documenter.getpostman.com/view/16609215/2s93mATzCG

1. `generateAuthorization.py`将授权过程封装成了具有RestfulAPI接口的服务，使用如下命令进行部署：

   ```bash
   python generateAuthorization.py --apihost {apihost} --apiport {apiport}
   ```

   > apihost：默认为127.0.0.1
   >
   > apihort：默认为8300
   >
   > 注：要求使用minio作为授权文件存储引擎，并定义该服务参数如下，后期更新为可自定义参数：
   >
   > 127.0.0.1:9000, access_key="minioadmin", secret_key="minioadmin”
   >
   > API文档见下文

2. `Method_Authorize`提供py与so版本（暂未做CentOS7.9+Python3.7.4环境下的运行测试），其中包括授权过程与鉴权过程，相关API接口见下文。

# 关于授权与鉴权

## 授权接口的使用

授权接口使用RestfulAPI进行了封装，正确发布API服务后，可以使用如下方法进行功能调用。

### 查询环境变量

``` python
"""
查看当前默认的基础环境信息及能查询到的核心环境信息

Example
-------
获取基础环境信息
`[GET] http://{{host}}:{{port}}/info/?quest=basic_env_info`

获取核心环境信息
`[GET] http://{{host}}:{{port}}/info/?quest=core_env_info`

获取所有环境信息
`[GET] http://{{host}}:{{port}}/info/?quest=all`

:return: str，基础环境信息、核心环境信息或两者
"""
```

### 生成授权文件

```python
"""
在后台生成授权文件

Example
-------
basic_env_info: json格式，用于授权文件的生成，必要参数，不可为空。形如，{
"plant": "葛洲坝电厂",
"unit": "1、2#",
"author": "东方电气集团东方电机有限公司",
"validityDate": "2023-12-31 00:00:00.000",
"announcement": "【法律声明】"
}

with_core_env_info：用于授权文件的生成，是否调用核心环境变量，可为空，默认False，进一步指示前不使用核心环境变量做授权控制

`[GET] http://{{host}}:{{port}}/generate/?basic_env_info={basic_env_info}&&with_core_env_info={with_core_env_info}`

:return: json，生成授权的情况：时间、基础环境信息、授权过程是否包含核心环境变量
"""
```

### 确认授权并完成存储

```python
"""
确认授权、存储授权文件
TODO:后续补充专用下载接口

Example
-------
projectName: 全小写字母、可以使用“-”连接的bucketName，建议项目名，非必要参数，默认default

functionModuleName：被授权的功能名称，无符号中英文大小写，用于对授权文件进行命名，非必要参数，默认default

tags：用于标识的授权信息，如版本号、备注等，为空则使用默认值{'version': 'v0.0', 'remark': 'None'}

miniohost：OSS的host，默认"127.0.0.1"

minioport：OSS的port，默认"9000"

miniouser：OSS的用户名，默认"minioadmin"

miniopwd：OSS的密码，默认"minioadmin"

`[GET] http://{{host}}:{{port}}/confirmAndDownload/?projectName={projectName}&&functionModuleName={functionModuleName}&&tags={tags}`


:return: 返回接口服务状态信息
"""
```

使用`generateAuthorization.py`生成的授权文件包`authorizedFile.rar`的内容物包括：`authInfo.txt`、`privateKey.txt`、`publicKey.txt`。

`authInfo.txt`中是在授权前，用以描述被授权主主体信息的dict型字符串

`privateKey.txt`中是授权秘钥主体

`publicKey.txt`中是授权秘钥主体

## 鉴权接口的使用

`Method_Authorize.py`中提供了修饰器`AuthorizationValidate`，其功能描述如下：

    """
    用于装饰所有需要进行认证的函数
    
    :param authInfo: dict, 基本授权信息,形如:{
            'plant': '葛洲坝智能诊断决策系统',
            'unit': '1#机',
            'validityDate': '2023-12-31 00:00:00.000',
        }
    :param privateKeyPath: str,授权文件（私钥）地址与文件名，形如:"./privateKey.txt"
    :param publicKey: str,公钥字符串，形如:"eyd9JzogJzAxMTExM"
    :param withCoreEnv: bool，是否使用深层硬件环境变量进行授权认证
    """

在调用授权对象时，需参照下述方式：

```python
# 导入环境
from Method_Authorize import AuthorizationValidate


# 来自授权文件 authInfo
AUTH_INFO = {
  'plant': '葛洲坝电厂', 
  'unit': '1、2机', 
  'author': '东方电气集团东方电机有限公司', 
  'validityDate': '2023-12-31 00:00:00.000', 
  'announcement': '【法律声明】'}
# 授权文件 privateKey
privateKeyPath = "./privateKey.txt"
# 授权文件 publicKey
publicKey = "eydkJzogJzAxMDAwMTEnLCAnNyc6ICcwMTExMCcsICcwJzogJzAwJywgJzInOiAnMDExMTEnLCAnMSc6ICcwMTAxMDEnLCAnMyc6ICcwMTEwMCcsICdlJzogJzAxMDExMTEnLCAnNic6ICcwMTEwMScsICdmJzogJzAxMDExMTAxJywgJzgnOiAnMDEwMDAxMCcsICc1JzogJzAxMDAxJywgJ2InOiAnMDEwMTExMDAnLCAnYyc6ICcwMTAwMDAnLCAnYSc6ICcwMTAxMTAxJywgJzQnOiAnMDEwMTAwJywgJzknOiAnMDEwMTEwMCd9"


# 使用修饰器AuthorizationValidate，并定义其参数，参数来源为授权文件包
@AuthorizationValidate(authInfo=AUTH_INFO, privateKeyPath=privateKeyPath, publicKey=publicKey, withCoreEnv=False)
def SomeFunction($$$):  # 需要进行授权保护的主体，一般出现在Method_XXX中
	$$$
	return $$$
```


