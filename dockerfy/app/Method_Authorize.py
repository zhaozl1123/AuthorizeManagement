import base64
import struct, os, re


class Node:
    def __init__(self, name: str, value: float):
        self.name = name
        self.value = value
        self.leftLeaf = None
        self.rightLeaf = None
        self.code = None


class HuffmanTree:
    def __init__(self, nameValueList: list):
        self._nodeQuant = len(nameValueList)
        self._allNodes = [Node(item[0], item[1]) for item in nameValueList]
        self._allNodes.sort(key=lambda item: item.value, reverse=True)
        self.codeDict = {}

        while len(self._allNodes) >= 2:
            __leftNode = self._allNodes.pop(-1)
            __rightNode = self._allNodes.pop(-1)
            __newNode = Node(__leftNode.name + __rightNode.name, __leftNode.value + __rightNode.value)
            __newNode.leftLeaf = __leftNode
            __newNode.rightLeaf = __rightNode
            self._allNodes.append(__newNode)
            self._allNodes.sort(key=lambda item: item.value, reverse=True)
        self.root = self._allNodes[0]
        self.__setLeafNodeCode(self.root, "0")
        self.codeDict = self.__getCodeDict(nameValueList)

    def __setLeafNodeCode(self, leafNode, fatherNodeCode: str):
        leafNode.code = fatherNodeCode
        try:
            self.__setLeafNodeCode(leafNode.leftLeaf, fatherNodeCode+"0")
        except:
            pass
        try:
            self.__setLeafNodeCode(leafNode.rightLeaf, fatherNodeCode+"1")
        except:
            pass

    def getCodeByName(self, name):
        return self.__getCodeByName(self.root, name)

    def __getCodeByName(self, node, name):
        _res = None, None
        if node.leftLeaf.name == name:
            _res = node.leftLeaf.name, node.leftLeaf.code
        elif node.rightLeaf.name == name:
            _res = node.rightLeaf.name, node.rightLeaf.code
        else:
            try:
                _res = self.__getCodeByName(node.leftLeaf, name)
            except:
                _res = self.__getCodeByName(node.rightLeaf, name)
        return _res

    def __getCodeDict(self, nameValueList):
        _res = {}
        for item in [item[0] for item in nameValueList]:
            _res = {**_res, **{item: self.getCodeByName(item)[1]}}
        return _res


class HuffmanTree_nameValueList(HuffmanTree):
    def __init__(self, nameValueList: list):
        super().__init__(nameValueList)


class HuffmanTree_longString(HuffmanTree):
    def __init__(self, longString: str):
        longList = list(longString)
        self.chrDict = {}
        self.__static(longList)
        self.occurStatics = [(item, self.chrDict[item]) for item in self.chrDict.keys()]
        super().__init__(self.occurStatics)

    def __static(self, longList: list):
        _targetChr = longList.pop(-1)
        if _targetChr in self.chrDict.keys():
            self.chrDict[_targetChr] = self.chrDict[_targetChr] + 1
        else:
            self.chrDict = {**self.chrDict, **{_targetChr: 1}}
        try:
            self.__static(longList)
        except:
            pass


def translateBinList2IntList(func):
    def outerWrapper(*args):
        _zeroes = [str(item).find("1") if "1" in str(item) else len(str(item)) for item in args[0]]
        return func([int(item, 2) for item in args[0]], _zeroes)
    return outerWrapper


