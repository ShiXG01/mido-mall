from authlib.jose import jwt, JoseError
from django.conf import settings


def check_access_token(access_token_openid):
    """反解access_token_openid"""
    key = settings.SECRET_KEY

    try:
        data = jwt.decode(access_token_openid, key)
    except JoseError:
        return None
    else:
        return data.get('openid')


def generate_access_token(openid):
    """签名openid"""
    # 签名算法
    header = {'alg': 'HS256'}
    # 用于签名的密钥
    key = settings.SECRET_KEY
    # 待签名的数据负载
    data = {'openid': openid}
    token = jwt.encode(header=header, payload=data, key=key)

    return token.decode()
