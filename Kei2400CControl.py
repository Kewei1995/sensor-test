import visa
import time
import warnings

class keithley2400c:
    def __init__(self):
        instlist=visa.ResourceManager()
        print(instlist.list_resources())
        #self.kei2400c=instlist.open_resource("GPIB0::24::INSTR")
        self.kei2400c=instlist.open_resource("ASRL1::INSTR")
        self.timedelay=0.5
        self.cmpl='105E-6' # global current protection

    def testIO(self):
        message=self.kei2400c.query('*IDN?')
        print(message)

    def set_current_protection(self,current):
        self.cmpl=str(current)

    def set_voltage(self,vol):
        #if vol > 2.0:
		#    warnings.warn("Warning High Voltage!!!!")

        self.kei2400c.write(":sense:current:protection "+self.cmpl)
        self.kei2400c.write(":source:function voltage")
        self.kei2400c.write(":source:voltage:mode fixed")
        vols=self.show_voltage()
        self.sweep(vols,vol,1)
        vols=self.show_voltage()
        return vols

    def show_voltage(self):
        self.kei2400c.write(":source:voltage:mode fixed")
        self.kei2400c.write(":form:elem voltage")
        voltage=self.kei2400c.query(":read?")
        print("voltage [V]:  " + str(voltage))
        return float(str(voltage))

    def sweep(self, vols, vole, step):
        if vols < vole:
            self.sweep_forward(vols,vole,step)
        else:
            self.sweep_backward(vols,vole,step)

    def sweep_forward(self, vols, vole, step):
        # Conveter from V to mV
        mvols=vols*1000
        mvole=vole*1000
        mstep=step*1000

        for mvol in range(int(mvols),int(mvole),int(mstep)):
            vol=mvol/1000 # mV -> V
            self.kei2400c.write(":source:voltage:level "+str(vol))
            self.kei2400c.write(":sense:current:protection "+self.cmpl)
            self.show_voltage()
            time.sleep(self.timedelay)

        self.kei2400c.write(":source:voltage:level "+str(vole))
        self.show_voltage()

    def sweep_backward(self, vols, vole, step):
        # Conveter from V to mV
        mvols=vols*1000
        mvole=vole*1000
        mstep=step*1000

        for mvol in range(int(mvols),int(mvole), -int(mstep)):
            vol=mvol/1000 # mV -> V
            self.kei2400c.write(":source:voltage:level "+str(vol))
            self.kei2400c.write(":sense:current:protection "+self.cmpl)
            self.show_voltage()
            time.sleep(self.timedelay*0.2)

        self.kei2400c.write(":source:voltage:level "+str(vole))
        self.show_voltage()

    def display_current(self):
        self.kei2400c.write(":sense:function 'current'")
        self.kei2400c.write(":sense:current:range "+self.cmpl)
        self.kei2400c.write(":display:enable on")
        self.kei2400c.write(":display:digits 7")
        self.kei2400c.write(":form:elem current")
        current=self.kei2400c.query(":read?")
        print("current [A]:  " + str(current))

        time.sleep(self.timedelay)
        self.kei2400c.write(":form:elem current")
        current=self.kei2400c.query(":read?")
        return float(str(current))

    def hit_compliance(self):
        tripped=int(str(self.kei2400c.query(":SENSE:CURRENT:PROTECTION:TRIPPED?")))
        if tripped:
            print("Hit the compliance "+self.cmpl+"A.")
        return tripped

    def output_on(self):
        self.kei2400c.write(":output on")
        print("On")

    def output_off(self):
        self.kei2400c.write(":output off")
        print("Off")


if __name__=="__main__":
    kei2400c=keithley2400c()
    kei2400c.output_on()
    kei2400c.set_voltage(1)
    current=kei2400c.display_current()
    print(current)
    kei2400c.output_off()

