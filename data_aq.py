import smbus2 as smbus
import csv
import time
from statistics import mean
from statistics import pstdev
from datetime import datetime as dt
import numpy as np

# Global variables

# Activates the automatic data post-processing:
trig=1

# Number of axes and accelerometer:
n_acc = 4
axes = 2
tot_ax = n_acc * axes

# Principal axis (of the slope trigger):
ax_princ = 'Az_2'

# Accelerometers and I2C busses definition (fino a 4 accelerometri):
mpu1 = mpu6050(0x68)
mpu2 = mpu6050(0x69)
mpu3 = mpu6050(0x68, bus=4)
mpu4 = mpu6050(0x69, bus=4)

# Standard ranges
ACCEL_RANGE_2G = 0x00
ACCEL_RANGE_4G = 0x08

fs = ACCEL_RANGE_2G      # Acceleration range set

dlpf = 3                # Low-pass filter parameter (refer to datasheets of mpu60x0)

### Low-pass filter settings:

#         Accel         Gyro
#DLPF_CFG Hz  Delay(ms) Hz   Delay(ms)   Fs(kHz)
#0        260 0         256  0.98        8
#1        184 2.0       188  1.9         1
#2        94  3.0       98   2.8         1
#3        44  4.9       42   4.8         1
#4        21  8.5       20   8.3         1
#5        10  13.8      10   13.4        1
#6        5   19.0      5    18.6        1

# Accelerometer Class:

class mpu6050:

    GRAVITIY_MS2 = 9.80665
    address = None
    bus = None

    ACCEL_SCALE_MODIFIER_2G = 16384.0
    ACCEL_SCALE_MODIFIER_4G = 8192.0

    ACCEL_RANGE_2G = 0x00
    ACCEL_RANGE_4G = 0x08

    PWR_MGMT_1 = 0x6B
    PWR_MGMT_2 = 0x6C

    ACCEL_XOUT0 = 0x3B
    # ACCEL_YOUT0 = 0x3D
    ACCEL_ZOUT0 = 0x3F

    ACCEL_CONFIG = 0x1C
    DLPF_CONFIG = 0x1A
    
    # I2C methods:

    def __init__(self, address, bus=1):
        self.address = address
        self.bus = smbus.SMBus(bus)
        self.bus.write_byte_data(self.address, self.PWR_MGMT_1, 0x00)

    # Bit-banging I2C:

    def read_i2c_word(self, register):
        high = self.bus.read_byte_data(self.address, register)
        low = self.bus.read_byte_data(self.address, register + 1)

        value = (high << 8) + low

        if value >= 0x8000:
            return -((65535 - value) + 1)
        else:
            return value
            
    # Range setting   
    
    def set_accel_range(self, accel_range):
        self.bus.write_byte_data(self.address, self.ACCEL_CONFIG, 0x00)
        self.bus.write_byte_data(self.address, self.ACCEL_CONFIG, accel_range)
        
    # Digital low-pass filter setting

    def set_dlpf(self, dlpf=0):
        self.bus.write_byte_data(self.address, self.DLPF_CONFIG, 0)
        self.bus.write_byte_data(self.address, self.DLPF_CONFIG, dlpf)
        
    # Range reading

    def read_accel_range(self, raw=False):
        raw_data = self.bus.read_byte_data(self.address, self.ACCEL_CONFIG)

        if raw is True:
            return raw_data
        elif raw is False:
            if raw_data == self.ACCEL_RANGE_2G:
                return 2
            elif raw_data == self.ACCEL_RANGE_4G:
                return 4
            elif raw_data == self.ACCEL_RANGE_8G:
                return 8
            elif raw_data == self.ACCEL_RANGE_16G:
                return 16
            else:
                return -1
                
    # Range reading at +-2g:

    def get_accel_data_2g(self, g=False):
        x = self.read_i2c_word(self.ACCEL_XOUT0)/ self.ACCEL_SCALE_MODIFIER_2G
        # y = self.read_i2c_word(self.ACCEL_YOUT0)/ self.ACCEL_SCALE_MODIFIER_2G
        z = self.read_i2c_word(self.ACCEL_ZOUT0)/ self.ACCEL_SCALE_MODIFIER_2G

        if g is True:
            #return [x, y, z]
            return [x, z]
        elif g is False:
            x = x * self.GRAVITIY_MS2
            # y = y * self.GRAVITIY_MS2
            z = z * self.GRAVITIY_MS2
            # return [x, y, z]
            return [x, z]
            
    # Range reading +-4g:

    def get_accel_data_4g(self, g=False):
        x = self.read_i2c_word(self.ACCEL_XOUT0)/ self.ACCEL_SCALE_MODIFIER_4G
        # y = self.read_i2c_word(self.ACCEL_YOUT0)/ self.ACCEL_SCALE_MODIFIER_4G
        z = self.read_i2c_word(self.ACCEL_ZOUT0)/ self.ACCEL_SCALE_MODIFIER_4G

        if g is True:
            #return [x, y, z]
            return [x, z]
        elif g is False:
            x = x * self.GRAVITIY_MS2
            # y = y * self.GRAVITIY_MS2
            z = z * self.GRAVITIY_MS2
            # return [x, y, z]
            return [x, z]

