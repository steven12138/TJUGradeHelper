import requests
from utils.captcha import captcha_handler


class login_DTO:
    def __init__(self, usr, pwd, captcha):
        self.usr = usr
        self.pwd = pwd
        self.captcha = captcha

    def get_data(self):
        return {
            "username": self.usr,
            "password": self.pwd,
            "captcha": self.captcha,
            "execution": "e2s1",
            "_eventId": "submit",
            "geolocation": ""
        }


class UsernamePasswordErrorException(Exception):
    def __str__(self) -> str:
        return "ERROR: Username or Password Error\n" + super().__str__()


class NetworkErrorException(Exception):
    def __str__(self) -> str:
        return "ERROR: Network Error\n" + super().__str__()


class login_loader:
    def __init__(self, usr, pwd) -> None:
        self.x = None
        self.usr = usr
        self.pwd = pwd
        self.captcha_url = None
        self.captcha_path = None
        self.captcha_id = None
        self.login_url = "https://sso.tju.edu.cn/cas/login?service=http%3A%2F%2Fclasses.tju.edu.cn%2Feams%2FhomeExt.action%3Bjsessionid%3DC2885AAC82F28DCBA5DFDB98F6726B78.std2"

    def login(self):
        self.x = requests.session()
        result = self.x.get("http://classes.tju.edu.cn/eams/homeExt.action")
        self.x.get(self.login_url)
        captcha = captcha_handler(session=self.x).get_final_captcha()
        dto = login_DTO(self.usr, self.pwd, captcha).get_data()
        result = self.x.post(self.login_url, data=dto)
        result = self.x.get(result.url)
        final_url = "http://classes.tju.edu.cn/eams/homeExt.action"
        test = self.x.get(final_url)
        if test.status_code!=200:
            raise NetworkErrorException
        if final_url != test.url:
            raise UsernamePasswordErrorException
        print()
        return self.x
