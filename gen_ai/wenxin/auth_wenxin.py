import requests

from gen_ai.config import secrets, update_wenxin_token


def get_token_from_env():
    return secrets["wenxinAccessToken"] if "wenxinAccessToken" in secrets else None


def get_token_from_auth():
    api_key = secrets["wenxinApiKey"] if "wenxinApiKey" in secrets else None
    api_secret = secrets["wenxinApiSecret"] if "wenxinApiSecret" in secrets else None
    if api_key and api_secret:
        try:
            response = requests.post(
                f'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={api_key}&client_secret={api_secret}',
            )
            result = response.json()
            access_token = result["access_token"] if "access_token" in result else None
            if access_token is not None:
                secrets["wenxinAccessToken"] = access_token
                update_wenxin_token(access_token)
                return access_token
            else:
                raise Exception(
                    f'{result["error"]}: {result["error_description"]}' if "error" in result
                    else f'Error occurred: {result}')
        except Exception as err:
            raise Exception(f'Error occurred: {err}')
    else:
        raise Exception(f'API key or secret not exist.')
