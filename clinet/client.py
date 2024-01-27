import sys
import threading
import time
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
import socket
import webbrowser
from PIL import Image, ImageTk
from time import sleep
from datetime import datetime

ISOTIMEFORMAT = '%Y-%m-%d %H:%M:%S'  # 时间格式声明
SOCK_IP = '127.0.0.1'
SOCK_PORT = 4444


class Login:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title('')
        self.window.geometry('400x600')
        self.window.iconbitmap(default="")
        self.window.resizable(False, False)

        canvas = tk.Canvas(self.window, height=400, width=400)
        im = Image.open("images/chat.png")
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
        entry_usr_name.config(font=("Arial", 27))

        entry_usr_pwd = tk.Entry(self.window, textvariable=var_usr_pwd, width=15)
        self.on_focus_out(entry_usr_pwd, "密码")
        entry_usr_pwd.bind('<FocusOut>', lambda event: self.on_focus_out(entry_usr_pwd, "密码", event=event))
        entry_usr_pwd.bind('<FocusIn>', lambda event: self.on_entry_click(entry_usr_pwd, "密码", event=event))
        entry_usr_pwd.place(x=50, y=260)
        entry_usr_pwd.config(font=("Arial", 27))

        tips_label = tk.Label(self.window, text='')
        tips_label.place(x=52, y=305)

        btn_login = tk.Button(self.window, text=' 登  录 ',
                              command=lambda: self.login(tips_label, user=entry_usr_name.get(), passwd=var_usr_pwd.get()),
                              width=42, height=2, bg='#90CBFB')
        btn_login.place(x=52, y=330)

        self.window.mainloop()

    def open_website(self, url):
        webbrowser.open(url)

    def on_entry_click(self, entry, default_text, event=None):
        if entry.get() == default_text:
            entry.delete(0, tk.END)
            entry.config(fg='black')

    def on_focus_out(self, entry, default_text, event=None):
        if not entry.get():
            entry.insert(0, default_text)
            entry.config(fg='gray')

    def login(self, l, user='', passwd=''):
        s = socket.socket()
        s.connect((SOCK_IP, SOCK_PORT))
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
            time.sleep(0.5)
            threading.Thread(target=self.chat_gui_run, args=(s,)).start()
            self.window.destroy()  # 关闭登录窗口

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

    def chat_gui_run(self, s):
        data = {
            "type": "success"
        }
        s.send(f'{data}'.encode())
        sleep(0.5)
        chat = Chat(s)


class Chat:
    def __init__(self, s):
        self.master = tk.Tk()
        self.s = s
        self.master.title("Chat_2024")
        self.master.geometry("650x400")
        self.master.resizable(False, False)
        self.master.overrideredirect(False)
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.selection_tree = ttk.Treeview(self.master)
        self.selection_tree.heading("#0", text="搜索", anchor=tk.W)
        self.selection_tree.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        is_time = "2024/1/26 17:30"
        is_send = "最新消息"
        self.selection_tree.insert("", tk.END, text=f"      MoJang  {is_time}")
        self.selection_tree.insert("", tk.END, text=f"      {is_send}")

        image = Image.open("images/01.png")
        image = image.resize((35, 35))
        self.img = ImageTk.PhotoImage(image)
        self.image_label = tk.Label(self.master, image=self.img)
        self.image_label.place(x=5, y=29)

        self.search = tk.StringVar()
        self.search_input = tk.Entry(self.master, textvariable=self.search, width=10)
        self.search_input.config(font=("Fangsong", 18))
        self.search_input.place(x=4, y=0)

        self.add_button = tk.Button(self.master, text=" + ", command=self.connect_to_server, bg="#66c2ff", fg="white",
                                    relief=tk.FLAT)
        self.add_button.place(x=175, y=0)

        self.send_button = tk.Button(self.master, text=" 搜索 ", command=self.send_message, bg="#4CAF50", fg="white",
                                     relief=tk.FLAT)
        self.send_button.place(x=130, y=0)

        self.chat_display = scrolledtext.ScrolledText(self.master, wrap=tk.WORD, width=40, height=20, fg="black")
        self.chat_display.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.input_entry = tk.Entry(self.master, width=40, bg="white", fg="black", font=("Helvetica", 12))
        self.input_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.input_entry.bind("<Return>", self.send_message)

        self.send_button = tk.Button(self.master, text="发送", command=self.send_message, bg="#4CAF50", fg="white",
                                     font=("Helvetica", 12), relief=tk.FLAT)
        self.send_button.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=10)

        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.start()

        self.master.mainloop()

    def send_message(self, event=None):
        message = self.input_entry.get()
        if message:
            try:
                self.s.send(message.encode('utf-8'))
            except Exception as error:
                print(f"Error sending message: {error}")
                self.s.close()
                messagebox.showerror("Error", "Connection lost.")
                self.master.destroy()
        self.input_entry.delete(0, tk.END)

    def on_close(self):
        try:
            self.s.close()  # 关闭连接的socket
        except Exception as error:
            print(f"Error closing socket: {error}")
        finally:
            self.master.destroy()  # 关闭窗口
            sys.exit()

    def receive_messages(self):
        while True:
            try:
                message = self.s.recv(1024).decode('utf-8')
                self.chat_display.insert(tk.END, message + "\n")
                self.chat_display.yview(tk.END)
            except Exception as error:
                print(f"Error receiving message: {error}")
                self.s.close()
                messagebox.showerror("Error", "Connection lost.")
                self.master.destroy()
                break

    def connect_to_server(self):
        server_info = simpledialog.askstring("添加服务器", "请输入服务器信息（格式：host:port）:")
        if server_info:
            try:
                host, port = server_info.split(':')
                port = int(port)
                self.s.connect((host, port))
                messagebox.showinfo("成功", "成功连接到服务器！")
            except Exception as error:
                messagebox.showerror("错误", f"连接服务器时出错: {error}")


if __name__ == '__main__':
    login_window = Login()