def readPrivateKeyFileAndDecode2IntList(func):
    def outerWrapper(*args, **kwargs):
        _filePath = args[0] if isinstance(args[0], str) else args[1]  # 需要关注一下，为什么编译成so之前和之后，会影响参数
        _privateKeyStr = []
        with open(_filePath, "rb") as file:
            while 1:
                try:
                    _privateKeyStr.append(struct.unpack(">B", file.read(1))[0])
                except:
                    file.close()
                    break
        _res = (_privateKeyStr[0: (len(_privateKeyStr)//2)], _privateKeyStr[(len(_privateKeyStr)//2): None])
        return func(*_res)
    return outerWrapper


def zerosSupplementQuantList(func):
    """
    根据需要在字符串前补零的数量，对list中字符串元素进行补零
    """
    def outerWrapper(*args, **kwargs):
        _binList = [bin(item).replace("0b", "") for item in args[0]]
        _addedBinList = ["0"*item + _binList[i] for i, item in enumerate(args[1])]
        return func(_addedBinList)
    return outerWrapper


class ProductAuthorization:
    """
    用于对3DS产品的授权文件生成

    Example
    ----------
    >>> productAuth = ProductAuthorization()
    >>> productAuth.setBasicAuthInfo({
    >>>     "plant": "葛洲坝",
    >>>     "unit": "1#机",
    >>>     'authorizedBy': '那谁谁',
    >>>     "validityDate": "2023-12-31 00:00:00.000",
    >>>     "serialNumber_decrypted": "167890-=0987655tfgbhnjki8765rdfcvbhj",
    >>>     "environment": {
    >>>         "macAddress": "GF:EE:AA:FF:EE"
    >>>     }
    >>> })
    >>> print(productAuth.basicAuthInfo)
    >>> productAuth.generateAuthorizationFile()
    >>> print(f"publicKey {len(productAuth.publicKey)}: ", productAuth.publicKey)
    >>> print(f"privateKey {len(productAuth.privateKey)}: ", productAuth.privateKey)
    """
    def __init__(self):
        self.basicAuthInfo = None
        self.publicKey = None
        self.privateKey = None

    def setBasicAuthInfo(self, basicAuthDict: dict, lengthLimit=800, withCoreEnvParams=True):
        """
        设置基本授权信息，形如：\n
        {
            "plant": "葛洲坝",\n
            "unit": "1#机",\n
            "validityDate": "2023-12-31 00:00:00.000", \n
            "serialNumber_decrypted": "ABcd123-=?", \n
            "environment": { \n
            "macAddress": "GF:EE:AA:FF:EE" \n
            }\n
        }

        :arg basicAuthDict: dict,基本的授权信息
        :arg lengthLimit: int,基本授权信息的字符数量限制，默认1000
        :arg withCoreEnvParams: bool,是否使用硬件信息进行授权，默认True
        """
        _coreAuthInfo = getEnvParams()
        if withCoreEnvParams:
            _combinedAuthInfo = {**basicAuthDict, **_coreAuthInfo}
        else:
            _combinedAuthInfo = basicAuthDict
        _basicAuthStr = str(_combinedAuthInfo)
        _strLength = len(_basicAuthStr)
        if _strLength > lengthLimit:
            raise Warning(f"过长的授权信息(字符数 {_strLength} > {lengthLimit}): {basicAuthDict}")
        self.basicAuthInfo = _basicAuthStr

    def generateAuthorizationFile(self, output=True, outputPath="./"):
        """
        生成授权文件（公钥:publicKey.txt/私钥privateKey.txt）

        :arg output: bool,是否输出授权文件,默认:True
        :arg outputPath: str,授权文件（公钥/私钥）保存路径,默认:"./"
        """
        """将含有中英文的字典型变量转化为不会影响增加Huffman深度的编码"""
        basicAuthInfoTransferred = translate(self.basicAuthInfo)
        _tree = HuffmanTree_longString(basicAuthInfoTransferred)
        self.publicKey = base64.b64encode(bytes(str(_tree.codeDict), encoding="utf-8"))
        self.privateKey = self.convertInt2HexBytes([_tree.codeDict[item] for item in str(basicAuthInfoTransferred)])
        if output:
            with open(outputPath + "privateKey.txt", "wb") as f:
                for item in self.privateKey:
                    f.write(struct.pack("B", item))
            with open(outputPath + "publicKey.txt", "wb") as f:
                f.write(self.publicKey)
            with open(outputPath + "authInfo.txt", "w") as f:
                f.write(self.basicAuthInfo)

    @staticmethod
    @translateBinList2IntList
    def convertInt2HexBytes(_ele, _zeroes):
        return _ele + _zeroes


def translate(inputDict: dict) -> str:
    inputStr = str(inputDict)
    hexStr = [hex(ord(item)).replace("0x", "") for item in inputStr]
    complementedHexStr = [item if len(item)==4 else "0"*(4-len(item)) + item for item in hexStr]
    return "".join(complementedHexStr)



def getEnvParams():
    """
    获取深层硬件环境变量： \n
    ①System Firmware Version \n
    ②Serial Number System \n
    ③Hardware UUID \n
    ④Provisioning UDID \n

    :return: dict
    """
    _cmd = "/usr/sbin/system_profiler SPHardwareDataType"
    _info = os.popen(_cmd).read()
    _keys = ["System Firmware Version", "Serial Number \(system\)", "Hardware UUID", "Provisioning UDID"]
    _values = []
    for item in _keys:
        _re = re.compile(rf"{item}: (.*)")
        _res = _re.findall(_info)
        _values.append(_res[0])
    return dict(zip([item.replace(" ", "").replace("\\", "").replace("(system)", "") for item in _keys], _values))


class AuthorizationVerify:
    """
    用于对授权信息进行认证

    Exmaple
    ----------
    >>> verify = AuthorizationVerify()
    >>> verify.defineAuthorizeTargetInfo({
    >>>     'plant': '葛洲坝',
    >>>     'unit': '1#机',
    >>>     'authorizedBy': '那谁谁',
    >>>     'validityDate': '2023-12-31 00:00:00.000',
    >>>     'serialNumber_decrypted': '167890-=0987655tfgbhnjki8765rdfcvbhj',
    >>>     'environment': {
    >>>         'macAddress': 'GF:EE:AA:FF:EE'
    >>>     }
    >>> })
    >>> publicKey = "eyd9JzogJzAwMDAwMDAnLCAiJyI6ICcwMTAwJywgJ0UnOiAnMDExMDAxMScsICc6JzogJzAxMDEwJywgJ0YnOiAnMDAwMTEwMScsICdBJzogJzAwMDExMDAnLCAnRyc6ICcwMTExMDAxMDEnLCAnICc6ICcwMDExMScsICdzJzogJzAwMDExMTEnLCAnZSc6ICcwMTExMTEnLCAncic6ICcwMTEwMDAnLCAnZCc6ICcwMTAxMTEnLCAnYyc6ICcwMDAxMTEwJywgJ2EnOiAnMDAwMDExJywgJ20nOiAnMDAwMTAwMScsICd7JzogJzAxMTAxMTAxJywgJ3QnOiAnMDExMTEwJywgJ24nOiAnMDAwMDEwJywgJ28nOiAnMDExMDExMDAnLCAnaSc6ICcwMTAxMTAnLCAndic6ICcwMDAxMDAwJywgJywnOiAnMDAwMDAxJywgJ2onOiAnMDExMDExMTEnLCAnaCc6ICcwMDAxMDExJywgJ2InOiAnMDAwMTAxMCcsICdmJzogJzAxMTAxMTEwJywgJzUnOiAnMDAxMDEwMScsICc2JzogJzAwMTAxMDAnLCAnNyc6ICcwMDEwMTExJywgJzgnOiAnMDAxMDExMCcsICdrJzogJzAxMTEwMDEwMCcsICdnJzogJzAxMTEwMDExMScsICc5JzogJzAxMTAxMDAxJywgJzAnOiAnMDAxMTAnLCAnPSc6ICcwMTExMDAxMTAnLCAnLSc6ICcwMDEwMDAxJywgJzEnOiAnMDExMDAxMCcsICdwJzogJzAxMTAxMDAwJywgJ3knOiAnMDAxMDAwMCcsICdfJzogJzAxMTEwMDAwMScsICd1JzogJzAwMTAwMTEnLCAnTic6ICcwMTExMDAwMDAnLCAnbCc6ICcwMDEwMDEwJywgJy4nOiAnMDExMTAwMDExJywgJzMnOiAnMDExMDEwMTEnLCAnMic6ICcwMDAwMDAxJywgJ0QnOiAnMDExMTAwMDEwJywgJ+iwgSc6ICcwMTEwMTAxMCcsICfpgqMnOiAnMDExMTAxMTAxJywgJ0InOiAnMDExMTAxMTAwJywgJ3onOiAnMDExMTAxMTExJywgJ+acuic6ICcwMTExMDExMTAnLCAnIyc6ICcwMTExMDEwMDEnLCAn5Z2dJzogJzAxMTEwMTAwMCcsICfmtLInOiAnMDExMTAxMDExJywgJ+iRmyc6ICcwMTExMDEwMTAnfQ=="
    >>> verify.defineAuthorizationInfo(privateKeyFilePath="./privateKey.txt", publicKey=publicKey)
    >>> print(verify.verify())
    """
    def __init__(self):
        self.authorizeTargetKnownInfo = None
        self.__privateKeyFilePath = None
        self.__publicKey = None
        self.__decodedPublicKey = None
        self.__decodedPrivateKey = None
        self.decodedAuthInfo = None

    def defineAuthorizeTargetInfo(self, targetInfo: dict):
        """
        定义所授权对象的基本信息 `targetInfo`

        :param targetInfo: dict, 形如：{
            'plant': '葛洲坝智能诊断决策系统',
            'unit': '1#机',
            'authorizedBy': '那谁谁',
            'validityDate': '2023-12-31 00:00:00.000',
            'serialNumber_decrypted': '167890-=0987655tfgbhnjki8765rdfcvbhj',
            'environment': {
                'macAddress': 'GF:EE:AA:FF:EE'
            }
        }
        """
        if isinstance(targetInfo, dict) and (len(targetInfo.keys()) != 0):
            self.authorizeTargetKnownInfo = targetInfo
        else:
            raise ValueError(f"错误的入参 targetInfo: {targetInfo}")

    def defineAuthorizationInfo(self, privateKeyFilePath: str, publicKey: str):
        """
        定义授权文件（私钥）所在地址和公钥字符串

        :param privateKeyFilePath: str,形如："./privateKey.txt"
        :param publicKey: str, 形如："eyd9JzogJzAxMTExMTAwJywgIic"
        """
        self.__publicKey = publicKey
        self.__decodedPublicKey = self.__decodePublicKeyStr(self.__publicKey)

        self.__privateKeyFilePath = privateKeyFilePath
        self.__decodedPrivateKey = self.__decodePrivateKeyStr(self.__privateKeyFilePath)
        _cache = [self.__decodedPublicKey[item] if "1" in item else self.__decodedPublicKey[item[0:-1]] for item in self.__decodedPrivateKey]
        _cache = "".join(_cache)
        _cache = [chr(int(_cache[(i*4):((i+1)*4)], 16)) for i in range(len(_cache)//4)]
        self.decodedAuthInfo = eval("".join(_cache))

    def verify(self, withCoreEnvParams):
        """
        进行授权认证

        :return: bool,授权认证结果
        """
        if withCoreEnvParams:
            _combinedParams = {**self.authorizeTargetKnownInfo, **getEnvParams()}
        else:
            _combinedParams = self.authorizeTargetKnownInfo
        return True if self.decodedAuthInfo == _combinedParams else False

    @staticmethod
    def __decodePublicKeyStr(_codedStr):
        _cache = eval(base64.b64decode(_codedStr).decode("utf-8"))
        return dict(zip(_cache.values(), _cache.keys()))

    @readPrivateKeyFileAndDecode2IntList
    @zerosSupplementQuantList
    def __decodePrivateKeyStr(_decodedPrivateKey):
        return _decodedPrivateKey


def AuthorizationValidate(authInfo: dict, privateKeyPath: str, publicKey: str, withCoreEnv: bool):
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
    def outerWrapper(func):
        def innerWrapper(*args, **kwargs):
            try:
                __verify = AuthorizationVerify()
                __verify.defineAuthorizeTargetInfo(authInfo)
                __verify.defineAuthorizationInfo(privateKeyFilePath=privateKeyPath, publicKey=publicKey)
                if __verify.verify(withCoreEnv):
                    return func(*args, **kwargs)
                else:
                    raise Warning("授权无效")
            except:
                raise Warning("授权无效")
        return innerWrapper
    return outerWrapper


if __name__ == '__main__':
    """
    授权
    """
    productAuth = ProductAuthorization()
    productAuth.setBasicAuthInfo({
        "plant": "葛洲坝",
        "unit": "1#机",
        'authorizedBy': '那谁谁',
        "validityDate": "2023-12-31 00:00:00.000",
        "serialNumber_decrypted": "167890-=0987655tfgbhnjki8765rdfcvbhj",
        "environment": {
            "macAddress": "GF:EE:AA:FF:EE"
        }
    })
    print(productAuth.basicAuthInfo)
    productAuth.generateAuthorizationFile()
    print(f"publicKey {len(productAuth.publicKey)}: ", productAuth.publicKey)
    print(f"privateKey {len(productAuth.privateKey)}: ", productAuth.privateKey)
    exit()
    """
    验证
    """
    verify = AuthorizationVerify()
    verify.defineAuthorizeTargetInfo({
        'plant': '葛洲坝',
        'unit': '1#机',
        'authorizedBy': '那谁谁',
        'validityDate': '2023-12-31 00:00:00.000',
        'serialNumber_decrypted': '167890-=0987655tfgbhnjki8765rdfcvbhj',
        'environment': {
            'macAddress': 'GF:EE:AA:FF:EE'
        }
    })
    publicKey = "eyd9JzogJzAwMDAwMDAnLCAiJyI6ICcwMTAwJywgJ0UnOiAnMDExMDAxMScsICc6JzogJzAxMDEwJywgJ0YnOiAnMDAwMTEwMScsICdBJzogJzAwMDExMDAnLCAnRyc6ICcwMTExMDAxMDEnLCAnICc6ICcwMDExMScsICdzJzogJzAwMDExMTEnLCAnZSc6ICcwMTExMTEnLCAncic6ICcwMTEwMDAnLCAnZCc6ICcwMTAxMTEnLCAnYyc6ICcwMDAxMTEwJywgJ2EnOiAnMDAwMDExJywgJ20nOiAnMDAwMTAwMScsICd7JzogJzAxMTAxMTAxJywgJ3QnOiAnMDExMTEwJywgJ24nOiAnMDAwMDEwJywgJ28nOiAnMDExMDExMDAnLCAnaSc6ICcwMTAxMTAnLCAndic6ICcwMDAxMDAwJywgJywnOiAnMDAwMDAxJywgJ2onOiAnMDExMDExMTEnLCAnaCc6ICcwMDAxMDExJywgJ2InOiAnMDAwMTAxMCcsICdmJzogJzAxMTAxMTEwJywgJzUnOiAnMDAxMDEwMScsICc2JzogJzAwMTAxMDAnLCAnNyc6ICcwMDEwMTExJywgJzgnOiAnMDAxMDExMCcsICdrJzogJzAxMTEwMDEwMCcsICdnJzogJzAxMTEwMDExMScsICc5JzogJzAxMTAxMDAxJywgJzAnOiAnMDAxMTAnLCAnPSc6ICcwMTExMDAxMTAnLCAnLSc6ICcwMDEwMDAxJywgJzEnOiAnMDExMDAxMCcsICdwJzogJzAxMTAxMDAwJywgJ3knOiAnMDAxMDAwMCcsICdfJzogJzAxMTEwMDAwMScsICd1JzogJzAwMTAwMTEnLCAnTic6ICcwMTExMDAwMDAnLCAnbCc6ICcwMDEwMDEwJywgJy4nOiAnMDExMTAwMDExJywgJzMnOiAnMDExMDEwMTEnLCAnMic6ICcwMDAwMDAxJywgJ0QnOiAnMDExMTAwMDEwJywgJ+iwgSc6ICcwMTEwMTAxMCcsICfpgqMnOiAnMDExMTAxMTAxJywgJ0InOiAnMDExMTAxMTAwJywgJ3onOiAnMDExMTAxMTExJywgJ+acuic6ICcwMTExMDExMTAnLCAnIyc6ICcwMTExMDEwMDEnLCAn5Z2dJzogJzAxMTEwMTAwMCcsICfmtLInOiAnMDExMTAxMDExJywgJ+iRmyc6ICcwMTExMDEwMTAnfQ=="
    verify.defineAuthorizationInfo(privateKeyFilePath="./privateKey.txt", publicKey=publicKey)
    print(verify.verify())

