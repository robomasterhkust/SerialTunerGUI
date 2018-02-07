import struct as st
import serial as sp
import params as p
import time   as t

class serialPort:
    #private
    _ser = []
    _connected = False
    _changed = False
    _version = []

    rxBuffer = ()
    paramName = []
    subParamName = []

    param_count = 0
    _subparam_count = 0
    _private_flag = []

    _mode = 1 # 0:CHIBIOS USB mode
              # 1:CHIBIOS UART mode

    #public
    portName = ''

    def __init__(self,version):
        self._connected = False
        self._changed = False
        self._version = version

    def checkConnection(self):
        self._changed = False
        return self._connected

    def checkConnectionChange(self):
        return self._changed

    def connect(self):
        try:
            self._ser = sp.Serial(self.portName, 115200, timeout=0.5)
        except:
            print 'E:Cannot find port '+ self.portName
            return

        print 'Connected to '+self._ser.name
        self._connected = True
        self._changed = True

    def disconnect(self):
        self._ser.close()
        del self._ser
        self._connected = False
        self._changed = True

    def sendScale(self, index, sub_index, power):
        #byte = st.pack('i',power)
        data = chr(ord('0') + power)
        if self._mode == 0:
            self._ser.write('\r')
            t.sleep(0.05)
        param_index = chr(ord('0')+index)
        subparam_index = chr(ord('0')+sub_index)
        self._ser.write('\xFD '+ param_index + subparam_index)
        self._ser.write(data)
        self._ser.write('-------\r')
        #print 's '+str(index)+' '+str(sub_index)+' '+str(power)

    def sendUpdateCommand(self):
        if self._mode == 0:
            self._ser.write('\r')
            t.sleep(0.05)
        self._ser.write('\xFB update----\r')
        t.sleep(1)
        print 'parameters saved'

    def sendParam(self, value, index, sub_index):
        data = hex(st.unpack('I',(st.pack('f',value)))[0])[2:]
        #convert floating point number to hex value , then to a character string
        #E.g. 3.141592653 -> 0x40490fdb -> '40490fdb' -> '40490?=;'
        while len(data) < 8:
            data = '0'+ data

        if self._mode == 0:
            self._ser.write('\r')
            t.sleep(0.05)
        param_index = chr(ord('0')+index)
        subparam_index = chr(ord('0')+sub_index)
        self._ser.write('\xF9 '+ param_index + subparam_index)
        self._ser.write(data)
        self._ser.write('\r')
        #print 'p '+str(index)+' '+str(sub_index)+' '+data

    def clearRxBuffer(self):
        del self.paramName[:]
        del self.subParamName[:]
        paramName = []
        subParamName = []
        self.rxBuffer = ()

    def reset(self):
        del self._private_flag[:]
        self._private_flag = []

        self.param_count = 0
        self._subparam_count = 0
        self.clearRxBuffer()

    def getParam(self, params):
        #TODO:getParameters
        self.reset()

        self._ser.write('\r-----------\r') #flush the shell serial port
        t.sleep(0.05)
        self._ser.write('\xFA getPID----\r')

        t.sleep(0.05)
        self._ser.reset_input_buffer()

        byte1 =  self._ser.read(1)
        if len(byte1) == 0:
            print 'E:Unable to retrieve parameters from board 1!'
            return False;

        byte2 =  self._ser.read(1)
        byte_private = self._ser.read(4)
        byte_mode = self._ser.read(1)

        self._mode = (st.unpack('B',byte_mode))[0]
        if self._mode == 0:
            print 'Device in USB mode'
        elif self._mode == 1:
            print 'Device in UART mode'
        else:
            print 'E:Unsupported connection mode!'

        ver = self._ser.readline().split('.')
        ver[len(ver)-1]=ver[len(ver)-1][0:len(ver[len(ver)-1])-1]

        ver_min = self._version.split('.')
        ver_num_min = 0
        for i in range(0,3):
            if i < len(ver_min):
                ver_num_min += int(ver_min[i])
            ver_num_min *= 1000

        ver_num = 0
        try:
            for i in range(0,3):
                if i < len(ver):
                    ver_num += int(ver[i])
                ver_num *= 1000
        except ValueError:
            print 'E:Your on-board param driver appeared to be obsolete, namely param.c and param.h'
            print 'Please download the latest param driver from Github, and reload your embedded program'
            return False

        if ver_num < ver_num_min:
            print 'E:Your on-board param driver appeared to be obsolete, namely param.c and param.h'
            print 'Please download the latest param driver from Github, and reload your embedded program'
            return False

        private = st.unpack('I',byte_private)[0]

        for i in range(0,32):
            self._private_flag.append((private & pow(2,i) > 0))

        self.param_count = (st.unpack('B',byte1))[0]
        self._subparam_count = (st.unpack('B',byte2))[0]

        print 'Retrieved '+str(self.param_count)+' parameters and ' +\
            str(self._subparam_count)+' sub-parameters'

        byteSubparams =  self._ser.read(self.param_count * 9)
        for byte in byteSubparams:
            self.rxBuffer = self.rxBuffer + st.unpack('b',byte)
        param_count = 0;

        for i in range(0, self.param_count):
            #print 'Param '+ str(i)+' has '+ str(self.rxBuffer[9*i])+ ' subparams'
            for j in range(0, self.rxBuffer[9*i]):
                byteparams = self._ser.read(4)
                self.rxBuffer = self.rxBuffer + st.unpack('f',byteparams)
            param_count += self.rxBuffer[9*i]

        for i in range(0, self.param_count):
            p = str(self._ser.readline())
            subp = str(self._ser.readline())
            if p[0] == '*':
                print 'W:unknown parameter name at position '+str(i)
                p = 'Controller '+str(i)
            p = p[0:len(p)-1]
            self.paramName.append(p)
            print self.paramName[i]

            self.subParamName.append(subp.split())
            if len(self.subParamName[i]) != self.rxBuffer[9*i]:
                print 'W:incorrect subparameter name at position '+str(i)
                self.subParamName[i] = []
                for j in range(0, self.rxBuffer[9*i]):
                    self.subParamName[i].append('p'+str(j))


        self._ser.flush()
        if len(byteSubparams) != self.param_count*9 or param_count != self._subparam_count:
            print 'E:GODDAMNIT!!Fucking incorrect parameters on board!'
            return False;

        return True
