import pandas as pd 
import requests as req 
from bs4 import BeautifulSoup as bs
import pandas as pd
import time
from tqdm import tqdm
from threading import Thread
from random import randrange
from queue import Queue
import json


users_df = pd.read_csv("userdetails.csv")
users_email_list = users_df['Email'].tolist()
error_count = 0
queue_var = Queue()
thread_list = []

config = ''
with open("config.json","r") as fb:
    config = json.load(fb)
    # func_exec_call()
# print("Error Count",error_count)
# print("finished=>",time.ctime())



def func_exec_call(queue_var,email,client_id,password,client_secret,token_url,userinfo_url):
    try:
        headers = {"Content-Type":"application/x-www-form-urlencoded",'User-Agent': 'Mozilla/5.0'}
        # logout_url = "http://localhost:8888/realms/test/protocol/openid-connect/logout?redirect_uri=http://localhost:9100/"
        # logout_url = "http://localhost:8180/auth/realms/lsac/protocol/openid-connect/logout?client-id=lsac-platform-home&redirect_uri=http://localhost:9100/"
        data = {
        "client_id": client_id,
        "grant_type":"password",
        "service":client_id,
        "username":email,
        "password":password,
        "client_secret":client_secret,
        "scope":"openid"
        }
        if config['LOCAL_KC']:
            data['account']=config["LOCAL_KC_ACCOUNT_NAME"]
        # time.sleep(2)
        token_response = req.post(token_url,headers=headers,data=data)
        if(token_response.status_code!=200):
            # error_count+=1
            queue_var.put(1)
        print(email," token ==> ",token_response.status_code,token_response.json() )
        token = token_response.json()['access_token']
        refresh_token = token_response.json()['refresh_token']
        # print(token_response.json()['access_token'])
        userinfo_headers = {"Authorization":"Bearer "+token}
        time.sleep(randrange(10))
        userinfo_response = req.get(userinfo_url,headers=userinfo_headers)
        if(userinfo_response.status_code!=200):
            # error_count+=1 
            queue_var.put(1)
        print(email," userinfo ==> ",userinfo_response.status_code,userinfo_response.json())
        # logout_response = req.get(logout_url+"&refresh_token="+refresh_token,headers=userinfo_headers,allow_redirects=False)
        # logout_response = req.get(logout_url,headers=userinfo_headers,allow_redirects=False)
        # print("logoout",logout_response.status_code,logout_response.headers,bs(logout_response.content,"html.parser"))
        # logout_cookie = logout_response.headers['Set-Cookie']
        # confirm_headers = {"cookie":logout_cookie}
        # confirm_logout = bs(logout_response.content,"html.parser")
        # confirm_url = "http://localhost:8888"+confirm_logout.find("form")["action"]
        # session_code = confirm_logout.find('input', {'name':'session_code'})['value']
        # data_confirm = {"confirmLogout":"logout","session_code":session_code}
        # confirm_reponse = req.post(confirm_url,headers=confirm_headers,data=data_confirm)
        # print(confirm_reponse.status_code,confirm_reponse.headers,bs(confirm_reponse.content,"html.parser"))
        # time.sleep(randrange(10))
    except Exception as e:
        print("error processing ",e)
        # error_count+=1
        queue_var.put(1)
        time.sleep(3)


print("started",time.ctime())
user_count = config['USER_COUNT']
if config['LOCAL_KC'] or config['VANILLA_KC'] :
    password = config['COMMON_USER_PASSWORD']
    token_url=""
    userinfo_url=""
    client_id=""
    client_secret=""
    if config['LOCAL_KC']:
        token_url = config['LOCAL_KC_BASE_URL']+"/auth/realms/"+config['LOCAL_KC_REALM_ID']+"/protocol/openid-connect/token"
        userinfo_url = config['LOCAL_KC_BASE_URL']+"/auth/realms/"+config['LOCAL_KC_REALM_ID']+"/protocol/openid-connect/userinfo"
        client_id = config['LOCAL_KC_CLIENT_ID']
        client_secret = config['LOCAL_KC_CLIENT_SECRET']

    else:
        token_url = config['VANILLA_KC_BASE_URL']+"/realms/"+config['VANILLA_KC_REALM_ID']+"/protocol/openid-connect/token"
        userinfo_url = config['VANILLA_KC_BASE_URL']+"/realms/"+config['VANILLA_KC_REALM_ID']+"/protocol/openid-connect/userinfo"
        client_id = config['VANILLA_CLIENT_ID']
        client_secret = config['VANILLA_KC_CLIENT_SECRET']
    for i in tqdm(range(0,user_count)):
        print(users_email_list[i])
        thread_var = Thread(target=func_exec_call,args=(queue_var,users_email_list[i],client_id,password,client_secret,token_url,userinfo_url))
        # thread_var.start()
        thread_list.append(thread_var)
        print(thread_list)
    for i in range(0,len(thread_list)):
        thread_list[i].start()
        # thread_list[i].join()
    print(list(queue_var.queue))
    # print(sum(queue_var))
    print("finished=>",time.ctime())



