import serial
import time
import re
import os
from Tkinter import *

class Window(Frame):
    """A GUI with basic settings and commands."""
   
    def __init__(self, master):
        """Initialise the Frame"""
        Frame.__init__(self,master)
        self.grid()
        self.create_widgets()
        
    def create_widgets(self):
        """Create widgets for basic control"""
        
        # Button1 - extract and convert to CSV
        self.button1 = Button(self, relief = GROOVE, width = 15, pady = 5, padx = 2)
        self.button1["text"] = "2. Convert to CSV"
        self.button1["command"] = convert_csv
        self.button1.grid(row = 2, column = 4, columnspan = 1, sticky = E)
        
        # Button2 - deletes the logged data from the GM80
        self.button2 = Button(self, relief = GROOVE, width = 15, pady = 5, padx = 2)
        self.button2["text"] = "3. Delete Data"
        self.button2["command"] = self.delete_confirmation
        self.button2.grid(row = 3, column = 4, sticky = E)
        
        # Text Box - prints out useful information
        self.text = Text(self, width = 32, height = 15, wrap = WORD)
        self.text.grid(row = 1, column = 0, columnspan = 3, rowspan = 3, sticky = E)
        
        # Dropdown1 - Baudrates
        optionList1 = [2400,4800,9600,19200,38400,115200]
        self.var1 = IntVar()
        self.var1.set(optionList1[2])
        self.dropdown1 = OptionMenu(self, self.var1, *optionList1)
        self.dropdown1.grid(row = 5, column = 1, sticky = W)
        
        # Labels for Baudrate & console
        Label(self, text="Console:").grid(row = 0, column = 0, sticky = W)
        Label(self, text="Set Baudrate:").grid(row = 5, column = 0, sticky = W)
        Label(self,text="").grid(row = 4, column = 0, columnspan = 2)
        Label(self,text="  ").grid(row = 1, column = 3, rowspan = 3)
        
        # Button5 - Initialise the device
        self.button5 = Button(self, relief = GROOVE, width = 15, pady = 5, padx = 2)
        self.button5["text"] = "1. Initialise"
        self.button5["command"] = lambda: refresh_device(self.var1.get())
        self.button5.grid(row = 1, column = 4, sticky = E)
        
        # Button6 - Refresh the device (reiniitialise)
        self.button6 = Button(self, relief = GROOVE)
        self.button6["text"] = "Refresh"
        self.button6["command"] = lambda: refresh_device(self.var1.get())
        self.button6.grid(row = 5, column = 2, sticky = N, pady = 4, padx = 2)
        
        
    def delete_confirmation(self):
        """Create a confirmation window"""
        
        # Initializes the new window
        self.top = Toplevel()
        self.top.overrideredirect(False)
        self.top.grid()
        self.top.title("Warning...")
        self.top.geometry("250x90+450+450")
        self.msg = Message(self.top, text = "Make sure the GM80 is in Measuring Mode?\n", width = 250)
        self.msg.grid(row = 0, column = 0, columnspan = 2)
        
        # Button3 - cancels deletion
        self.button3 = Button(self.top, width = 10)
        self.button3["text"] = "Cancel"
        self.button3["command"] = self.top.destroy
        self.button3.grid(row = 1, column = 0, columnspan = 1)
        
        # Button4 - deletes logged data in GM80
        self.button4 = Button(self.top, width = 10)
        self.button4["text"] = "OK"
        self.button4["command"] = lambda: self.delete_command(self.top)
        self.button4.grid(row = 1, column = 1)
        
    def delete_command(self, top):
        top.destroy()
        command('B')
        
    def update_text(self, text_input):
        """Update information text box"""
        self.text.insert(15.0, "%s\n" % text_input)
        
    def delete_text(self):
        """Delete information from text box"""
        self.text.delete(0.0, END)    
        
def refresh_device(baudrate):
    """Initialises the correct settings for the device"""
    
    global ser
    global app
    
    app.delete_text()
    app.update_text("initilising...\n")
    app.update_idletasks()
    
    #Checks whether ser is False or object
    if ser == False:
        pass
    else:
        ser.close()
    # does serial port need flishing?
    p = 0
    port = 'COM0'
    while p < 9: 
        try:
            ser = serial.Serial(
            port=port,\
            baudrate=baudrate,\
            parity=serial.PARITY_NONE,\
            stopbits=serial.STOPBITS_ONE,\
            bytesize=serial.EIGHTBITS,\
            timeout=0)
            break
        except (serial.SerialException, AttributeError):
            app.update_text("%s - no connection" % port)
            app.update_idletasks()
            p += 1
            port = 'COM' + str(p)
            
    
    time.sleep(1)
    
    if not ser:
        app.update_text("\nopen COM port not found!\n")
    elif ser.isOpen():
        app.update_text("\nconnected to: %s" % ser.portstr)
        app.update_text("baudrate: %d \n" % baudrate)
                         
                        
    else:
        app.update_text("\nerror occured!\n")
    
def command(cmd):
    """Sends the appropiate command to the device"""  
    
    global app
    global ser
    
    app.delete_text()
    app.update_text("attempting to send command to device...\n")
    app.update_idletasks()
    
    if not ser:
        time.sleep(0.5)
        app.update_text("no connection")
        return False
    elif ser.isOpen():
        app.update_text("port is open...\n")
        ser.write(cmd + '\r\n')
        time.sleep(1)
    else:
        app.update_text("error occured!")
        return False
        
    # returns data from Logger
    output = ""
    if cmd == 'A':
        while ser.inWaiting() > 0:
            output += str(ser.readline())
        return output
        
    if cmd == 'B':
        app.update_text("command sent!\n\n"
                        "please check by attempting to Convert to CSV\n")
        
    else:
        print "failed"
            
def convert_csv():
    """Sends 'A' to GM80 and converts results to CSV"""
     
    global app
    global ser
     
    out = command('A')
    
    if not out:
        app.update_text("error occured: no data\n")
        return
    
    app.update_text("extracting data...\n")

    # Extacts and reformats the data into lists
    act_time = []
    load = []
    extracted_data = re.findall(r'(-?\d{2},\d{2})\s{2}kN\s(\d{2}:\d{2}:\d{2})', out)
    for i in extracted_data:
        load.append(i[0].replace(",", "."))
        act_time.append(i[1])
    
    # Checks for data
    if len(load) == 0:
        app.update_text("error occured: no data\n")
        return
        
    # create's appropiate file name and path
    date_label = time.strftime("GM80_%j%Y_%H%M%S")
    path = os.path.expanduser('~') + '\\DESKTOP\\'
    
    # Checks to ensure file can be saved to desktop
    # otherwise saved to current directory
    try:
        op = open('%s%s.csv' % (path,date_label), 'a+')
    except IOError:
        op = open('%s.csv' % date_label, 'a+')
        path = ''
    
    # Appropiately writes the extracted data to created CSV
    op.write("Time, Load\n")
    i = 0
    while i < len(load):
        op.write('%s,%s\n' % (act_time[i], load[i]))
        i += 1
    op.close()
    
    # Writes original data format to txt - backup
    op = open('%s%s.txt' % (path,date_label), 'a+')
    op.write(out)
            
    app.update_text("data extracted:\n"
                    "check Desktop for files\n")        
         
'''Initialization and global variables''' 
root = Tk()
root.title("GM80 Logger")
root.geometry("400x330+400+400")

app = Window(root)
ser = False

root.mainloop()
