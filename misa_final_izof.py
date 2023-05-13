import serial
import json
import tkinter as tk
import tkinter.font as tkfont
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.style as mplstyle
import paho.mqtt.client as mqtt

mplstyle.use('ggplot')
ser = serial.Serial('COM11', 115200)
distance_values = []


broker_address = "demo.thingsboard.io"
access_token = "Vqj6QODQLXlQeSwKhrrh"
broker_port = 1883


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
    else:
        print(f"Connection failed with error code {rc}")

def on_publish(client, userdata, mid):
    print("Data published successfully")

client = mqtt.Client()
client.username_pw_set(access_token)
client.on_connect = on_connect
client.on_publish = on_publish
client.connect(broker_address, broker_port)
topic = "v1/devices/me/telemetry"

def read_serial():
    while True:
        if ser.in_waiting > 0:
            data = ser.readline().decode('utf-8').rstrip()
            try:
                json_data = json.loads(data)

                temperature = json_data.get('t')
                humidity = json_data.get('h')
                distance = json_data.get('d')

                text_temperature.config(text=f'{temperature} °C')
                text_humidity.config(text=f'{humidity} %')
                text_distance.config(text=f'{distance} cm')

                distance_values.append(distance)
                update_distance_graph()
                client.publish(topic,  json.dumps(json_data, separators=(',', ':')))
                
            except json.JSONDecodeError:
                print("Data: ", data)
                pass

def send_command(command):
    ser.write(command.encode())

def handle_beep():
    global beep_count
    if beep_count % 2 == 0:
        send_command("beepStart")
        button_beep.config(text="Beep End")
    else:
        send_command("beepEnd")
        button_beep.config(text="Beep Start")
    beep_count += 1

def handle_record():
    global record_count
    if record_count % 2 == 0:
        send_command("recordStart")
        button_record.config(text="Record End")
    else:
        send_command("recordEnd")
        button_record.config(text="Record Start")
    record_count += 1

def update_distance_graph():
    distance_graph.clear()
    distance_graph.plot(distance_values, 'b-')
    distance_graph.set_xlabel('Time')
    distance_graph.set_ylabel('Distance (cm)')
    distance_canvas.draw()

root = tk.Tk()
root.title("Serial Data Reader")
root.geometry("520x500")
root.resizable(False, False)

# Custom font for the 8-segment display
display_font = tkfont.Font(family="Seven Segment", size=20, weight="normal")

# Distance display
text_distance = tk.Label(root, text='-- cm', font=tkfont.Font(family="Seven Segment", size=40, weight="bold"))
text_distance.grid(row=0, column=0, columnspan=2)

# Temperature display
text_temperature = tk.Label(root, text='-- °C', font=display_font, padx=20, pady=20)
text_temperature.grid(row=1, column=0)

# Humidity display
text_humidity = tk.Label(root, text='-- %', font=display_font, padx=20, pady=20)
text_humidity.grid(row=1, column=1)

# Beep button
beep_count = 0
button_beep = tk.Button(root, text="Beep Start", command=handle_beep)
button_beep.grid(row=2, column=0, pady=10, padx=10)

# Record button
record_count = 0
button_record = tk.Button(root, text="Record Start", command=handle_record)
button_record.grid(row=2, column=1, pady=10, padx=10)

# Distance graph
figure = Figure(figsize=(5, 3), dpi=100)
distance_graph = figure.add_subplot(111)
distance_canvas = FigureCanvasTkAgg(figure, master=root)
distance_canvas.get_tk_widget().grid(row=3, column=0, columnspan=2, padx=10, pady=10)

import threading
t = threading.Thread(target=read_serial)
t.daemon = True
t.start()

root.mainloop()