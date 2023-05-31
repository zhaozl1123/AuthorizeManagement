from Method_Authorize import AuthorizationValidate

AUTH_INFO = {
    'plant': '葛洲坝电厂', 'unit': '1、2机', 'author': '东方电气集团东方电机有限公司',
    'validityDate': '2023-12-31 00:00:00.000', 'announcement': '【法律声明】'
}
privateKeyPath = "./privateKey.txt"
publicKey = "eydkJzogJzAxMDAwMTEnLCAnNyc6ICcwMTExMCcsICcwJzogJzAwJywgJzInOiAnMDExMTEnLCAnMSc6ICcwMTAxMDEnLCAnMyc6ICcwMTEwMCcsICdlJzogJzAxMDExMTEnLCAnNic6ICcwMTEwMScsICdmJzogJzAxMDExMTAxJywgJzgnOiAnMDEwMDAxMCcsICc1JzogJzAxMDAxJywgJ2InOiAnMDEwMTExMDAnLCAnYyc6ICcwMTAwMDAnLCAnYSc6ICcwMTAxMTAxJywgJzQnOiAnMDEwMTAwJywgJzknOiAnMDEwMTEwMCd9"


@AuthorizationValidate(authInfo=AUTH_INFO, privateKeyPath=privateKeyPath, publicKey=publicKey, withCoreEnv=False)
def some_function(param01, param02, someKV1=15, someKV2=50, **kwargs) -> int:
    """
    Notes:
        This is a function description.

    Args:
        param01: int, some desc
        param02: int, some desc

    Keyword Args:
        keyName1: value1

    References:
        Something is used to be supplemental.

    See Also:
        FYI descriptions.

    Returns:
        Description of returns.

    Raises:
        01: which situation would trigger what raise.
        02: which situation would trigger what raise.

    Examples:
        >>> print()
        >>> print()
    """
    print(f"SomeFunction: param01={param01}, param02={param02},  someKV1={someKV1}, someKV2={someKV2}")
    return sum([param01, param02, someKV1, someKV2])


if __name__ == '__main__':
    print(some_function(15, 20, someKV1=5, someKV2=5))
