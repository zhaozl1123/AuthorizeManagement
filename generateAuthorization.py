import os, argparse

from minio import Minio
from minio.tagging import Tags

from Method_Authorize import ProductAuthorization, getEnvParams
from flask import Flask, request, Response
from commonMethods_zhaozl_green.core import printWithColor

import json, time
from zipfile import ZipFile


app = Flask(__name__)

AUTH_INFO = {
    "plant": "葛洲坝电厂",
    "unit": "1、2#",
    "author": "东方电气集团东方电机有限公司",
    "validityDate": "2023-12-31 00:00:00.000",
    "announcement": "【法律声明】"
}


@app.route('/', methods=['GET', 'POST'])
def defaultPage():
    return '该程序用于实现对3DS产品的算子进行授权及下载当期授权的文件。<br>' \
           '对已授权产品的查询与管理需至minio的前端服务界面。'


@app.route('/info/', methods=['GET'])
def getInfoByParam():
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
    global AUTH_INFO

    __coreInfo = {}
    try:
        __coreInfo = getEnvParams()
    except:
        pass

    _options = {
        "basic_env_info": AUTH_INFO,
        "core_env_info": __coreInfo,
        "all": {**AUTH_INFO, **__coreInfo},
    }
    return _options[request.args.get("quest")]


@app.route('/generate/', methods=['GET'])
def generateAuthFile():
    """
    在后台生成授权文件

    Example
    -------
    basic_env_info: 形如，{
        "plant": "葛洲坝电厂",
        "unit": "1、2#",
        "author": "东方电气集团东方电机有限公司",
        "validityDate": "2023-12-31 00:00:00.000",
        "announcement": "【法律声明】"
    }

    with_core_env_info：默认False，进一步指示前不使用核心环境变量做授权控制

    `[GET] http://{{host}}:{{port}}/generate/?basic_env_info={basic_env_info}&&with_core_env_info={with_core_env_info}`

    :return: json，生成授权的情况：时间、基础环境信息、授权过程是否包含核心环境变量
    """
    global AUTH_INFO

    requestParamsDict = request.args.to_dict()
    requestKeys = requestParamsDict.keys()
    basic_env_info = eval(request.args.get("basic_env_info")) if "basic_env_info" in requestKeys else AUTH_INFO
    with_core_env_info = eval(request.args.get("with_core_env_info").capitalize()) if "with_core_env_info" in requestKeys else False
    output = True
    outputPath = "./"
    productAuth = ProductAuthorization()
    productAuth.setBasicAuthInfo(basic_env_info, withCoreEnvParams=with_core_env_info)
    productAuth.generateAuthorizationFile(output=output, outputPath=outputPath)
    execTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    printWithColor(f"生成了一次授权", fontStyle="bold", backColor="green", fontColor="white", prefix="", suffix="", withTime=True)
    printWithColor(f"\t【basic_env_info】{basic_env_info}", fontStyle="bold", backColor="yellow", fontColor="blue", prefix="", suffix="", withTime=True)
    printWithColor(f"\t【with_core_env_info】{with_core_env_info}", fontStyle="bold", backColor="yellow", fontColor="blue", prefix="", suffix="", withTime=True)
    return json.dumps({
        "status": "已生成",
        "authorizedTime": execTime,
        "basic_env_info": basic_env_info,
        "with_core_env_info": with_core_env_info,
    })


@app.route('/confirmAndDownload/', methods=['GET'])
def confirm_download_store():
    """
    确认授权、存储授权文件
    TODO:并提供下载服务(在专用接口进行授权文件包的下载)

    Example
    -------
    projectName: 全小写字母、可以使用“-”连接的bucketName，建议项目名，非必要参数，默认default

    functionModuleName：被授权的功能名称，无符号中英文大小写，用于对授权文件进行命名，非必要参数，默认default

    tags：用于标识的授权信息，如版本号、备注等，为空则使用默认值{'version': 'v0.0', 'remark': 'None'}

    miniohost：OSS的host，默认"127.0.0.1"

    minioport：OSS的port，默认"9000"

    miniouser：OSS的用户名，默认"minioadmin"

    miniopwd：OSS的密码，默认"minioadmin"

    `[GET] http://{{host}}:{{port}}/confirmAndDownload/?projectName={projectName}&&functionModuleName={functionModuleName}&&tags={tags}&&miniohost={miniohost}&&minioport={minioport}&&miniouser={miniouser}&&miniopwd={miniopwd}`


    :return: 下载对象
    """
    """解析http请求"""
    requestParamsDict = request.args.to_dict()
    requestKeys = requestParamsDict.keys()
    _projectName = request.args.get("projectName") if "projectName" in requestKeys else "default"
    _functionModuleName = request.args.get("functionModuleName") if "functionModuleName" in requestKeys else "default"
    _miniohost = request.args.get("miniohost") if "miniohost" in requestKeys else "127.0.0.1"
    _minioport = request.args.get("minioport") if "minioport" in requestKeys else "9000"
    _miniouser = request.args.get("miniouser") if "miniouser" in requestKeys else "minioadmin"
    _miniopwd = request.args.get("miniopwd") if "miniopwd" in requestKeys else "minioadmin"
    _tagsDict = eval(request.args.get("tags") if "tags" in requestKeys else "{'version': 'v0.0', 'remark': 'None'}")
    """生成minio对象标签"""
    tags = Tags(for_object=True)
    for item in _tagsDict.keys():
        tags[item] = _tagsDict[item]
    """操作文件对象"""
    try:
        os.remove(f"./authorizedFile.rar")
    except:
        pass
    _zipFile = ZipFile("./authorizedFile.rar", 'a')
    try:
        _zipFile.write('./authInfo.txt')
    except:
        pass
    finally:
        os.remove(f"./authInfo.txt")
    try:
        _zipFile.write('./publicKey.txt')
    except:
        pass
    finally:
        os.remove(f"./publicKey.txt")
    try:
        _zipFile.write('./privateKey.txt')
    except:
        pass
    finally:
        os.remove(f"./privateKey.txt")
    _zipFile.close()
    with open("./authorizedFile.rar", "rb") as file:
        _zipFile = file.readlines()
        file.close()
    """上传文件"""
    # response = Response(_zipFile, content_type='text/plain')
    # response.headers["Content-disposition"] = f'attachment; filename="authorizedFile.rar"'
    execTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    client = Minio(f"{_miniohost}:{_minioport}", access_key=_miniouser, secret_key=_miniopwd, secure=False)
    if not client.bucket_exists(_projectName.lower()):
        client.make_bucket(_projectName.lower())
    client.fput_object(
        _projectName.lower(),
        f"[{execTime}]_{_functionModuleName}_授权文件", "./authorizedFile.rar",
        tags=tags
    )
    # return response
    return json.dumps({
        "status": "已上载",
        "uploadTime": execTime,
        "projectName": _projectName,
        "minio": {
            "host": _miniohost,
            "port": _minioport,
            "user": _miniouser,
            "password": _miniopwd,
        },
    })


def main(args):
    app.run(args.apihost, args.apiport)


if __name__ == '__main__':
    argParser = argparse.ArgumentParser()
    argParser.add_argument("--apihost", default="127.0.0.1", type=str, help="IP地址，缺省 127.0.0.1", dest="apihost")
    argParser.add_argument("--apiport", default=8300, type=int, help="端口号，缺省 8300", dest="apiport")
    arg = argParser.parse_args()
    main(arg)

