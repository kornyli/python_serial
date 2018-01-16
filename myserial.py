import wx
import serial
import serial.tools.list_ports
import threading
import time

com=[]
port_list = list(serial.tools.list_ports.comports())
for i in range(0, len(port_list)):
    com .append(list(port_list[i])[0])


class ListBoxFrame(wx.Frame):
    global com

    def __init__(self):
      wx.Frame.__init__(self, None, -1, '串口助手',size = (800, 600))
      self.InitUI()
      self.ser = []  # 用于保存串口
      self.thread_ser = []


    def InitUI(self):
      self.panel = wx.Panel(self, -1)
      self.vbox = wx.BoxSizer(wx.VERTICAL)#垂直管理面板
      self.listBox = wx.CheckListBox(self.panel, -1, (1,1),(70, 200),com,wx.LB_SINGLE)#合并复选框和列表框
      self.s1= wx.StaticText(self.panel, -1, '串口选择',size=(20, 20))#静态文本标签
      self.s2 = wx.StaticText(self.panel, -1, '波特率', size=(20, 20))#静态文本标签
      self.baudratelist = ['300', '600', '1200', '2400', '4800', '9600', '19200', '38400'
          , '43000', '56000', '57600', '115200']
      self.baudratelistctr = wx.Choice(self.panel, -1 ,choices=self.baudratelist)#单选框（选择波特率）
      self.baudratelistctr.SetSelection(5)#默认选择第五个
      self.open = wx.ToggleButton(self.panel, -1, "打开",size=(50,30))#开关按钮

      self.Emptied = wx.Button(self.panel, -1, "清空接收",size=(70,30))
      self.send = wx.Button(self.panel, -1, "发送", size=(70, 30))
      self.receive_data=wx.TextCtrl(parent=self.panel, id=-1, size=(50,600), style=wx.TE_READONLY|wx.TE_MULTILINE)#不可编辑文本（用于接收）
      self.send_data = wx.TextCtrl(parent=self.panel, id=-1, size=(20, 100))  # 可编辑文本（用于发送）

      self.vbox.Add(self.s1,0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL,5)#添加控件到垂直面板中
      self.vbox.Add(self.listBox, 0,wx.ALL|wx.ALIGN_LEFT,5)
      self.vbox.Add(self.s2, 0, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL, 5)
      self.vbox.Add(self.baudratelistctr, 0, wx.ALL|wx.ALIGN_LEFT,5)
      self.vbox.Add(self.open, 0, wx.ALL | wx.ALIGN_LEFT, 5)

      self.vbox2 = wx.BoxSizer(wx.VERTICAL)  # 垂直管理面板
      self.vbox2.Add(self.receive_data, 1, wx.ALL |  wx.EXPAND, 5)
      self.vbox2.Add(self.Emptied, 0, wx.ALL |  wx.ALIGN_RIGHT, 10)
      self.vbox2.Add(self.send_data, 0.5, wx.ALL | wx.EXPAND, 5)
      self.vbox2.Add(self.send, 0, wx.ALL | wx.ALIGN_RIGHT, 10)

      self.hbox = wx.BoxSizer(wx.HORIZONTAL)  # 水平管理面板
      self.hbox.Add(self.vbox, 0, wx.ALL | wx.ALIGN_LEFT, 5)
      self.hbox.Add(self.vbox2, 1, wx.ALL | wx.ALIGN_LEFT, 5)

      self.listBox.SetSelection(3)
      self.panel.SetSizer(self.hbox)

      self.open.Bind(wx.EVT_TOGGLEBUTTON, self.open_envent)  #绑定打开按钮事件
      self.send.Bind(wx.EVT_BUTTON, self.send_envent)
    def choice_com(self):

        for i in range(0,self.listBox.GetCount()):  #获取列表框的长度
            if self.listBox.IsChecked(i) :
                try:
                    self.ser.append(serial.Serial(self.listBox.GetString(i), self.baudratelistctr.GetStringSelection()))#生成对应串口对象
                except:
                    wx.MessageBox('打开串口冲突！', 'error')
                    return None
                print(self.listBox.GetString(i))
        print(self.baudratelistctr.GetStringSelection())

    def receive(self,choice_com,index):

        try:
            n = choice_com.inWaiting()  #等待接收
        except:
            wx.MessageBox('接收错误！', 'error')
            return None
        if n != 0:
            str1 = choice_com.readline()
            self.receive_data.AppendText(str1)
            print(str(str1, 'utf8'))
        T=threading.Thread(target=self.receive, args=(choice_com, i))  #重新开启一个接收子线程，这种方法很占CPU资源，以后再改
        T.start()
    def send_envent(self,envent):
        value=self.send_data.GetValue()
        try:
            for i in range(0,len(self.ser)):
                n = self.ser[i].write(bytes(value, 'utf8'))
        except:
            wx.MessageBox('发送失败！', 'error')
            return None

    def open_envent(self,envent):

        state = envent.GetEventObject().GetValue()

        if state:
            envent.GetEventObject().SetLabel("关闭")
            self.choice_com()
            for i in range(0,len(self.ser)) :
                self.thread_ser.append(threading.Thread(target=self.receive,args=(self.ser[i],i)))

            for j in range(len( self.thread_ser)):
                self.thread_ser[j].start()

        else:
            for i in range(0,len(self.ser)) :
               self.ser[i].close()
               #self.thread_ser[i].cancel()
               self.ser[i].__del__()
            self.ser = []
            self.thread_ser=[]
            envent.GetEventObject().SetLabel("打开")



if __name__ == '__main__':

    app = wx.PySimpleApp()
    ListBoxFrame().Show()

    app.MainLoop()