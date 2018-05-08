import tkinter
import socket
import time  
import threading
import json
from PIL import Image, ImageTk
# monitor chatroom
class window:
    def __init__(self,root):
        super().__init__()
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__id = None
        self.__nickname = None
        '''''创建分区'''  
        f_msglist = tkinter.Frame(height = 300,width = 300) #创建<消息列表分区 >    
        f_msgsend = tkinter.Frame(height = 300,width = 300) #创建<发送消息分区 >  
        f_floor = tkinter.Frame(height = 100,width = 300)   #创建<按钮分区>  
        f_right = tkinter.Frame(height = 700,width = 100)   #创建<图片分区>  
  
        '''''创建控件'''  
        self.txt_msglist = tkinter.Text(f_msglist) #消息列表分区中创建文本控件  
        self.txt_msglist.tag_config('green',foreground = 'blue') #消息列表分区中创建标签  
        self.listbar = tkinter.Scrollbar(f_msglist) #设置滚动条
        self.txt_msgsend = tkinter.Text(f_msgsend) #发送消息分区中创建文本控件  
        self.txt_msgsend.bind('<KeyPress-Up>',self.msgsendEvent) #发送消息分区中，绑定‘UP’键与消息发送。
        '''''txt_right = Text(f_right) #图片显示分区创建文本控件'''  
        self.button_send = tkinter.Button(f_floor,text = 'Send（↑）',command = lambda : self.do_send(args=self.txt_msgsend.get('0.0',tkinter.END))) #按钮分区中创建按钮并绑定发送消息函数  
        self.button_login = tkinter.Button(f_floor,text = 'Login',command = lambda : self.do_login(args=self.txt_msgsend.get('0.0',tkinter.END))) #分区中创建登录按钮并绑定登录函数
        
        #photo = tkinter.PhotoImage(file = r'C:\Users\53073\Desktop\kejian\internet\test\background.gif') #GIF打开方式
        img = Image.open(r'C:\Users\53073\Desktop\kejian\internet\test\background.jpg')  # 非gif要用PIL模块的PhotoImage打开
        photo = ImageTk.PhotoImage(img)  # 非gif要用PIL模块的PhotoImage打开
        self.label = tkinter.Label(f_right,image = photo) #右侧分区中添加标签（绑定图片）  
        self.label.image = photo  
  
        '''''分区布局'''  
        f_msglist.grid(row = 0,column = 0 ) #消息列表分区  
        f_msgsend.grid(row = 1,column = 0)  #发送消息分区  
        f_floor.grid(row = 2,column = 0)    #按钮分区  
        f_right.grid(row = 0,column = 1,rowspan = 3) #图片显示分区  
        self.txt_msglist.grid()  #消息列表文本控件加载 
        self.txt_msglist.see(tkinter.END) #始终保持最新
        self.txt_msgsend.grid()  #消息发送文本控件加载  
        self.button_send.grid(row = 0,column = 0,sticky = tkinter.W)   #发送按钮控件加载  
        self.button_login.grid(row = 0,column = 1,sticky = tkinter.W) #取消按钮控件加载  
        #self.label.grid() #右侧分区加载标签控件(图片)，待调整大小
        #self.listbar.grid() #安滚动条，待搞
        self.txt_msglist.insert(tkinter.END,'欢迎来到网络创新第一队聊天室v1.1\n请在下框输入你的用户名并点击LOGIN登录\n','green') #默认欢迎语
    
    def msgsendEvent(self,event):  
        if event.keysym == 'Up':  
            self.do_send(args=self.txt_msgsend.get('0.0',tkinter.END))  

    def __receive_message_thread(self):
        """
        接受消息线程
        """
        while True:
            # noinspection PyBroadException
            try:
                buffer = self.__socket.recv(1024).decode()
                obj = json.loads(buffer)
                msg = str(obj['sender_nickname'])+ '(' + str(obj['sender_id']) + ')'+ '[' +time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())+ ']'+'\n'  
                self.txt_msglist.insert(tkinter.END,msg,'green') #添加时间  
                self.txt_msglist.insert(tkinter.END,obj['message']) #接受消息，添加文本到消息列表
            except Exception:
                self.txt_msglist.insert(tkinter.END,'[Client] 无法从服务器获取数据','green')

    def __send_message_thread(self, message):
        """
        发送消息线程
        :param message: 消息内容
        """
        self.__socket.send(json.dumps({
            'type': 'broadcast',
            'sender_id': self.__id,
            'message': message
        }).encode())

    def start(self):
        """
        启动客户端
        """
        self.__socket.connect(('192.168.1.105', 9999))
        root.mainloop()

    def do_login(self, args):
        """
        登录聊天室
        :param args: 参数
        """
        self.txt_msgsend.delete('0.0',tkinter.END) #清空发送消息  
        nickname = args.split(' ')[0]

        # 将昵称发送给服务器，获取用户id
        self.__socket.send(json.dumps({
            'type': 'login',
            'nickname': nickname
        }).encode())
        # 尝试接受数据
        # noinspection PyBroadException
        try:
            buffer = self.__socket.recv(1024).decode()
            obj = json.loads(buffer)
            if obj['id']:
                self.__nickname = nickname
                self.__id = obj['id']
                self.txt_msglist.insert(tkinter.END,'[Client] 成功登录到聊天室\n','green')

                # 开启子线程用于接受数据
                thread = threading.Thread(target=self.__receive_message_thread)
                thread.setDaemon(True)
                thread.start()
                self.button_login.grid_forget()
            else:
                self.txt_msglist.insert(tkinter.END,'[Client] 无法登录到聊天室','green')
        except Exception:
            self.txt_msglist.insert(tkinter.END,'[Client] 无法从服务器获取数据','green')

    def do_send(self, args):
        """
        发送消息
        :param args: 参数
        """
        message = args
        # 显示自己发送的消息
        # 注意：str(self.__nickname)后拼接字符串会自动换行，原因不明
        msg = str(self.__nickname) + '(' + str(self.__id) + ')' + '[' + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())+']'+'\n'  
        self.txt_msglist.insert(tkinter.END,msg,'green') #添加时间  
        self.txt_msglist.insert(tkinter.END,message) #获取发送消息，添加文本到消息列表  
        self.txt_msgsend.delete('0.0',tkinter.END) #清空发送消息 
        if message == "quit":
            client.close()
            mySocket.close()
            txt_msglist.insert(END,'谢谢使用！再见！\n','green')
            exit()
        # 开启子线程用于发送数据
        thread = threading.Thread(target=self.__send_message_thread, args=(message, ))
        thread.setDaemon(True)
        thread.start()

root=tkinter.Tk()
monitorchat=window(root)
monitorchat.start()
