# coding=utf-8
import Tkinter as Tk
import ttk
from xvh.d_ic_hd.stepper_control import stepper_control as sc


class DrillControlElement:
    def __init__(self, tk, parent, logger, title_font_type, title_font_size):
        # Set the parent
        self.parent = parent
        self.parent.pack_propagate(False)
        # set the logging method
        self.logger = logger
        # motor controller
        self.mc = None
        # command flag
        self.command_flag = False
        # Title
        self.lbl_drill_control = tk.Label(master=self.parent, text='Drill Depth Control',
                                          font=(title_font_type, title_font_size))
        self.lbl_drill_control.grid(row=0, column=0, sticky="w", pady=2)
        # Add controls frame
        self.frm_controls = tk.Frame(master=self.parent)
        self.frm_controls.grid(row=1, column=0, sticky="nesw",)
        for col in range(0, 120):
            self.frm_controls.grid_columnconfigure(col, weight=1)
        col_1 = 1
        span_1 = 9
        col_2 = span_1 + col_1 + 4
        span_2 = 8
        # add status field
        self.lbl_status = tk.Label(master=self.frm_controls, text="Status")
        self.lbl_status.grid(row=0, column=col_1, columnspan=span_1, sticky=tk.W, padx=3, pady=1)
        self.status_value = tk.StringVar()
        self.txt_status = tk.Text(master=self.frm_controls, width=8, height=1)
        self.txt_status.grid(row=0, column=col_2, columnspan=span_2, sticky=(tk.W, tk.E), padx=3, pady=1)
        self.txt_status.configure(state="disabled")
        self.set_connection_status('Disconnected')
        # add com port selection box and connection button
        self.lbl_com_ports = tk.Label(master=self.frm_controls, text="COM Port")
        self.com_port_value = tk.StringVar()
        self.com_port_value.set('COM1')
        self.cbx_com_ports = ttk.Combobox(master=self.frm_controls, state='readonly', textvariable=self.com_port_value)
        self.cbx_com_ports.bind("<<ComboboxSelected>>", self.com_port_selected)
        self.cbx_com_ports["values"] = get_com_ports()
        self.lbl_com_ports.grid(row=1, column=col_1, columnspan=span_1, sticky=tk.W, padx=3, pady=1)
        self.cbx_com_ports.grid(row=1, column=col_2, columnspan=4, sticky=tk.W, padx=3, pady=1)
        self.connect_value = tk.StringVar()
        self.connect_value.set("Connect")
        self.btn_connect = tk.Button(master=self.frm_controls, textvariable=self.connect_value, command=self.connect_button_pressed)
        self.btn_connect.grid(row=1, column=col_2 + 4, columnspan=4, sticky=(tk.W, tk.E), padx=3, pady=1)
        # Add controls label
        self.lbl_controls = tk.Label(master=self.frm_controls, text="Controls")
        self.lbl_controls.grid(row=2, column=col_1, columnspan=span_1, sticky=tk.W, padx=3, pady=1)

    def update_connection(self):
        if self.mc is None:
            # no motor connection, update the status
            self.set_connection_status('Disconnected')
            # enable the widgets
            self.toggle_control_widgets(True)
            # log
            self.log('Disconnected from motor')
            # stop looping
            return
        # there is a motor connection
        if self.mc.is_valid():
            # set the status
            self.set_connection_status('Connected')
            # log
            self.log('Connected to motor on port ' + self.get_com_port())
            # stop looping
            return
        if self.mc.is_validating():
            # update the status
            self.set_connection_status('Connecting')
            # loop
            self.parent.after(1, self.update_connection)
        else:
            # motor connection timed out: update the status
            self.set_connection_status('Disconnected')
            # reset the motor, no need to log as the motor controller will log
            self.mc = None
            # enable the widgets
            self.toggle_control_widgets(True)
            # stop looping,
            return

    def com_port_selected(self, event=None):
        pass    # TODO

    def connect_button_pressed(self):
        # get target port
        target_port = self.get_com_port()
        # check if there is currently a connection
        if self.mc is not None:
            # get the port
            motor_port = self.mc.get_port()
            if motor_port == target_port:
                # same port
                if self.mc.is_valid_or_validating():
                    # already connected, do nothing
                    return
                else:
                    # try connecting again
                    self.mc.start_connection()
            # disconnect from the previous motor
            self.mc.stop_connection()
            self.set_connection_status('Disconnected')
            self.mc = None
        # Create new motor controller
        self.mc = sc.create_motor_controller(target_port, 5, self.log)
        # Log
        self.log('Attempting connection with motor on port ' + target_port)
        # Try connecting to it
        self.mc.start_connection()
        # Update the status
        self.set_connection_status('Connecting')
        # set the command flag
        self.command_flag = True
        # disable the control widgets
        self.toggle_control_widgets(False)
        # Launch event loop
        self.parent.after(1, self.update_connection)

    def get_com_port(self):
        return self.com_port_value.get()

    def get_connection_status(self):
        return self.txt_status.get("1.0", "end-1c")

    def set_connection_status(self, status):
        # get the current status
        current = self.get_connection_status()
        # if there is no change, return
        if current == status:
            return
        # enable the text box
        self.txt_status.configure(state="normal")
        # delete the previous status
        self.txt_status.delete("1.0", "end-1c")
        # set the new text
        self.txt_status.insert(Tk.END, status)
        # disable the text box again
        self.txt_status.configure(state="disabled")

    def toggle_control_widgets(self, status):
        if status:
            state = "normal"
        else:
            state = "disabled"
        self.cbx_com_ports.configure(state=state)
        self.btn_connect.configure(state=state)
        self.cbx_com_ports.configure(state=state)

    def log(self, line):
        self.logger("Motor Control: " + line)


def get_com_ports():
    port_info_list = sc.list_serial_ports()
    ports = []
    for port_info in port_info_list:
        ports.append(port_info.name)
    return ports
