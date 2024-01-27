import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
import socket
import threading
from PIL import Image, ImageTk  # Make sure to install the Pillow library


class ChatClient:
    def __init__(self, master):
        self.master = master
        self.master.title("Chat_2024")
        self.master.geometry("650x400")
        self.master.resizable(False, False)
        self.master.overrideredirect(False)

        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Left selection tree
        self.selection_tree = ttk.Treeview(master)
        self.selection_tree.heading("#0", text="搜索", anchor=tk.W)
        self.selection_tree.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        is_time = "2024/1/26 17:30"
        is_send = "最新消息"
        self.selection_tree.insert("", tk.END, text=f"      MoJang  {is_time}")
        self.selection_tree.insert("", tk.END, text=f"      {is_send}")

        # Add an image label next to the selection tree
        image = Image.open("images/01.png")  # Replace with the path to your image
        image = image.resize((35, 35))  # Adjust the size as needed
        self.img = ImageTk.PhotoImage(image)
        self.image_label = tk.Label(master, image=self.img)
        self.image_label.place(x=5, y=29)

        # Add a "+" button to the right of the selection tree
        self.search = tk.StringVar()
        self.search_input = tk.Entry(master, textvariable=self.search, width=10)
        self.search_input.config(font=("Fangsong", 18))
        self.search_input.place(x=4, y=0)


        self.add_button = tk.Button(master, text=" + ", command=self.button_clicked, bg="#66c2ff", fg="white",
                                    relief=tk.FLAT)
        self.add_button.place(x=175, y=0)

        # Add a "发送" button to the right of the selection tree
        self.send_button = tk.Button(master, text=" 搜索 ", command=self.send_message, bg="#4CAF50", fg="white",
                                     relief=tk.FLAT)
        self.send_button.place(x=130, y=0)

        # Chat display area
        self.chat_display = scrolledtext.ScrolledText(master, wrap=tk.WORD, width=40, height=20, fg="black")
        self.chat_display.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Input box
        self.input_entry = tk.Entry(master, width=40, bg="white", fg="black", font=("Helvetica", 12))
        self.input_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.input_entry.bind("<Return>", self.send_message)

        # Send button
        self.send_button = tk.Button(master, text="发送", command=self.send_message, bg="#4CAF50", fg="white",
                                     font=("Helvetica", 12), relief=tk.FLAT)
        self.send_button.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=10)

        # Client socket
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('127.0.0.1', 4444))

        # Start the thread to receive messages
        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.start()

    def send_message(self, event=None):
        message = self.input_entry.get()
        if message:
            try:
                self.client_socket.send(message.encode('utf-8'))
            except Exception as error:
                print(f"Error sending message: {error}")
                self.client_socket.close()
                messagebox.showerror("Error", "Connection lost.")
                self.master.destroy()
        self.input_entry.delete(0, tk.END)

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                self.chat_display.insert(tk.END, message + "\n")
                self.chat_display.yview(tk.END)
            except Exception as error:
                print(f"Error receiving message: {error}")
                self.client_socket.close()
                messagebox.showerror("Error", "Connection lost.")
                self.master.destroy()
                break

    def button_clicked(self):
        # 弹出对话框以输入服务器信息
        server_info = simpledialog.askstring("添加服务器", "请输入服务器信息（格式：host:port）:")

        if server_info:
            try:
                host, port = server_info.split(':')
                port = int(port)
                # 连接到新的服务器
                self.client_socket.connect((host, port))
                messagebox.showinfo("成功", "成功连接到服务器！")
            except Exception as error:
                messagebox.showerror("错误", f"连接服务器时出错: {error}")


if __name__ == "__main__":
    root = tk.Tk()
    chat_client_app = ChatClient(root)
    root.mainloop()
