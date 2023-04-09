import certifi
import requests


url = "https://192.168.3.199:8443/login"
headers = {
    "Cookie": "sessionid=6f897e3e35fb719730bcc09838e6996e3fb3835b1081d1aee3a54a017efb973c",
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E)",
}

response = requests.post(url=url, headers=headers)
print(response.status_code)
print(response.text)

# Cookie: sessionid=cdd0adc69b3fb9eadafd6c049b32121a2a11e084ac4574c311168b1782ddcd85
