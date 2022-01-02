from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import (QScrollArea, QVBoxLayout, QHBoxLayout, QSplitter, QStyleFactory, QWidget, QLabel, QLineEdit,QDesktopWidget, QGraphicsDropShadowEffect,
                             QTextEdit, QGridLayout, QApplication, QInputDialog, QPushButton, QFrame, QSplashScreen, QMessageBox, QFileDialog)

from PyQt5.QtWidgets import (QWidget, QSlider, QLineEdit, QPlainTextEdit, QLabel, QPushButton, QScrollArea,QApplication,
                             QHBoxLayout, QVBoxLayout, QMainWindow, QSizePolicy)
from PyQt5.QtCore import Qt


import requests
import random
import sys
import os

lst = ["How are you", "I am fine, thank you ksjdhbfjsdhfvkjdskuhsdiufyhsdhskfgsfcgjususgfcuhndgnhjdnfvgxd", "Hi", "Hello"]

USER_DEATILS = open("user.txt", "r").read().split("\n")
USERNAME = USER_DEATILS[0]
PASSWORD = USER_DEATILS[1]

CHAT_AREA = None
USER_AREA = None
MOVED_TO_BOTTOM = False
CHAT_TITLE_AREA = None
CURRENT_USER = None


##to_username = "ayush"
##from_username = "rajma"
##password = "22fe3ffce7c2dca5bef3"
##
##def check_messages():
##    while True:
##        data = requests.get(f"https://test-app-goo.herokuapp.com/check_new_messages?username={to_username}&password={password}").json()#22fe3ffce7c2dca5bef3
##        if data["data"]:
##            for msg in data["data"]:
##                #print(msg["message"])
##
##def send_message(msg):
##    data = requests.get(f"https://test-app-goo.herokuapp.com/send_message?from_username=ayush&to_username=rajma&message={msg}&password={password}").json()

class Check_new_message(QtCore.QThread):
    change_value = QtCore.pyqtSignal(dict)

    def __init__(self, username, password):
        super().__init__()
        self.username = username
        self.password = password
        

    def run(self):
        global MOVED_TO_BOTTOM
        try:
            while True:
                data = requests.get(f"https://test-app-goo.herokuapp.com/check_new_messages?username={self.username}&password={self.password}").json()#22fe3ffce7c2dca5bef3
                if data["data"]:
                    self.change_value.emit(data)
                    MOVED_TO_BOTTOM = True
                else:
                    MOVED_TO_BOTTOM = False
        except Exception as e:
            print(e)
            #change_value.emit({"status": "no_internet"})



##class Extract_message(QtCore.QThread):
##    change_value = QtCore.pyqtSignal(dict)
##
##    def __init__(self, username, password):
##        super().__init__(parent)
##        self.username = username
##        self.password = password
##
##    def run(self):
##        try:
##            data = requests.get(f"https://test-app-goo.herokuapp.com/check_all_messages?username={self.username}&password={self.password}").json()#22fe3ffce7c2dca5bef3
##            if data["data"]:
##                for msg in data["data"]:
##                    change_value.emit(msg)
##        except:
##            change_value.emit({"status": "no_internet"})

def Add_shadow_effect(obj):
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(15)
    obj.setGraphicsEffect(shadow)


class MsgLabel(QLabel):
    def __init__(self, *args):
        super(MsgLabel, self).__init__(*args)

    def resizeEvent(self, event):
        width = self.width()
        height = self.height()
        #print(height)
        


