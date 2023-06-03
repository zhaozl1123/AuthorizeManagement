import datetime
import json

import streamlit as st
from PIL import Image
import requests

imagePath = Image.open("./DEC-logo-whiteBgBlueFont.jpeg")

LEGAL_INFO = "本许可证用于对授权人向被授权人所提供的'东方电机智能机组诊断决策系统（3DS）'产品所有组成部分中的一切算法、代码、" \
             "脚本与软件进行以下授权许可：\n" \
             "1.被授权人在本许可证所列出的发电厂/站、发电机组、计算机物理设备、计算机操作系统、计算机网络环境、代码基础运行环" \
             "境和授权时间内，对通过本许可证进行调用的算法、代码、脚本具有使用权；\n" \
             "2.上述授权条件中任一不符则许可失效，被授权人使用权失效；\n" \
             "3.使用本许可证进行调用、运行、操作的，包括经编译或未经编译的程序、代码、脚本等在内物项的一切权利归于授权人；\n" \
             "4.未经授权人书面同意，被授权人不得复制、修改、合并、出版发行、散布、再授权、贩售或以其它形式进行公开；\n" \
             "5.被授权人不得通过修改、翻译、反向工程、反向编译等其它手段获取该许可证所指对象的源代码；\n" \
             "6.未经授权人书面同意，被授权人不得以授权物项为基础制作、传播衍生作品。"
VALIDITY_DATE = datetime.date(2099, 12, 31)
VALIDITY_TIME = datetime.time(0, 0)

validationResult_projectName = "unknown"


def checkAndStore():
    try:
        __res = {}
        for i in range(1, 6):
            if len(st.session_state[f"key0{i}"]) * len(st.session_state[f"value0{i}"]) != 0:
                __cache = {st.session_state[f"key0{i}"]: st.session_state[f"value0{i}"]}
                __res = {**__res, **__cache}
        __requestJson = {
            "tags": __res,
            "projectName": st.session_state["projectName"],
            "functionModuleName": st.session_state["functionName"],
            "miniohost": st.session_state["ossHost"],
            "minioport": st.session_state["ossServicePort"],
            "miniouser": st.session_state["ossUsername"],
            "miniopwd": st.session_state["ossPassword"],
        }
        url = f"http://127.0.0.1:8300/confirmAndDownload/?tags={__res}&projectName={st.session_state['projectName']}" \
              f"&functionModuleName={st.session_state['functionName']}" \
              f"&miniohost={st.session_state['ossHost']}" \
              f"&minioport={st.session_state['ossServicePort']}" \
              f"&miniouser={st.session_state['ossUsername']}&" \
              f"&miniopwd={st.session_state['ossPassword']}"
        res = json.loads(requests.get(url).text)
        print(res)
        if res["status"] == "已上载":
            tagContainerForm.success("已上载")
        else:
            tagContainerForm.exception("出现问题，上载不成功")
    except:
        tagContainerForm.warning("不可重复上载！需再次上载需重新生成授权")


def validation_functionName():
    __symbols = "~!@#$%^&*()_+`-=[]{};':,./<>?|"
    __string2Check = list(st.session_state["functionName"])
    if len(__string2Check) == 0:
        return "unknown"
    return all([item not in __symbols for item in __string2Check])


def validation_projectName():
    __lowercase = "abcdefghijklmnopqrstuvwxyz"
    __uppercase = __lowercase.upper()
    __decNums = "1234567890"
    __symbols = "-"
    __legalChrs = list(__lowercase) + list(__lowercase) + list(__decNums) + list(__symbols)
    __string2Check = list(st.session_state["projectName"])
    if len(__string2Check) == 0:
        return "unknown"
    return all([item in __legalChrs for item in __string2Check])


def loadDefault():
    global LEGAL_INFO, VALIDITY_DATE, VALIDITY_TIME

    st.session_state["new_authInfo_announcement"] = LEGAL_INFO
    st.session_state["new_authInfo_validityDate"] = VALIDITY_DATE
    st.session_state["new_authInfo_validityTime"] = VALIDITY_TIME
    _res = requests.get(f"http://127.0.0.1:8300/info/?quest=basic_env_info")
    for item in ["new_authInfo_plant", "new_authInfo_unit"]:
        st.session_state[item] = json.loads(_res.text)[item.replace("new_authInfo_", "")]

def authorize():
    _keys = [
        "new_authInfo_author", "new_authInfo_plant", "new_authInfo_unit", "new_authInfo_announcement",
        "new_authInfo_validityDate", "new_authInfo_validityTime"
    ]
    request_json = {
        "plant": st.session_state["new_authInfo_plant"],
        "unit": st.session_state["new_authInfo_unit"],
        "author": st.session_state["new_authInfo_author"],
        "validityDate": f"{st.session_state['new_authInfo_validityDate']} {st.session_state['new_authInfo_validityTime']}",
        "announcement": st.session_state["new_authInfo_announcement"],
        "with_core_env_info": st.session_state["UseCoreEnvParam"]
    }
    res = requests.get(f"http://127.0.0.1:8300/generate/?{json.dumps(request_json)}")
    if json.loads(res.text)["status"] == "已生成":
        st.session_state["generateStatus"] = "已生成"



