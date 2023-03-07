from utils.login import login_loader
import re
import time

usr = ""
pwd = ""
sem = 76


class Provider:
    def __init__(self, usr, pwd, sem):
        loader = login_loader(usr, pwd)
        self.sem = sem
        self.x = loader.login()

    def update(self):
        data = self.x.get(
            f"http://classes.tju.edu.cn/eams/teach/grade/course/person!search.action?semesterId={self.sem}&projectType=&_"
            f"=1678176732941", ).text
        pattern = r'<tr class=".*">(?:.|\n)+?</tr>'
        match = re.findall(pattern, data)
        ls = []
        for item in match:
            name = re.findall(r"[\u4e00-\u9fa5]+", item)[0]
            score = int(re.findall("[0-9].*", re.findall(r'style.*">(?:.|\n)+?<', item)[0])[0])
            ls.append([name, score])
        return ls


if __name__ == "__main__":
    pvd = Provider(usr, pwd, sem)
    pvd.update()
