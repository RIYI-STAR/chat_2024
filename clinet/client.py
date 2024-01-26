import threading
import tkinter as tk
import tkinter.messagebox
import webbrowser

from PIL import Image as ima, ImageTk
from time import *
from datetime import *
from socket import *
from tkinter.scrolledtext import ScrolledText

ISOTIMEFORMAT = '%Y-%m-%d %H:%M:%S'  # 时间格式声明
SOCK_IP = '127.0.0.1'  # input("请输入进入房间：")
SOCK_PORT = 5678


class Login:

    def __init__(self):
        self.window = tk.Tk()
        self.window.title('')
        self.window.geometry('400x600')
        self.window.iconbitmap(default="")
        self.window.resizable(False, False)  # 横纵均不允许调整


        # 图标
        canvas = tk.Canvas(self.window, height=400, width=400)
        im = ima.open("images/chat.png")
        image_file = ImageTk.PhotoImage(im)
        canvas.create_image(170, 40, anchor='nw', image=image_file)
        canvas.pack(side='top')

        var_usr_name = tk.StringVar()
        var_usr_pwd = tk.StringVar()

        entry_usr_name = tk.Entry(self.window, textvariable=var_usr_name, width=15)
        self.on_focus_out(entry_usr_name, "用户名")
        entry_usr_name.bind('<FocusOut>', lambda event: self.on_focus_out(entry_usr_name, "用户名", event=event))
        entry_usr_name.bind('<FocusIn>', lambda event: self.on_entry_click(entry_usr_name, "用户名", event=event))
        entry_usr_name.place(x=50, y=200)
        entry_usr_name.config(font=("Arial", 27))  # 设置字体大小

        entry_usr_pwd = tk.Entry(self.window, textvariable=var_usr_pwd, width=15)  # 密码输入框
        self.on_focus_out(entry_usr_pwd, "密码")
        entry_usr_pwd.bind('<FocusOut>', lambda event: self.on_focus_out(entry_usr_pwd, "密码", event=event))
        entry_usr_pwd.bind('<FocusIn>', lambda event: self.on_entry_click(entry_usr_pwd, "密码", event=event))
        entry_usr_pwd.place(x=50, y=260)
        entry_usr_pwd.config(font=("Arial", 27))  # 设置字体大小

        tips_label = tk.Label(self.window, text='')
        tips_label.place(x=52, y=305)

        btn_login = tk.Button(self.window, text=' 登  录 ',
                              command=lambda: self.login(entry_usr_name.get(), var_usr_pwd.get(), tips_label), width=42, height=2,
                              bg='#90CBFB')
        btn_login.place(x=52, y=330)

        self.window.mainloop()

    def open_website(self, url):  # 跳转页面
        webbrowser.open(url)

    def on_entry_click(self, entry, default_text, event=None):
        """当用户点击输入框时清除默认文本"""
        if entry.get() == default_text:
            entry.delete(0, tk.END)
            entry.config(fg='black')

    def on_focus_out(self, entry, default_text, event=None):
        """当输入框失去焦点时，如果内容为空，恢复默认文本"""
        if not entry.get():
            entry.insert(0, default_text)
            entry.config(fg='gray')

    def login(self, user, passwd, l):
        s = socket()  # 套接字
        s.connect((SOCK_IP, SOCK_PORT))  # 建立连接
        d = {
            "type": "login",
            "data": {
                "user": user,
                "passwd": passwd
            }
        }
        s.send(f'{d}'.encode())
        reply = eval(s.recv(4096).decode())
        if reply["type"] == "login_status":
            reply = int(reply["code"])
        if reply == 0:
            r = "登陆成功"
            c = 'green'
            threading.Thread(target=chat_gui_run, args=(self.window,)).start()
        else:
            if reply == 1:
                r = "密码错误"
            elif reply == 2:
                r = "登录次数过多，请十分钟后再登录"
            elif reply == 3:
                r = "您的账号因异常操作被封禁，请联系管理员解封"
            elif reply == -1:
                r = "无此账户,请先注册!"
            s.close()
            c = 'red'
        l.configure(text=r, fg=c)


# 聊天窗口
class Chat:
    def __init__(self):
        print(1)


# 聊天窗口
def chat_gui_run(login_window):
    sleep(0.5)
    login_window.destroy()
    chat = Chat()
    # window = Tk()
    # window.maxsize(650, 400)  # 设置相同的最大最小尺寸，将窗口大小固定
    # window.minsize(650, 400)
    #
    # var1 = StringVar()
    # user_list = []
    # user_list = s.recv(2048).decode('utf-8').split(',')  # 从服务器端获取当前用户列表
    # user_list.insert(0, '------当前用户列表------')
    #
    # nickname = user_list[len(user_list) - 1]  # 获取正式昵称，经过了服务器端的查重修改
    # window.title("客户端" + nickname)  # 设置窗口标题
    # var1.set(user_list)  # 用户列表文本设置
    # # var1.set([1,2,3,5])
    # listbox1 = Listbox(window, listvariable=var1)  # 用户列表，使用Listbox组件
    # listbox1.place(x=510, y=0, width=140, height=300)
    #
    # listbox = ScrolledText(window)  # 聊天信息窗口，使用ScrolledText组件制作
    # listbox.place(x=5, y=0, width=500, height=300)
    #
    # # 接收服务器发来的消息并显示到聊天信息窗口上，与此同时监控用户列表更新
    # def read_server(s):
    #     while True:
    #         content = s.recv(2048).decode('utf-8')  # 接收服务器端发来的消息
    #         curtime = datetime.now().strftime(ISOTIMEFORMAT)  # 获取当前系统时间
    #         listbox.insert(tkinter.END, curtime)  # 聊天信息窗口显示（打印）
    #         listbox.insert(tkinter.END, '\n' + content + '\n\n')
    #         listbox.see(tkinter.END)  # ScrolledText组件方法，自动定位到结尾，否则只有消息在涨，窗口拖动条不动
    #         listbox.update()  # 更新聊天信息窗口，显示新的信息
    #
    #         # 贼傻贼原始的用户列表更新方式，判断新的信息是否为系统消息，暂时没有想到更好的解决方案
    #         if content[0:5] == '系统消息：':
    #             if content[content.find(' ') + 1: content.find(' ') + 3] == '进入':
    #                 user_list.append(content[5:content.find(' ')])
    #                 var1.set(user_list)
    #             if content[content.find(' ') + 1: content.find(' ') + 3] == '离开':
    #                 user_list.remove(content[5:content.find(' ')])
    #                 var1.set(user_list)
    #
    # threading.Thread(target=read_server, args=(s,)).start()
    #
    # var2 = StringVar()  # 聊天输入口
    # var2.set('')
    # entryInput = Entry(window, width=140, textvariable=var2)
    # entryInput.place(x=5, y=305, width=600, height=95)
    #
    # # 发送按钮触发的函数，即发送信息
    # def sendtext():
    #     line = var2.get()
    #     s.send(line.encode('utf-8'))
    #     var2.set('')  # 发送完毕清空聊天输入口
    #
    # # 发送按钮
    # sendButton = Button(window, text='发 送', font=('Fangsong', 18), bg='white', command=sendtext)
    # sendButton.place(x=500, y=305, width=150, height=95)
    #
    # window.mainloop()


if __name__ == '__main__':
    login_window = Login()