class Users_area(QScrollArea):
    def __init__(self, parent, width=None, height=None, array = []):
        super().__init__(parent)
        self.main_win_width = width
        self.main_win_height = height
        self.users = []

        self.widget = QWidget()
        
        self.layout = QVBoxLayout(self.widget)
        self.layout.setAlignment(Qt.AlignTop)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        sec_width = self.main_win_width/4.17 #460
        sec_height = self.main_win_height/19.5 #50
        multiplier = sec_height - 10

        if sec_height < 44:
            sec_height = 44

        for info in array:#for items in sections:
            user = info["from_username"]
            if user in self.users or user == USERNAME:
                continue
            self.users.append(user)
            #print(info)
            lb = QLabel()
            lb.setStyleSheet("background-color: rgb(240, 240, 240)")
            obj_lst = []
                
            but = QPushButton(lb)
            chapter = QLabel(user, but)
            chapter.setAttribute(QtCore.Qt.WA_TranslucentBackground)
            font = chapter.font()
            font.setPointSize(12)
            chapter.setFont(font)
            chapter.move(10, sec_height//2-10)

            but.clicked.connect(lambda event, user=user: self.load_new_chat(user))
            but.move(0, 0)
            but.setFixedSize(sec_width, sec_height)
            but.setStyleSheet("""QPushButton{
                                    background-color: rgb(230, 230, 230);
                                    border-radius: 5px}
                                QPushButton::hover{
                                    background-color: rgb(210, 210, 210);}""")
            #Add_shadow_effect(but)
            
            lb.setFixedSize(sec_width, sec_height)
            self.layout.addWidget(lb)

        self.setWidget(self.widget)
        self.setWidgetResizable(True)

    def load_new_chat(self, user):
        global CURRENT_USER
        CURRENT_USER = user
        data = requests.get(f"https://test-app-goo.herokuapp.com/get_user?username={user}&password={PASSWORD}&by_username={USERNAME}").json()
        if data["msg"] == "Success":
            CHAT_TITLE_AREA.setText(f"{data['data']['first_name']} {data['data']['last_name']}")
            CHAT_AREA.clear_chat()
            CHAT_AREA.add_user(user)


class Chat_area(QScrollArea):
    def __init__(self, parent, width=None, height=None, from_user = "gopi"):
        global MOVED_TO_BOTTOM
        super().__init__(parent)
        self.spacer = None
        self.main_win_width = width
        self.main_win_height = height
        self.add_user(from_user)
        data = requests.get(f"https://test-app-goo.herokuapp.com/get_user?username={from_user}&password={PASSWORD}&by_username={USERNAME}").json()
        CHAT_TITLE_AREA.setText(f"{data['data']['first_name']} {data['data']['last_name']}")
        MOVED_TO_BOTTOM = False
        #print(dir(self))


    def add_user(self, user):
        self.array = requests.get(f"https://test-app-goo.herokuapp.com/check_messages_for_particular_user?from_user={user}&username={USERNAME}&password={PASSWORD}").json()
        self.array = self.array["data"]
        
        self.widget = QWidget()
        
        self.layout = QVBoxLayout(self.widget)
        self.layout.setAlignment(Qt.AlignTop)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        sec_width = self.main_win_width - self.main_win_width/3.5#self.main_win_width/4.17 #460
        sec_height = 30
        multiplier = sec_height - 10

        self.sec_width = sec_width
        self.sec_height = sec_height
        self.multiplier = multiplier

##        if sec_height < 44:
##            sec_height = 44

        for info in self.array:#for items in sections:
            sender = info["from_username"]
            msg = info["message"]
            sec_height = 30
            lb = QLabel()
            lb.setAttribute(QtCore.Qt.WA_TranslucentBackground)
            lb.setStyleSheet("background-color: rgb(240, 240, 240)")
            obj_lst = []

            #msg = random.choice(lst)
            
            

##            for j in range(len(msg)):
##                msg_temp += msg[j]
##                if j%100 == 0 and j > 0:
##                    #print(j)
##                    msg_temp += "\n"
##                    sec_height += 30
                
                
            condn = sender != user
            but = QLabel(lb)
            but.setAttribute(QtCore.Qt.WA_TranslucentBackground)
            msg_label = MsgLabel(msg, but)
            #msg_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            msg_label.setWordWrap(True)  
            msg_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
            if condn:
                msg_label.setStyleSheet("background-color: rgb(239, 253, 200);padding :5px")
            else:
                msg_label.setStyleSheet("background-color: rgb(180, 255, 200);padding :5px")
            msg_label.setAlignment(QtCore.Qt.AlignVCenter)
            
            #msg_label.setFixedHeight(sec_height)
            
##            chapter = QLabel("MSG", but)
#            chapter.setAttribute(QtCore.Qt.WA_TranslucentBackground)
            font = msg_label.font()
            font.setPointSize(10)
            msg_label.setFont(font)
            msg_label.show()
            sec_height = msg_label.height()
            ##print(dir(msg_label))
            
##            chapter.move(10, sec_height//2-10)
##            chapter.setAlignment(Qt.AlignCenter)
            #but.clicked.connect(lambda event, arrow=arrow, lb=lb, lst=obj_lst, height=lb_height: self.restore_size(arrow, lb, lst, height))
            if condn:
                msg_label.move(sec_width//2.5 - msg_label.width(), msg_label.y())
                but.move(sec_width//1.7 - 25, 0)
            else:
                but.move(25, 0)
            
            but.setFixedSize(sec_width//2.5, sec_height)
            but.setStyleSheet("""background-color: rgb(240, 240, 240);
                                border-radius: 5px
                                """)
            
            
            lb.setFixedSize(sec_width, sec_height)
            self.layout.addWidget(lb)

        self.setWidget(self.widget)
        #print(dir(self))
        self.setStyleSheet("""background-color: QLinearGradient( x1: 0, y1: 0,
                             x2: 1, y2: 0, 
                          stop: 0 #c4f081, 
                          stop: 1 #91eddc);}
                          """)
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setWidgetResizable(True)

##
##    def add_spacer(self):
##        del self.spacer
##        self.spacer = QLabel()
##        self.spacer.setFixedSize(50, 50)
##        self.layout.addWidget(self.spacer)
##        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

    def scroll_to_bottom(self):
        global MOVED_TO_BOTTOM
        MOVED_TO_BOTTOM = True

    def scrolled(self):
        global MOVED_TO_BOTTOM
        MOVED_TO_BOTTOM = False

    def clear_chat(self):
        self.widget.deleteLater()

    def eventFilter(self, event, evt):
        global MOVED_TO_BOTTOM
##        #print(type(evt))
##        #print(self.verticalScrollBar().value())
        try:
            if MOVED_TO_BOTTOM:
                
                self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())
                
        except:
            MOVED_TO_BOTTOM = False
        return False


    def add_messages(self, user, array):
##        spacer = QLabel()
##        spacer.setFixedSize(100, 100)
        for info in array["data"]:
            sender = info["from_username"]
            msg = info["message"]
            if sender != user:
                continue
            sec_height = 30
            sec_width = self.main_win_width - self.main_win_width/3.5
            lb = QLabel()
            lb.setAttribute(QtCore.Qt.WA_TranslucentBackground)
            lb.setStyleSheet("background-color: rgb(240, 240, 240)")
            obj_lst = []
            
            condn = sender == USERNAME
            but = QLabel(lb)
            but.setAttribute(QtCore.Qt.WA_TranslucentBackground)
            msg_label = MsgLabel(msg, but)
            msg_label.setWordWrap(True)  
            msg_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
            if condn:
                msg_label.setStyleSheet("background-color: rgb(239, 253, 200);padding :5px")
            else:
                msg_label.setStyleSheet("background-color: rgb(180, 255, 200);padding :5px")
            msg_label.setAlignment(QtCore.Qt.AlignVCenter)
            
            font = msg_label.font()
            font.setPointSize(10)
            msg_label.setFont(font)
            msg_label.show()
            sec_height = msg_label.height()
            #print(sec_height)
            
            if condn:
                msg_label.move(sec_width//2.5 - msg_label.width(), msg_label.y())
                but.move(sec_width//1.7 - 25, 0)
            else:
                but.move(25, 0)
            
            but.setFixedSize(sec_width//2.5, sec_height)
            but.setStyleSheet("""background-color: rgb(240, 240, 240);
                                border-radius: 5px
                                """)
            
            
            lb.setFixedSize(sec_width, sec_height)
            
            self.layout.insertWidget(-1, lb)
            self.scroll_to_bottom()


    def add_message(self, msg):
        sec_height = 30
        sec_width = self.main_win_width - self.main_win_width/3.5
        lb = QLabel()
        lb.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        lb.setStyleSheet("background-color: rgb(240, 240, 240)")
        obj_lst = []
        but = QLabel(lb)
        but.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        msg_label = MsgLabel(msg, but)
        msg_label.setWordWrap(True)  
        msg_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        msg_label.setStyleSheet("background-color: rgb(239, 253, 200);padding :5px")
        
        msg_label.setAlignment(QtCore.Qt.AlignVCenter)
        
        font = msg_label.font()
        font.setPointSize(10)
        msg_label.setFont(font)
        msg_label.show()
        sec_height = msg_label.height()
        #print(sec_height)
        msg_label.move(sec_width//2.5 - msg_label.width(), msg_label.y())
        but.move(sec_width//1.7 - 25, 0)
        
        but.setFixedSize(sec_width//2.5, sec_height)
        but.setStyleSheet("""background-color: rgb(240, 240, 240);
                            border-radius: 5px
                            """)
        
        
        lb.setFixedSize(sec_width, sec_height)
        
        self.layout.insertWidget(-1, lb)
        self.scroll_to_bottom()
        
        #self.setWidgetResizable(True)
##        self.layout.addWidget(spacer)
        #self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())
        #self.layout.setContentsMargins(0, 0, 0, 0)

        
class MainWindow(QMainWindow):
    def __init__(self):
        global CHAT_AREA, USER_AREA, CHAT_TITLE_AREA, CURRENT_USER
        super().__init__()
##        self.user = "gopi"
##        CURRENT_USER = self.user
        self.all_messages = requests.get(f"https://test-app-goo.herokuapp.com/check_all_messages?username={USERNAME}&password={PASSWORD}").json()
        #print(self.all_messages)
        self.width = QDesktopWidget().screenGeometry(-1).width()
        self.height = QDesktopWidget().screenGeometry(-1).height()
        self.dx = self.height/10.38

        self.scroll = QScrollArea()             
        self.widget = QWidget()                 
        self.vbox = QVBoxLayout()

        self.main_win = QFrame()
        self.main_win.setStyleSheet("QFrame{background-color: rgb(255, 255, 255)}")
        self.main_win.setMinimumSize(self.width, self.height-self.dx)
        self.vbox.addWidget(self.main_win)

        self.title_area = QLabel("MessagingApp", self.main_win)
        self.title_area.move(10, 10)
        self.title_area.setFixedSize(self.main_win.width()/3.84, self.main_win.height()/8)
        self.title_area.setStyleSheet("""background-color: rgb(145, 237, 220);""")
        self.title_area.setAlignment(Qt.AlignCenter)
        font = self.title_area.font()
        font.setPointSize(15)
        self.title_area.setFont(font)

        self.chat_title_area = QLabel("Name", self.main_win)
        self.chat_title_area.move(self.main_win.width()/3.84+15, 10)
        self.chat_title_area.setFixedSize(self.main_win.width() - self.main_win.width()/3.65, self.main_win.height()/14)
        self.chat_title_area.setStyleSheet("""background-color: rgb(145, 237, 220);""")
        self.chat_title_area.setAlignment(Qt.AlignCenter)
        font = self.chat_title_area.font()
        font.setPointSize(15)
        self.chat_title_area.setFont(font)
        CHAT_TITLE_AREA = self.chat_title_area

        self.area = Users_area(self.main_win, self.main_win.width(), self.main_win.height(), self.all_messages["data"])
        self.area.move(10, self.main_win.height()/8)
        self.area.setFixedSize(self.main_win.width()/3.84, self.main_win.height()/1.13)
        USER_AREA = self.area

        self.chat_area = Chat_area(self.main_win, self.main_win.width(), self.main_win.height())
        self.chat_area.move(self.main_win.width()/3.84+15, self.main_win.height()/14)
        self.chat_area.setFixedSize(self.main_win.width() - self.main_win.width()/3.65, self.main_win.height()/1.13)
        CHAT_AREA = self.chat_area

        self.thread = Check_new_message(USERNAME, PASSWORD)
        self.thread.change_value.connect(self.update_ui)
        self.thread.start()

        self.widget.setLayout(self.vbox)
        
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(False)
        self.scroll.setWidget(self.widget)

        self.text_box = QPlainTextEdit(self.main_win)
        self.text_box.setFixedSize(self.main_win.width() - self.main_win.width()/3.65, 50)
        self.text_box.move(self.main_win.width()/3.84+15, (self.main_win.height()/14) + self.main_win.height()/1.13)
        font = self.text_box.font()
        font.setPointSize(14)
        self.text_box.setFont(font)
        self.text_box.setPlaceholderText("Type a message...")

        self.find_user = QPushButton("+", self.main_win)
        self.find_user.setFixedSize(70, 70)
        self.find_user.move(self.main_win.width()/3.84 - 100, self.main_win.height()/1.13)
        self.find_user.setStyleSheet("""background-color: QLinearGradient( x1: 0, y1: 0,
                             x2: 1, y2: 0, 
                          stop: 0 #c4f081, 
                          stop: 1 #91eddc);
                          border-radius: 35px}
                          """)
        Add_shadow_effect(self.find_user)
        #self.find_user.setAlignment(QtCore.Qt.AlignCenter)
        font = self.find_user.font()
        font.setPointSize(20)
        self.find_user.setFont(font)

        self.send = QPushButton("➤", self.text_box)
        self.send.setFixedSize(50, 50)
        self.send.move(self.text_box.width()-50, self.text_box.height()-50)
        self.send.setStyleSheet("""background-color: QLinearGradient( x1: 0, y1: 0,
                             x2: 1, y2: 0, 
                          stop: 0 #c4f081, 
                          stop: 1 #91eddc);}
                          """)
        self.send.clicked.connect(self.send_message)

        self.vbox.setContentsMargins(0, 0, 0, 0)

        self.setCentralWidget(self.scroll)

        self.showMaximized()


    def send_message(self):
        msg = self.text_box.toPlainText()

##        self.chat_area.show()
        #print(CURRENT_USER)
        self.text_box.clear()
        temp = requests.get(f"https://test-app-goo.herokuapp.com/send_message?from_username={USERNAME}&to_username={CURRENT_USER}&message={msg}&password={PASSWORD}").json()
        self.chat_area.add_message(msg)
##        print(temp)
        #add_message


##    def load_new_chat(self, user):
##        data = requests.get(f"https://test-app-goo.herokuapp.com/get_user?username={user}&password=c0178f00703a609f553a&by_username=rajma").json()
##        if data["msg"] == "Success":
##            self.user = user
##            print(data)
##            self.chat_title_area.setText(f"{data['data']['first_name']} {data['data']['last_name']}")
##            self.chat_area.clear_chat()
##            self.chat_area.add_user(user)


    def update_ui(self, val):
        self.chat_area.scroll_to_bottom()
        print(CURRENT_USER)
        self.chat_area.add_messages(CURRENT_USER, val)
##        self.chat_area.show()
##        self.chat_area.update()
        #self.chat_area.scrolled()
        #self.chat_area.verticalScrollBar().setValue(self.chat_area.verticalScrollBar().maximum())
        ##print(dir(self.chat_area))

def main():
    app = QApplication(sys.argv)
    main = MainWindow()
    sys.exit(app.exec_())

sys._excepthook = sys.excepthook
def exception_hook(exctype, value, traceback):
    print(exctype, value, traceback)
    sys._excepthook(exctype, value, traceback) 
    sys.exit(1)
   
if __name__ == '__main__':
    sys.excepthook = exception_hook
    main()
