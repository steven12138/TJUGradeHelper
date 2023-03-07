from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QTableWidget, QTableWidgetItem, QSizePolicy, \
    QLineEdit, QPushButton, QHBoxLayout, QHeaderView, QMessageBox
from PyQt5.QtCore import QTimer, QTime, Qt, QObject, pyqtSignal
from functools import partial

from grade_provider import Provider
from utils.login import UsernamePasswordErrorException, NetworkErrorException
import threading
from PyQt5 import sip


class Login(QWidget):
    def __init__(self, callback):
        super().__init__()

        self.setWindowTitle("登录")
        self.setGeometry(100, 100, 300, 150)

        hbox1 = QHBoxLayout()
        hbox2 = QHBoxLayout()
        hbox3 = QHBoxLayout()

        self.username_label = QLabel("Username:", self)
        self.username_label.setStyleSheet("font-size: 24px")
        self.username_input = QLineEdit(self)
        self.username_input.setStyleSheet("font-size: 24px")
        hbox1.addWidget(self.username_label)
        hbox1.addWidget(self.username_input)

        self.password_label = QLabel("Password:", self)
        self.password_label.setStyleSheet("font-size: 24px")
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        hbox2.addWidget(self.password_label)
        hbox2.addWidget(self.password_input)

        self.sem_label = QLabel("Semester:", self)
        self.sem_label.setStyleSheet("font-size: 24px")
        self.sem_input = QLineEdit(self)
        self.sem_input.setStyleSheet("font-size: 24px")
        self.sem_input.setText("76")
        hbox3.addWidget(self.sem_label)
        hbox3.addWidget(self.sem_input)

        self.login_button = QPushButton("Login", self)
        self.login_button.setStyleSheet("font-size: 24px")
        self.login_button.clicked.connect(partial(callback, self))

        layout = QVBoxLayout()
        layout.addLayout(hbox1)
        layout.addLayout(hbox2)
        layout.addLayout(hbox3)
        layout.addWidget(self.login_button)
        self.setLayout(layout)

    def get_username(self):
        return self.username_input.text()

    def get_sem(self):
        return self.sem_input.text()

    def get_password(self):
        return self.password_input.text()


last_len = 0


def update_grade(this, table: QTableWidget, pvd: Provider):
    global last_len
    grade = pvd.update()
    table.setRowCount(len(grade))
    if last_len != 0 and len(grade) != last_len:
        QMessageBox.information(this, "成绩发布", "你有新的成绩发布！")

    last_len = len(grade)
    for i, course in enumerate(grade):
        table.setItem(i, 0, QTableWidgetItem(course[0]))
        table.setItem(i, 1, QTableWidgetItem(str(course[1])))
    table.setFixedHeight(table.rowHeight(0) * (last_len + 1))



class Clock(QWidget):
    def __init__(self):
        super().__init__()
        self.pvd = None
        self.proc = None
        self.setWindowTitle("成绩")
        self.setGeometry(50, 50, 500, 300)

        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)

        self.table = QTableWidget(self)
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["课程", "分数"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.resizeColumnsToContents()
        self.table.resizeColumnsToContents()
        self.table.setColumnWidth(0, 200)
        self.table.setColumnWidth(1, 200)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.table)
        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_grade)
        self.setTime()

    def startUpdate(self, pvd):
        self.pvd = pvd
        self.timer.start(5000)

    def setTime(self):
        current_time = QTime.currentTime().toString("hh:mm:ss")
        self.label.setText(f"发布数目：{last_len} | 更新时间：{current_time}")

    def update_grade(self):
        self.setTime()
        self.proc = threading.Thread(target=update_grade, args=(self, self.table, self.pvd))
        self.proc.start()


class LoginTask(QObject):
    finished = pyqtSignal(Provider)
    error = pyqtSignal()
    network = pyqtSignal()

    def run_task(self, usr, pwd, sem):
        try:
            pvd = Provider(usr, pwd, sem)
            self.finished.emit(pvd)
        except UsernamePasswordErrorException:
            print("1")
            self.error.emit()
        except NetworkErrorException:
            print("2")
            self.network.emit()


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.login_proc = None
        self.login_task = None
        self.provider = None

        self.login_page = Login(self.on_login)
        self.clock_page = Clock()
        self.clock_page.hide()

        self.setWindowTitle("查成绩小助手")
        self.setGeometry(100, 100, 500, 300)

        layout = QHBoxLayout()
        layout.addWidget(self.login_page)
        layout.addWidget(self.clock_page)
        self.setLayout(layout)

    def login_finished(self, pvd: Provider):
        self.clock_page.show()
        self.clock_page.startUpdate(pvd)

    def login_error(self):
        print("b")
        QMessageBox.information(self, "提示", "用户名或密码错误")
        self.login_page.show()

    def network_error(self):
        self.login_page.show()
        QMessageBox.warning(self, "Error", "网络错误，请确保校园网环境")

    def on_login(self, login_page):
        self.login_page.hide()
        username = login_page.get_username()
        password = login_page.get_password()
        sem = login_page.get_sem()
        self.login_task = LoginTask()
        self.login_proc = threading.Thread(target=self.login_task.run_task, args=(username, password, sem))
        self.login_proc.start()
        self.login_task.finished.connect(self.login_finished)
        self.login_task.error.connect(self.login_error)
        self.login_task.network.connect(self.network_error)


if __name__ == '__main__':
    app = QApplication([])
    main_app = App()
    main_app.show()
    app.exec_()
