import threading
import atexit
import pymysql

from datetime import *
from socket import *

# 时间格式声明，用于后面的记录系统时间
ISOTIMEFORMAT = '%Y-%m-%d %H:%M:%S'

# 设置IP地址和端口号
SOCK_IP = '127.0.0.1'
SOCK_PORT = 4444

# 用户列表和套接字列表，用于后面给每个套接字发送信息
user_list = []
socket_list = []


# 数据库
class SQL:
    # 设置数据库信息
    SQL_IP = '202.182.125.24'
    SQL_PORT = 12942
    SQL_USERNAME = 'chat_2024'
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
            c.execute(f"insert chat_2024.users(user, name, password,try_to_login_ip) values('{user}', '{name}', '{password}', '');")
            c.close()
            return 1
        except:
            return 0

    def delete(self, user):
        c = self.conn.cursor()
        c.execute(f"delete from chat_2024.users where user='{user}'")
        c.close()
        return 1

    def logout(self, user, password):
        c = self.conn.cursor()
        c.execute(f"delete from chat_2024.users where user='{user}' and password='{password}'")
        c.close()
        return 1

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


class Control:
    def help(self, options):
        print("------------------------------StarChat帮助文档-------------------------------")
        print('h/help                                                        ----打开帮助文档')
        print('list                                                             ----在线人数')
        print('search [-u 用户名] [-n 昵称]                            ----查询在线用户的更多信息')
        print('tick -u 用户名                                       ----强制一个在线用户退出登录')
        print('register -u 用户名 -p 密码 -n 昵称                                ----注册新用户')
        print('delete -u 用户名                                               ----删除某一用户')
        print('--------------------------------更多请咨询RIYI--------------------------------')
        print('---------------------------------官方网站：未定---------------------------------')
        print('---------------------------联系邮箱：starbot@126.com---------------------------')
        print('-------------------------------感谢支持StarChat-------------------------------')

    def h(self, options=None):
        self.help(options)

    def list(self, options):
        if not user_list:
            print("没有在线的用户QWQ....")
        else:
            print("用户  昵称  上次登录IP")
            for u in user_list:
                info = sql.get_user(u)
                print(info[0][0], info[0][2], info[0][3])

    def tick(self, options):
        for option in options:
            if option.get("-u"):
                nickname = option["-u"]
                try:
                    s.close()
                    user_list.remove(nickname)
                    curtime = datetime.now().strftime(ISOTIMEFORMAT)  # 获取当前时间
                    print()
                    print(curtime)
                    print(f'用户 {nickname} 退出登录')
                    with open('../serverlog.txt', 'a+') as serverlog:  # log记录
                        serverlog.write(f'{curtime} {nickname} 退出登录\n')
                    return 1
                except ValueError:
                    print(f"用户{nickname}不在线")
                    return 0
        print("错误：[-u]是必须选项")

    def search(self, options):
        for option in options:
            try:
                if option.get("-u"):
                    nickname = option["-u"]
                    info = sql.get_user(nickname)
                    print("用户  昵称  上次登录IP")
                    print(info[0][0], info[0][2], info[0][3])
                    return 1
                elif option.get("-n"):
                    nickname = option["-n"]
                    for u in user_list:
                        info = sql.get_user(u)
                        if info[0][2] == nickname:
                            print("用户  昵称  上次登录IP")
                            print(info[0][0], info[0][2], info[0][3])
                            return 1
                    raise IndexError()
                else:
                    print("错误：[-u]或[-n]是必须选项")
                    return 0
            except IndexError:
                print(f"用户{nickname}不在线")
        return 0

    def register(self, options):
        if not options:
            print("错误：[-u][-p][-n]是必须选项")
            return 0

        for option in options:
            try:
                if option.get("-u"):
                    user = option.get("-u")
                if option.get("-p"):
                    passwd = option.get("-p")
                if option.get("-n"):
                    name = option.get("-n")
            except KeyError:
                continue
        if sql.register(user, passwd, name):
            print(f"新用户{user}注册成功，密码：{passwd}")
            return 1
        else:
            print(f"注册失败")
            return 0

    def delete(self, options):
        for option in options:
            try:
                if option.get("-u"):
                    user = option["-u"]
                    reply = input(f"真的要删除用户{user}吗(y确定，其他键取消)")
                    if reply == 'y' or reply == 'Y':
                        sql.delete(user)
                        print(f"成功删除用户{user}")
                    else:
                        print("成功取消操作")
                        return 0
                else:
                    print("错误：[-u]是必须选项")
                    return 0
            except IndexError:
                print("操作异常，请重试")
        return 0
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
    try:
        s.close()
        user_list.remove(nickname)
    except ValueError:
        pass
    curtime = datetime.now().strftime(ISOTIMEFORMAT)  # 获取当前时间
    print()
    print(curtime)
    print(f'用户 {nickname} 退出登录')
    with open('../serverlog.txt', 'a+') as serverlog:  # log记录
        serverlog.write(f'{curtime} {nickname} 退出登录\n')


def control():
    while 1:
        controls = input('\n').split(' ')
        control = controls[0]
        options = []
        i = 1
        try:
            while i <= len(controls):
                arg = controls[i]
                if arg[0] == '-':
                    option = {f"{arg}": f"{controls[i + 1]}"}
                    options.append(option)
                    i += 1
                else:
                    options.append(arg)
                i += 1
        except IndexError:
            pass
        try:
            eval(f"Control().{control}({options})")
        except AttributeError:
            pass
        except SyntaxError:
            print("未知命令")


def main():
    global addr
    print("服务端启动成功!")
    Control().h()
    while True:  # 不断接受新的套接字进来，实现“多人”
        try:
            conn_socket, addr = s.accept()  # 获取套接字与此套接字的地址
            login_info = conn_socket.recv(4096)

            login_info = eval(login_info.decode())
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
                    nickname = sql.get_user(login_info['data']['user'])[0][0]

                    user_list.append(nickname)  # 用户列表更新，加入新用户（新的套接字）
                    curtime = datetime.now().strftime(ISOTIMEFORMAT)
                    print('')
                    print(curtime)
                    print(f'用户 {nickname} 登录成功')
                    print(f'登录IP：{addr[0]}')

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

    threading.Thread(target=control).start()
    threading.Thread(target=main).start()