# --------- End of class mpu6050 -----------

# User request function:

def yes_or_no(domanda):
    check = str(input(domanda)).lower().strip()
    try:
        if check[:1] == 'y':
            return True
        elif check[:1] == '':
            return True
        elif check[:1] == 'n':
            return False
        else:
            print('\n Invalid input \n')
            return yes_or_no(domanda)
    except Exception as error:
        print("\n Error! Invalid input, please insert a valid value. (Y/n): \n")
        print(error)
        return yes_or_no(domanda)

print("\n Acceleration range \n")

mpu1.set_accel_range(fs)
mpu2.set_accel_range(fs)
mpu3.set_accel_range(fs)
mpu4.set_accel_range(fs)

print(" Register 0x1C bus.1 add.68: ", mpu1.read_accel_range(raw = False), "g")
print(" Register 0x1C bus.1 add.69: ", mpu2.read_accel_range(raw = False), "g")
print(" Register 0x1C bus.4 add.68: ", mpu3.read_accel_range(raw = False), "g")
print(" Register 0x1C bus.4 add.69: ", mpu4.read_accel_range(raw = False), "g")

print("\n Digital Low Pass Filter setup (please, refer tab DLPF_CFG pag.13 of the file MPU-6000-Register-map1.pdf). \n")

mpu1.set_dlpf(dlpf)
mpu2.set_dlpf(dlpf)
mpu3.set_dlpf(dlpf)
mpu4.set_dlpf(dlpf)

print(" Register 0x1A bus.1 add.68: ", mpu1.bus.read_byte_data(0x68, mpu1.DLPF_CONFIG))
print(" Register 0x1A bus.1 add.69: ", mpu2.bus.read_byte_data(0x69, mpu2.DLPF_CONFIG))
print(" Register 0x1A bus.4 add.68: ", mpu3.bus.read_byte_data(0x68, mpu3.DLPF_CONFIG))
print(" Register 0x1A bus.4 add.69: ", mpu4.bus.read_byte_data(0x69, mpu4.DLPF_CONFIG))

# Sampling frequency:
samp = 0.005 #[s])

### Calibration:

# Parameters:
i_c = 0
i_max_c = 12000

# Rounding parameters:
a = 5
b = 4
c = 2

# Calibrazion arrays:
x_1 = []
z_1 = []

x_2 = []
z_2 = []

x_3 = []
z_3 = []

x_4 = []
z_4 = []

# Gravity:
# g = GRAVITIY_MS2
g=0 # Z offset to zero

# Mean values initialization:

avg_1_x = 0
avg_1_z = 0

avg_2_x = 0
avg_2_z = 0

avg_3_x = 0
avg_3_z = 0

avg_4_x = 0
avg_4_z = 0

domanda1 = str("\n Do you want to start the calibration? (Y,n): ")

