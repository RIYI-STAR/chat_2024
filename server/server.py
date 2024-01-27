
def read_client(s, nickname):
    try:
        return s.recv(4096).decode('utf-8')  # 获取此套接字（用户）发送的消息
    except:  # 一旦断开连接则记录log以及向其他套接字发送相关信息
        curtime = datetime.now().strftime(ISOTIMEFORMAT)  # 获取当前时间
        print(curtime)
        print(nickname + ' 离开了聊天室!')
        with open('../serverlog.txt', 'a+') as serverlog:  # log记录
            serverlog.write(str(curtime) + '  ' + nickname + ' 离开了聊天室!\n')
        socket_list.remove(s)
        user_list.remove(nickname)
        for client in socket_list:  # 其他套接字通知（即通知其他聊天窗口）
            client.send(('系统消息：' + nickname + ' 离开了聊天室!').encode('utf-8'))


def socket_target(s, nickname):
    try:
        s.send((','.join(user_list)).encode('utf-8'))  # 将用户列表送给各个套接字，用逗号隔开
        while True:
            content = read_client(s, nickname)  # 获取用户发送的消息
            if content is None:
                break
            else:
                curtime = datetime.now().strftime(ISOTIMEFORMAT)  # 系统时间打印
                print(curtime)
                print(nickname + ' ：' + content)
                with open('../serverlog.txt', 'a+') as serverlog:  # log记录
                    serverlog.write(str(curtime) + '  ' + nickname + ' ：' + content + '\n')
                for client in socket_list:  # 其他套接字通知
                    client.send((nickname + ' ：' + content).encode('utf-8'))
    except:
        print('Error!')

