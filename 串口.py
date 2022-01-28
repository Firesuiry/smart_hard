import serial, re  # 导入模块
# import serial.tools.list_ports
import threading, binascii, codecs, time
from binascii import unhexlify
import struct

ser = None
msg_buffer_ls = []
msg_buffer = b''


class Controller:
    def __init__(self, portx="COM3"):
        print('上位机初始化')
        global ser
        portx = "COM3"
        bps = 115200
        timex = 5
        self.ser = serial.Serial(portx, bps, timeout=timex)
        print('串口打开状态:', self.ser.is_open)
        print(self.ser)
        self.thread = threading.Thread(target=self.recv_data, args=(self.ser,))
        self.thread.start()

    def __del__(self):
        self.ser.close()
        self.thread.join()

    def recv_data(self, ser):
        global msg_buffer_ls
        while True:
            data_len = ser.in_waiting
            if data_len > 0:
                data = ser.read(data_len)
                print(data)
                msg_buffer_ls.append(data)
                self.msg_process()

    def msg_process(self):
        global msg_buffer_ls, msg_buffer
        while len(msg_buffer_ls) > 0:
            msg = msg_buffer_ls.pop(0)
            msg_buffer += msg
        print('buffer:',msg_buffer)
        while b'\r\n' in msg_buffer:
            msgs = msg_buffer.split(b'\r\n')
            single_msg = msgs[0]
            self.single_msg_process(single_msg)
            msg_buffer = msg_buffer[len(msgs[0]) + 2:]
            # print('单条信息内容：', single_msg)

    @staticmethod
    def get_str_from_hex_byte(data):
        return ''.join(['\\x%X' % b for b in data])
        pass

    def single_msg_process(self, msg):
        print('single_msg_process:', msg)
        if B'up:' not in msg:
            print('single_msg_process,return')
            return
        msg = msg.split(B'up:')[1]
        addr = self.get_str_from_hex_byte(msg[0:2])
        msg_info = msg[2:]
        print(f'信息来自：{addr}内容：{msg_info}原始信息：{self.get_str_from_hex_byte(msg)}')
        if msg_info[:3] == B'ADC':
            adc_index = int(msg_info[3:4])

    def send_command(self, addr, cmd):
        cmd = addr + cmd + b'\r\n'
        print('发送命令:', cmd)
        self.ser.write(cmd)

    @staticmethod
    def decode(data):
        ans_str = ''
        # print(data,len(data))
        data = str.lower(data.decode('ASCII'))
        for i in range(int(len(data) / 4)):
            single_hex_str = data[4 * i:4 * i + 4]
            single_char = chr(int(single_hex_str, 16))
            ans_str += single_char
        print('解码结果:', ans_str)
        return ans_str


if __name__ == '__main__':
    c = Controller("COM3")
    c.send_command(b'\x00\x00', b'\x01')
