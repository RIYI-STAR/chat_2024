import threading
import atexit
import pymysql

from datetime import *
from socket import *

# 时间格式声明，用于后面的记录系统时间
ISOTIMEFORMAT = '%Y-%m-%d %H:%M:%S'

# 设置IP地址和端口号
SOCK_IP = '127.0.0.1'
SOCK_PORT = 5678

# 用户列表和套接字列表，用于后面给每个套接字发送信息
user_list = []
socket_list = []


# 数据库
class SQL:
    # 设置数据库信息
    SQL_IP = '202.182.125.24'
    SQL_PORT = 20027
    SQL_USERNAME = 'chat2024'
    SQL_PASSWD = 'chat_2024'

    def __init__(self):
        try:
            self.conn = pymysql.connect(
                user=self.SQL_USERNAME,
                passwd=self.SQL_PASSWD,
                host=self.SQL_IP,
                port=self.SQL_PORT,
                database='chat_2024'
            )
            if self.conn:
                print("数据库连接成功!")
        except:
            print("数据库连接失败")

    def __del__(self):
        try:
            self.conn.close()
            print("数据库关闭成功!")
        except AttributeError:
            print("无法正常关闭数据库。。。")
            pass

    def register(self, user, password, name):
        try:
            c = self.conn.cursor()
            c.execute(f"insert chat_2024.users(user, name, password) values('{user}', '{name}', '{password}');")
            c.close()
            return 1
        except:
            return 0

    def logout(self, user, password):
        c = self.conn.cursor()
        c.execute(f"delete from chat_2024.users where user='{user}' and password='{password}'")
        c.close()
        return 0

    def login(self, user, password):
        c = self.conn.cursor()
        now = datetime.now()

        try:
            ip = addr[0]
            self.record_try_login_ip(user, ip)
            info = self.get_user(user)
            status = self.get_user_status(user)
            try_to_login_ip = info[0][4].split(';')[0]

            if status[0][0] == -1:
                return 3

            '''检测是否多次登录(防爆破)'''
            if try_to_login_ip == ip:
                self.add_user_status(user)

                if status[0][0] > 5:
                    last_login_time = status[0][1]

                    if (now - last_login_time).total_seconds() <= 600:
                        return 2
                    else:
                        self.set_user_status(user, 1)
                else:
                    c.execute(
                        f"update chat_2024.users set status_update_time='{now.strftime(ISOTIMEFORMAT)}' where user='{user}'")

            c.execute(f"select password from chat_2024.users where user='{user}'")
            passwd = c.fetchall()[0]

            if passwd[0] == password:
                c.execute(
                    f"update chat_2024.users set status_update_time='{now.strftime(ISOTIMEFORMAT)}' where user='{user}'")
                self.record_last_login_ip(user, ip)
                self.set_user_status(user, 1)
                return 0  # 0表示登录成功

            return 1  # 1表示密码错误

        except AttributeError:
            print('AttributeError')
            return -1
        except IndexError:
            return -1  # -1表示账号异常

    def get_user(self, user):
        c = self.conn.cursor()
        c.execute(
            f"select user, password, name, last_login_ip, try_to_login_ip from chat_2024.users where user='{user}'")
        r = c.fetchall()
        c.close()
        return r

    def add_user_status(self, user):
        c = self.conn.cursor()
        c.execute(f"UPDATE chat_2024.users AS u1 SET u1.status = u1.status + 1 WHERE u1.user = '{user}'")
        c.close()
        return 1

    def set_user_status(self, user, status):
        c = self.conn.cursor()
        c.execute(f"UPDATE chat_2024.users SET status={status} WHERE user = '{user}'")
        c.close()
        return 1

    def get_user_status(self, user):
        c = self.conn.cursor()
        c.execute(f"select status, status_update_time from chat_2024.users where user='{user}'")
        c.close()
        r = c.fetchall()
        return r

    def record_try_login_ip(self, user, ip):
        c = self.conn.cursor()
        c.execute(
            f"update chat_2024.users as u set u.try_to_login_ip = concat('{ip};', u.try_to_login_ip) where u.user='{user}'")
        c.close()
        return 1

    def record_last_login_ip(self, user, ip):
        c = self.conn.cursor()
        c.execute(f"update chat_2024.users set last_login_ip='{ip};' where user='{user}'")
        c.close()
        return 1


def sign_out(s, nickname):
    while 1:
        try:
            r = s.recv(2048)
            if not r:
                print(1)
            r = eval(r.decode())
            if r["type"] == 'exit' or not r:
                break
        except:
            break
    s.close()
    curtime = datetime.now().strftime(ISOTIMEFORMAT)  # 获取当前时间
    print(curtime)
    print(f'用户 {nickname} 退出登录')
    with open('../serverlog.txt', 'a+') as serverlog:  # log记录
        serverlog.write(f'{curtime} {nickname} 退出登录\n')

def main():
    global addr
    print("服务端启动成功!")
    while True:  # 不断接受新的套接字进来，实现“多人”
        try:
            conn_socket, addr = s.accept()  # 获取套接字与此套接字的地址
            login_info = eval(conn_socket.recv(4096).decode())
            if login_info['type'] == 'login':
                fail_to_login = sql.login(
                    login_info['data']['user'],
                    login_info['data']['passwd']
                )
                login_status = {
                    "type": "login_status",
                    "code": fail_to_login
                }
                conn_socket.send(f'{login_status}'.encode())
                if not fail_to_login:  # 登录成功后
                    socket_list.append(conn_socket)  # 套接字列表更新
                    nickname = sql.get_user(login_info['data']['user'])[0][2]

                    user_list.append(nickname)  # 用户列表更新，加入新用户（新的套接字）
                    curtime = datetime.now().strftime(ISOTIMEFORMAT)
                    print(curtime)
                    print(f'用户 {nickname} 登录成功')
                    print(f'登录IP：{addr[0]}')
                    print('')

                    with open('../serverlog.txt', 'a+') as serverlog:  # log记录
                        serverlog.write(f'{curtime} {nickname} 登录\n')

                    # 加入线程中跑，加入函数为socket_target，参数为conn_socket,nickname
                    threading.Thread(target=sign_out, args=(conn_socket, nickname,)).start()

        except:
            pass


@atexit.register  # 意外退出处理(防数据丢失)
def clean():
    del sql


if __name__ == '__main__':

    # 聊天记录存储至当前目录下的serverlog.txt文件中
    try:
        with open('../serverlog.txt', 'a+') as serverlog:
            curtime = datetime.now().strftime(ISOTIMEFORMAT)
            serverlog.write('\n\n-----------服务器打开时间：' + str(curtime) + '，开始记录聊天-----------\n')
    except:
        print('ERROR!')

    # 读取套接字连接
    s = socket()
    s.bind((SOCK_IP, SOCK_PORT))
    s.listen()

    sql = SQL()  # 启动数据库
    # PASSWD = input("请输入开服密码：")  # 开服密码不再是端口（密码设置为端口会导致密码重复（大规模时）以及位数限定（端口数量有限））
    threading.Thread(target=main).start()