if yes_or_no(domanda1):
    print("\n Calibration started: ", dt.now().strftime('%H-%M-%S'))
    start1 = time.time()

    for i_c in range(i_max_c):

        start = time.time()

        accel_data_1 = mpu1.get_accel_data_2g()
        accel_data_2 = mpu2.get_accel_data_2g()
        accel_data_3 = mpu3.get_accel_data_2g()
        accel_data_4 = mpu4.get_accel_data_2g()

    ### acc_1

        x_1.append(accel_data_1[0])
        z_1.append(accel_data_1[1])


    ### acc_2

        x_2.append(accel_data_2[0])
        z_2.append(accel_data_2[1])


    ### acc_3

        x_3.append(accel_data_3[0])
        z_3.append(accel_data_3[1])


    ### acc_4

        x_4.append(accel_data_4[0])
        z_4.append(accel_data_4[1])

        # Sleeptime to mantain a constant sample rate:
        time.sleep(samp - (time.time() % samp))
        

    # Time elapsed during the calibration cycle:
    print("\n Calibration completed: ", time.time() - start1, " s")

    ### acc_1


    avg_1_x = round(mean(x_1), c)
    avg_1_z = round(mean(z_1), c)

    print("\n\n Accelerometer 1:\n\n Mean value X_1: ", avg_1_x)
    print(" Mean value Z_1: ", avg_1_z)

    print("\n Offsets, X_1: ", avg_1_x, "\tZ_1: ", round(avg_1_z-g, c))

    dev_x_1 = round(pstdev(x_1), a)
    dev_z_1 = round(pstdev(z_1), a)

    print( "\n Standard deviation, X_1: ", dev_x_1, "\tZ_1: ", dev_z_1)


    ### acc_2


    avg_2_x = round(mean(x_2), c)
    avg_2_z = round(mean(z_2), c)

    print("\n\n Accelerometer 2:\n\n Mean value X_2: ", avg_2_x)
    print(" Mean value Z_2: ", avg_2_z)

    print("\n Offsets: X_2: ", avg_2_x, "\tZ_2: ", round(avg_2_z-g, c))

    dev_x_2 = round(pstdev(x_2), a)
    dev_z_2 = round(pstdev(z_2), a)

    print( "\n Standard deviation, X_2: ", dev_x_2, "\tZ_2: ", dev_z_2)

    ### acc_3


    avg_3_x = round(mean(x_3), c)
    avg_3_z = round(mean(z_3), c)

    print("\n\n Accelerometer 3:\n\n Mean value X_3: ", avg_3_x)
    print(" Mean value Z_3: ", avg_3_z)

    print("\n Offsets, X_3: ", avg_3_x, "\tZ_3: ", round(avg_3_z-g, c))

    dev_x_3 = round(pstdev(x_3), a)
    dev_z_3 = round(pstdev(z_3), a)

    print( "\n Standard deviation, X_3: ", dev_x_3, "\tZ_3: ", dev_z_3)

    ### acc_4


    avg_4_x = round(mean(x_4), c)
    avg_4_z = round(mean(z_4), c)

    print("\n\n Accelerometer 4:\n\n Mean value X_4: ", avg_4_x)
    print(" Mean value Z_4: ", avg_4_z)


    print("\n Offsets: X_4: ", avg_4_x, "\tZ_4: ", round(avg_4_z-g, c))

    dev_x_4 = round(pstdev(x_4), a)
    dev_z_4 = round(pstdev(z_4), a)


    print( "\n Standard deviation, X_4: ", dev_x_4, "\tZ_4: ", dev_z_4)

    print("\n Calibration completed: ", dt.now().strftime('%H-%M-%S'),"\n\n")
    
    # Definition of the .csv calibration file:
    with open('calibration4.csv', 'w',  newline='') as CalibFile:
        writer = csv.writer(CalibFile, delimiter=';')

        # Column names into the .csv
        
        writer.writerow(["Acceleration axes", "Ax_1", "Az_1", "Ax_2", "Az_2", "Ax_3", "Az_3", "Ax_4", "Az_4"])
        
        
        avg = ['Mean value: ', avg_1_x, avg_1_z, avg_2_x, avg_2_z, avg_3_x, avg_3_z, avg_4_x, avg_4_z]
        writer.writerow(avg)
        
        dvst = ['Standard deviation: ', dev_x_1, dev_z_1, dev_x_2, dev_z_2, dev_x_3, dev_z_3, dev_x_4, dev_z_4]
        writer.writerow(dvst)

else:
    print("\n Stepping into data acquisition: \n")

### Data acquisition

domanda2 = str("Do you want to start data acquisition? (Y/n): ")

