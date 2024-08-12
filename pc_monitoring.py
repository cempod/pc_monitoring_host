import clr
import time
import serial
import serial.tools.list_ports
import os

hwtypes = ['Mainboard','SuperIO','CPU','RAM','GpuNvidia','GpuAti','TBalancer','Heatmaster','HDD']
cpu_t = 0
gpu_t = 0
cpu_l = 0
gpu_l = 0

def initialize_openhardwaremonitor():
    clr.AddReference(os.path.abspath('OpenHardwareMonitorLib.dll'))

    from OpenHardwareMonitor import Hardware

    handle = Hardware.Computer()
    handle.CPUEnabled = True
    handle.RAMEnabled = True
    handle.GPUEnabled = True
    handle.Open()
    return handle

def fetch_stats(handle):
    for i in handle.Hardware:
        i.Update()
        for sensor in i.Sensors:
            parse_sensor(sensor)
        for j in i.SubHardware:
            j.Update()
            for subsensor in j.Sensors:
                parse_sensor(subsensor)

def parse_sensor(sensor):
    global cpu_t
    global cpu_l
    global gpu_t
    global gpu_l
    if sensor.Value:
        if str(sensor.SensorType) == 'Temperature':
            if(str(sensor.Name) == "CPU Package"):
                cpu_t = round(sensor.Value)
                #print("CPU Temperature:"+str(sensor.Value))
            if(str(sensor.Name) == "GPU Hot Spot"):
                gpu_t = round(sensor.Value)
                #print("GPU Temperature:"+str(sensor.Value))
        if str(sensor.SensorType) == 'Load':
            if(str(sensor.Name) == "GPU Core"):
                gpu_l = round(sensor.Value)
                #print("GPU Core Load:"+str(sensor.Value))
            if(str(sensor.Name) == "CPU Total"):
                cpu_l = round(sensor.Value)
                #print("CPU Load:"+str(sensor.Value))



if __name__ == "__main__":
    while(1):
        for port in serial.tools.list_ports.comports():
            print(port.device)
            try:
                ser = serial.Serial(port.device, baudrate=115200,timeout=1)
                if(ser.write(b"PCMACS")):
                    print("Written")
                else:
                    print("Can't write")
                if(ser.read(2)==b"OK"):
                    print("Connected")
                    HardwareHandle = initialize_openhardwaremonitor()
                    while(1):
                        fetch_stats(HardwareHandle)
                        print("CPU Temperature:"+str(cpu_t))
                        print("GPU Temperature:"+str(gpu_t))
                        print("CPU Load:"+str(cpu_l))
                        print("GPU Load:"+str(gpu_l))
                        ser.write(bytearray([cpu_t,gpu_t,cpu_l,gpu_l]))
                        time.sleep(1)
                else:
                    print("Can't read")
                    ser.close()
            except Exception:
                print("Disconnected")
                time.sleep(5)
        time.sleep(5)