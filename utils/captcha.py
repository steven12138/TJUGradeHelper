import random
from io import BytesIO

import ddddocr


class captcha_handler:
    def __init__(self, session):
        self.img_byte = None
        self.x = session
        self.captcha_id = random.random()
        self.captcha_url = "https://sso.tju.edu.cn/cas/images/kaptcha.jpg?id=%.16f" % self.captcha_id
        self.captcha_path = "captcha/captcha_%.16f.jpg" % self.captcha_id

    def get_captcha(self):
        ocr = ddddocr.DdddOcr(show_ad=False)
        captcha = self.img_byte.getvalue()
        res = ocr.classification(captcha)
        return res

    def refresh_captcha_path(self):
        self.captcha_id = random.random()
        self.captcha_url = "https://sso.tju.edu.cn/cas/images/kaptcha.jpg?id=%.16f" % self.captcha_id
        self.captcha_path = "captcha/captcha_%.16f.jpg" % self.captcha_id

    def read_captcha(self):
        self.refresh_captcha_path()
        r = self.x.get(self.captcha_url, stream=True)
        self.img_byte = BytesIO()
        for chunk in r.iter_content(chunk_size=512):
            self.img_byte.write(chunk)
        result = self.get_captcha()
        return result

    def get_final_captcha(self):
        res = ""
        while len(res) != 4:
            res = self.read_captcha()
        return res