while yes_or_no(domanda2):

    data_inizio = dt.now().strftime('%Y-%m-%d-%H-%M-%S')
    nomefile = 'Acceleration_' + data_inizio + '.csv'

    # Cycle parameters:
    i = 0
    i_max = 600

    # Empty numpy array with predefined dimension
    getdata = np.empty([i_max,(axes*n_acc+n_acc)])

    # Data acquisition start time:
    print("\n Acquisition started: ", dt.now().strftime('%H-%M-%S'))

    start2 = time.time()

    for _ in range(i_max):

        accel_data_1 = mpu1.get_accel_data_2g()
        t_1 = time.time()

        accel_data_2 = mpu2.get_accel_data_2g()
        t_2 = time.time()

        accel_data_3 = mpu3.get_accel_data_2g()
        t_3 = time.time()

        accel_data_4 = mpu4.get_accel_data_2g()
        t_4 = time.time()

        getdata[_] = [t_1, accel_data_1[0], accel_data_1[1], 
                      t_2, accel_data_2[0], accel_data_2[1],
                      t_3, accel_data_3[0], accel_data_3[1],
                      t_4, accel_data_4[0], accel_data_4[1]
                      ]

        # Sleeptime to maintain a constant sample rate:
        time.sleep(samp - (time.time() % samp))

    # Data acquisition stop:
    print("\n Data acquisition completed: ", time.time() - start2, " s")
    print("\n\n Data acquisition completed, wait until the end of the post-processing operations: ", dt.now().strftime('%H-%M-%S'), "\n")
    
    ### Post-processing
    
    from pandas import read_csv as rd
    import plotly.graph_objects as go
    import plotly.io as pio
    from zipfile import ZipFile
    import graphic_plot
    
    # data rounding function:
    getdata = np.around(getdata, decimals=a)
    
    # saves the array into a .csv
    np.savetxt(nomefile, getdata, delimiter=";", header="t_1;Ax_1;Az_1;t_2;Ax_2;Az_2;t_3;Ax_3;Az_3;t_4;Ax_4;Az_4", comments='')
    
    # Import of the calibration values from the calibration .csv:
    cal = rd('/root/calibration4.csv', sep=';')

    avg_m = []
    q=1
    
    while q <= tot_ax:
        avg_m.append(cal.values[0][q])
        q+=1
    
    cal_1_x = round(avg_m[0], c)
    cal_1_z = round(avg_m[1]-g, c)
    cal_2_x = round(avg_m[2], c)
    cal_2_z = round(avg_m[3]-g, c)
    cal_3_x = round(avg_m[4], c)
    cal_3_z = round(avg_m[5]-g, c)
    cal_4_x = round(avg_m[6], c)
    cal_4_z = round(avg_m[7]-g, c)
    
    acc = rd(nomefile, sep=';' )

    ### Offset cancellation:
    
    # Time offset
    acc['t_1'] = acc['t_1']-start2
    acc['t_2'] = acc['t_2']-start2
    acc['t_3'] = acc['t_3']-start2        
    acc['t_4'] = acc['t_4']-start2
    
    # Acceleration offset:
    acc['Ax_1'] = acc['Ax_1']-cal_1_x
    acc['Ax_2'] = acc['Ax_2']-cal_2_x
    acc['Ax_3'] = acc['Ax_3']-cal_3_x
    acc['Ax_4'] = acc['Ax_4']-cal_4_x

    acc['Az_1'] = acc['Az_1']-cal_1_z
    acc['Az_2'] = acc['Az_2']-cal_2_z
    acc['Az_3'] = acc['Az_3']-cal_3_z
    acc['Az_4'] = acc['Az_4']-cal_4_z

    # export of the .csv:
    export_csv = acc.to_csv(nomefile, sep=';')
    
    # Jerk of the principal axis:
    jerk = np.gradient(acc[ax_princ], samp)
    
    # Reset of the plot layout
    pio.templates.default = "none"

    # Plot of the time domain acceleration:

    ax_1 = go.Scatter(
            x = acc.t_1,
            y = acc.Ax_1,
            name = "A1: x",
            #line = dict(color = 'olive'),
            opacity = 0.8)

    ax_2 = go.Scatter(
            x = acc.t_2,
            y = acc.Ax_2,
            name = "A2: x",
            #line = dict(color = 'darkorange'),
            opacity = 0.8)
            
    ax_3 = go.Scatter(
            x = acc.t_3,
            y = acc.Ax_3,
            name = "A3: x",
            #line = dict(color = 'darkorchid'),
            opacity = 0.8)
            
    ax_4 = go.Scatter(
            x = acc.t_4,
            y = acc.Ax_4,
            name = "A4: x",
            #line = dict(color = 'lightcoral'),
            opacity = 0.8)
            
    jerk_pr = go.Scatter(
            x = acc.t_1,
            y = jerk,
            customdata = np.arange(0, i_max, 1),
            name = "jerk z 1",
            #line = dict(color = 'muted blue'),
            hovertemplate="Time: %{x:.3f} s<br>" + "Sample: %{customdata:.1f} <br>" + "Jerk: %{y:.2f} m/s^3" + " <extra></extra>",
            opacity = 0.8)

    az_1 = go.Scatter(
            x = acc.t_1,
            y = acc.Az_1,
            name = "A1: z",
            #line = dict(color = 'darkviolet'),
            opacity = 0.8)

    az_2 = go.Scatter(
            x = acc.t_2,
            y = acc.Az_2,
            name = "A2: z",
            #line = dict(color = 'cyan'),
            opacity = 0.8)

    az_3 = go.Scatter(
            x = acc.t_3,
            y = acc.Az_3,
            name = "A3: z",
            #line = dict(color = 'peru'),
            opacity = 0.8)

    az_4 = go.Scatter(
            x = acc.t_4,
            y = acc.Az_4,
            name = "A4: z",
            #line = dict(color = 'turquoise'),
            opacity = 0.8)

    data = [ax_1, ax_2, ax_3, ax_4, jerk_pr, az_1, az_2, az_3, az_4]

    layout = dict(title = 'Display of the acelerations (time domain):')
    
    fig = go.Figure(data=data, layout=layout)
    
    fig.update_xaxes(title_text="Time [s]")
    fig.update_yaxes(title_text="Acceleration [m/s^2]; Jerk [m/s^3]")
    
    nomegraf = 'Time_Domain_Plot_' + data_inizio + '.html'
    pio.write_html(fig, file = nomegraf, auto_open = False)
    
        # Post-processing check
     
    if trig==1:
    
        '''
        Syntax example:
        
        plotinstance = plot_acc.PlotAcc(df=dataf, samp=0.005, t=200, jerk_perc=70, pre_tr=20, ax_princ='Ax_1')
        
        (dataframe, sampleperiod, number of iteration (time window), trigger trheshold (percentage),
         pre-trigger iteration, principal trigger axis)
        
        It's possible to define other instancies of the class named PlotAcc with differend parameters!
            
        Plot of the single axis, syntax example:
        
        plotinstance.plot( axis, g=9.81)
        '''
        
        plotrigger = plot_acc.PlotAcc(df=acc, samp=samp, t=100, jerk_perc=350, pre_tr=20, ax_princ=ax_princ)
        
        # Transient check:
        
        if plotrigger.triggcalc():
        
            ### Acc 1
            plotrigger.plot(axis='Ax_1')
            plotrigger.plot(axis='Az_1')
                            
            ### Acc 2       
            plotrigger.plot(axis='Ax_2')
            plotrigger.plot(axis='Az_2')
                            
            ### Acc 3       
            plotrigger.plot(axis='Ax_3')
            plotrigger.plot(axis='Az_3')
                            
            ### Acc 4       
            plotrigger.plot(axis='Ax_4')
            plotrigger.plot(axis='Az_4')


            # .zip folder creation:
            nomezip = 'acceldata_' + data_inizio + '.zip'
            zipfold = ZipFile(nomezip, 'w')

            zipfold.write(nomefile)
            zipfold.write(nomegraf)
            zipfold.write('trigger tab.html')
            zipfold.write('calibration4.csv')
            
            for o in range(n_acc):
                zipfold.write('acceleration tab Ax_' + str(o+1) + '.html')
                zipfold.write('acceleration tab Az_' + str(o+1) + '.html')
                zipfold.write('acceleration plot Ax_' + str(o+1) + '.html')
                zipfold.write('acceleration plot Az_' + str(o+1) + '.html')

            zipfold.close()


    print("\n Post-processing operations completed", dt.now().strftime('%H-%M-%S'), "\n")

print("\n Data acquisition completed with no errors. \n")