if __name__ == '__main__':
    # 配置页面
    st.set_page_config(
        page_title="3DS™️模型授权管理",
        page_icon=imagePath,
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://www.extremelycoolapp.com/help',
            'Report a bug': "https://www.extremelycoolapp.com/bug",
            'About': "# This is a header. This is an *extremely* cool app!"
        }
    )
    # 配置侧边栏
    st.sidebar.subheader("OSS存储服务")
    ossHost = st.sidebar.text_input("Host", "172.17.0.1", key="ossHost", placeholder="形如：172.17.0.1",
                                    help="OSS服务的Host地址")
    ossServicePort = st.sidebar.text_input("Port", "9000", key="ossServicePort", placeholder="形如：9000",
                                           help="OSS服务的Port号")
    ossConsolePort = st.sidebar.text_input("Port", "9001", key="ossConsolePort", placeholder="形如：9001",
                                           help="OSS终端的Port号")
    ossUsername = st.sidebar.text_input("User", "minioadmin", key="ossUsername", help="账号")
    ossPassword = st.sidebar.text_input("Password", "minioadmin", key="ossPassword", help="密码")
    st.sidebar.subheader("OSS前端")
    st.sidebar.write(f"[跳转](http://127.0.0.1:{ossConsolePort})")
    # 配置PageTitle
    titleContainer = st.container()
    titleContainer.header("智能诊断决策系统（3DS）模型算子授权")
    # 基础环境信息重置
    setEnvParamsContainer = st.container()
    setEnvParamsContainer.subheader("授权信息")
    formContainer = st.form(key="form_key01")
    authorCol, plantCol, unitCol, validateCol, validTimeCol = formContainer.columns(5)
    authorCol.text_input("授权人", key="new_authInfo_author", disabled=True, value="东方电气集团东方电机有限公司")
    plantCol.text_input("被授权人", key="new_authInfo_plant")
    unitCol.text_input("被授权机组", key="new_authInfo_unit")
    validateCol.date_input("失效日期", key="new_authInfo_validityDate")
    validTimeCol.time_input("失效时间", key="new_authInfo_validityTime")
    formContainer.text_area("法律声明", key="new_authInfo_announcement", height=200)
    # 生成授权操作
    btns = formContainer.container()
    col1, col2, col3, col4, _, _, _, _ = btns.columns(8)
    col1.form_submit_button("加载缺省值", on_click=loadDefault, type="secondary")
    col2.form_submit_button("生成授权", on_click=authorize, type="primary")
    col3.selectbox(label="使用核心环境变量", options=("使用核心环境变量", False, True), key="UseCoreEnvParam",
                   label_visibility="collapsed", index=1)
    col4.text_input(label="None", key="generateStatus", value="未生成", label_visibility="collapsed")
    # 存储授权文件
    # saveAuthor = st.form(key="form_key02")
    saveAuthorContainer = st.container()
    col11, col12, col13 = saveAuthorContainer.columns(3)

    col11.text_input("项目名称", key="projectName", help="须为小写英文字母", placeholder="须为小写英文字母", on_change=validation_projectName)
    col12.text_input("授权功能", key="functionName", help="无符号中英文大小写", placeholder="无符号中英文大小写", on_change=validation_functionName)

    if validation_projectName() == "unknown":
        col11.info(":question:输入项目名称")
    elif validation_projectName() is True:
        col11.success("👌输入合法")
    else:
        col11.error(":x:输入非法")

    if validation_functionName() == "unknown":
        col12.info(":question:输入授权功能名称")
    elif validation_functionName() is True:
        col12.success("👌输入合法")
    else:
        col12.error(":x:输入非法")

    tagContainer = col13.container()
    tagContainerForm = tagContainer.form(key="tagContainer")
    tagContainerFormCol01, tagContainerFormCol02, tagContainerFormCol03 = tagContainerForm.columns(3)
    tagContainerFormCol01.text_input("标签名", key="key01", placeholder="仅英文")
    tagContainerFormCol01.text_input(" ", key="key02", label_visibility="collapsed", placeholder="仅英文")
    tagContainerFormCol01.text_input(" ", key="key03", label_visibility="collapsed", placeholder="仅英文")
    tagContainerFormCol01.text_input(" ", key="key04", label_visibility="collapsed", placeholder="仅英文")
    tagContainerFormCol01.text_input(" ", key="key05", label_visibility="collapsed", placeholder="仅英文")
    tagContainerFormCol02.text_input("标签值", key="value01", placeholder="仅英文")
    tagContainerFormCol02.text_input(" ", key="value02", label_visibility="collapsed", placeholder="仅英文")
    tagContainerFormCol02.text_input(" ", key="value03", label_visibility="collapsed", placeholder="仅英文")
    tagContainerFormCol02.text_input(" ", key="value04", label_visibility="collapsed", placeholder="仅英文")
    tagContainerFormCol02.text_input(" ", key="value05", label_visibility="collapsed", placeholder="仅英文")
    tagContainerFormCol03.text_input("提示", key="hint01", disabled=True, value="授权的版本号")
    tagContainerFormCol03.text_input(" ", key="hint02", label_visibility="collapsed", disabled=True, value="测试或正式部署")
    tagContainerFormCol03.text_input(" ", key="hint03", label_visibility="collapsed", disabled=True, value="其它必要信息")
    tagContainerFormCol03.text_input(" ", key="hint04", label_visibility="collapsed", disabled=True, value="授权日期")
    tagContainerFormCol03.text_input(" ", key="hint05", label_visibility="collapsed", disabled=True, value="授权用户")
    tagContainerForm.form_submit_button("储存至OSS服务", on_click=checkAndStore)