def browser_auth_local_kc(email,client_id,password,client_secret,token_url,userinfo_url):
    try:
        respon = req.get(config['LOCAL_KC_HOME_GATEWAY_BASE_URL'])
        sso_cookies = respon.cookies.get_dict()
        # print(sso_cookies)
        # print(respon.headers)
        bs1 = bs(respon.content,'html.parser')
        # print(bs1.prettify())
        cookie_str = ''
        for k,v in sso_cookies.items():
            cookie_str+=k+'='+v+';'
        # print(bs1.prettify())
        headers = {'cookie':cookie_str,'User-Agent': 'Mozilla/5.0','Content-Type': 'application/x-www-form-urlencoded'}
        auth_use_pass_link = bs1.find("form")["action"]
        # print(cookie_str)
        # print(bs1.find("form")["action"])
        # print(respon.content)
        # print(headers)
        # req.post(auth_use_pass_link)
        auth_response = req.post(auth_use_pass_link,headers=headers,data={"username":email,"password":password},allow_redirects=False)
        bs2 = bs(auth_response.content,"html.parser")
        pass_url = bs2.find("form")["action"]
        auth_response_pass = req.post(pass_url,headers=headers,data={"username":email,"password":password},allow_redirects=False)
        # auth_response = req.post(auth_use_pass_link,headers=headers,data={"username":"admin","password":"admin"})
        # print(auth_response.headers)
        # print(auth_response_pass.headers)
        # print(auth_response.status_code)
        # authenticated_cookies = auth_response.headers['Set-Cookie']
        state_str = auth_response_pass.headers["Location"].split("?")[1].split("&")[0]
        state=''
        # print(state_str)
        if "state=" in state_str:
            state=state_str.replace("state=","")
        # print(state)
        token_headers = {'cookie':auth_response_pass.headers['Set-Cookie'],'User-Agent': 'Mozilla/5.0','Content-Type': 'application/x-www-form-urlencoded'
        }
        # auth_url = "http://localhost:8888/realms/test/protocol/openid-connect/auth"
        # auth_code_data = {
        #     "scope":"openid",
        #     "response_type":"code",
        #     "redirect_uri":"http://localhost:9100/",
        #     "state":state,
        #     # "nonce":"35a5242e-3199-4144-88e9-6ce2dcaa0a3d",
        #     "client_id":"lsac-platform-home",
        #     # "response_mode":"fragment"
        # }
        code_str = [ i for i in auth_response_pass.headers["Location"].split("?")[1].split("&") if 'code=' in i]
        code=''
        # print(code_str)
        if len(code_str)>0:
            code=code_str[0].replace("code=","")
        # print(code)
        token_data = {
            "code":code,
            "scope":"openid",
            "grant_type":"authorization_code",
            "redirect_uri":config['LOCAL_KC_HOME_GATEWAY_BASE_URL']+"login/oauth2/code/lsac",
            "client_id":client_id,
            "client_secret":client_secret
            }
        # token_url = "http://localhost:8888/realms/test/protocol/openid-connect/token"
        token_response = req.post(token_url,data=token_data,headers=token_headers,allow_redirects=False)
        # print("token_response",token_response.status_code,token_response.content)
        extract_token = token_response.json()['access_token']
        # userinfo_url = "http://localhost:8180/auth/realms/lsac/protocol/openid-connect/userinfo"
        # userinfo_url = "http://localhost:8888/realms/test/protocol/openid-connect/userinfo"
        userinfo_headers = {"Authorization":"Bearer "+extract_token}
        #         # time.sleep(2)
        # print(userinfo_headers)
        userinfo_response = req.get(userinfo_url,headers=userinfo_headers)
        print(email," ==> ",userinfo_response.status_code,userinfo_response.json())
    except Exception as e:
        print("error in processing",e)

if config['LOCAL_KC_BROWSER_FLOW']:
    token_url = config['LOCAL_KC_BASE_URL']+"/auth/realms/lsac/protocol/openid-connect/token"
    userinfo_url = config['LOCAL_KC_BASE_URL']+"/auth/realms/lsac/protocol/openid-connect/userinfo"
    password = config['COMMON_USER_PASSWORD']
    client_id = config['LOCAL_KC_CLIENT_ID']
    client_secret = config['LOCAL_KC_CLIENT_SECRET']
    for i in tqdm(range(0,user_count)):
        print(users_email_list[i])
        thread_var = Thread(target=browser_auth_local_kc,args=(users_email_list[i],client_id,password,client_secret,token_url,userinfo_url))
        # thread_var.start()
        thread_list.append(thread_var)
        # print(thread_list)
    for i in range(0,len(thread_list)):
        thread_list[i].start()
# print(auth_response.headers["Location"])

# # bs2=bs(auth_response.content,"html.parser")
# # print(bs2.prettify())
# logout = req.get("http://localhost:8888/realms/test/protocol/openid-connect/logout",headers=token_headers)
# # print(logout.status_code)
# # userinfo = req.get("http://localhost:8888/realms/test/protocol/openid-connect/userinfo",headers=headers)
# # print(userinfo.status_code)
# # print(bs2.prettify())



# headers = {"Content-Type":"application/x-www-form-urlencoded",'User-Agent': 'Mozilla/5.0'}
# # token_url = "http://localhost:8888/realms/test/protocol/openid-connect/token"
# # userinfo_url = "http://localhost:8888/realms/test/protocol/openid-connect/userinfo"
# token_url = "http://localhost:8180/auth/realms/lsac/protocol/openid-connect/token"
# userinfo_url = "http://localhost:8180/auth/realms/lsac/protocol/openid-connect/userinfo"
# data = {
# "client_id":"lsac-platform-home",
# "grant_type":"password",
# "service":"lsac-platform-home",
# "username":"aaliyah.lowe@saama.com",
# "password":"Saama@12345!",
# # "client_secret":"euz7xfEM5dX2U1EUH7HUlaa8SMgtebz2",
# "client_secret":"0PKnN4WWvOcnws99bqMxIWUc6YSV7dqO",
# "scope":"openid",
# "account":"sch-dev-test"
# }
# token_response = req.post(token_url,headers=headers,data=data)
# # print(token_response.content)
# token = token_response.json()['access_token']
# # print(token_response.json()['access_token'])
# userinfo_headers = {"Authorization":"Bearer "+token}
# userinfo_response = req.get(userinfo_url,headers=userinfo_headers)
# print(userinfo_response.json())
# bs(token_response,"")
