import pandas as pd
import json


df = pd.read_excel('UserTemplate (4) (2).xlsx')

df = df.rename(columns={"First Name":"firstName","Last Name":"lastName","Email":"email"})
df["username"] = df.apply(lambda x:x["email"],axis=1)
df=df.drop("SSO",axis=1)
df=df.drop("Account Role",axis=1)
print(len(df))
df["emailVerified"]=pd.Series([True for i in range(len(df))])
df["enabled"]=pd.Series([True for i in range(len(df))])
print(df.to_dict("records"))
content = {"users":df.to_dict("records")}


with open("users.json","w") as f:
    json.dump(content,f)


# {"username":"jose.perez","email":"jose.perez@gmail.com","firstName":"Jose","lastName":"Perez","emailVerified":true,"enabled":true














