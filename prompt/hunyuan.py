import json
import requests
import time
import hmac
import base64
import hashlib
import uuid
import copy

url = "http://hunyuan.tencentcloudapi.com"

_SIGN_HOST = "hunyuan.cloud.tencent.com"
_SIGN_PATH = "hyllm/v1/chat/completions"
_URL = "https://hunyuan.cloud.tencent.com/hyllm/v1/chat/completions"


def gen_param(appid, messages, secretid):
    timestamp = int(time.time()) + 10000
    request = {
        "app_id": int(appid),
        "secret_id": secretid,
        "query_id": "test_query_id_" + str(uuid.uuid4()),
        "messages": messages,
        "temperature": 0,
        "top_p": 0.8,
        "stream": 0,
        "timestamp": timestamp,
        "expired": timestamp + 24 * 60 * 60
    }
    return request


def gen_signature(secretkey, param):
    sort_dict = sorted(param.keys())
    sign_str = _SIGN_HOST + "/" + _SIGN_PATH + "?"
    for key in sort_dict:
        sign_str = sign_str + key + "=" + str(param[key]) + '&'
    sign_str = sign_str[:-1]
    # print(sign_str)
    hmacstr = hmac.new(secretkey.encode('utf-8'),
                       sign_str.encode('utf-8'), hashlib.sha1).digest()
    signature = base64.b64encode(hmacstr)
    signature = signature.decode('utf-8')
    return signature


def gen_sign_params(data):
    params = dict()
    params['app_id'] = data["app_id"]
    params['secret_id'] = data['secret_id']
    params['query_id'] = data['query_id']
    # float类型签名使用%g方式，浮点数字(根据值的大小采用%e或%f)
    params['temperature'] = '%g' % data['temperature']
    params['top_p'] = '%g' % data['top_p']
    params['stream'] = data["stream"]
    # 数组按照json结构拼接字符串
    message_str = ','.join(
        ['{{"role":"{}","content":"{}"}}'.format(message["role"], message["content"]) for message in data["messages"]])
    message_str = '[{}]'.format(message_str)
    # print(message_str)
    params['messages'] = message_str
    params['timestamp'] = str(data["timestamp"])
    params['expired'] = str(data["expired"])
    return params


def HunYuan_request(appid, secretid, secretkey, messages, engine, gpt_param, log_dir):
    if isinstance(messages, str):
        messages = [{"role": "user", "content": messages}]


    request = gen_param(appid, messages, secretid)
    signature = gen_signature(secretkey, gen_sign_params(request))
    headers = {
        "X-TC-Actio": engine,
        "Content-Type": "application/json",
        "Authorization": str(signature)
    }

    url = _URL
    resp = requests.post(url, headers=headers, json=request, stream=True)
    response_json = resp.json()
    response_json["choices"][0]['message'] = response_json["choices"][0]['messages']
    response_json["choices"][0].pop('messages')
    write_json = {key: item for key, item in copy.deepcopy(response_json).items()}
    write_json["choices"][0]['message'] = [messages, write_json["choices"][0]['message']]
    fw = open(log_dir, 'a', encoding='utf-8')
    fw.write(json.dumps(write_json, ensure_ascii=False) + '\n')
    fw.close()
    return response_json


# messages = {
#     "TopP": 0,
#     "Temperature": 4.8,

# }
if __name__ == '__main__':
    from utils import tencent_appid, tencent_secretid, tencent_secretkey
    messages = [
        {
            "role": "user",
            "content": "What Is Entropy and How to Calculate It？"
        }
    ]

    print(HunYuan_request(tencent_appid, tencent_secretid, tencent_secretkey, messages, 'ChatPro', {}, '1.txt'))
