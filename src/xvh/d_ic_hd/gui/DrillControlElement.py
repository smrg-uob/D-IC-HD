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
        # position tracker
        self.position = 0.000
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
        self.txt_status = tk.Text(master=self.frm_controls, width=8, height=1)
        self.set_connection_status('Disconnected')
        self.lbl_status.grid(row=0, column=col_1, columnspan=span_1, sticky=tk.W, padx=3, pady=1)
        self.txt_status.grid(row=0, column=col_2, columnspan=span_2, sticky=(tk.W, tk.E), padx=3, pady=1)
        # add com port selection box and connection button
        self.lbl_com_ports = tk.Label(master=self.frm_controls, text="COM Port")
        ports, port_names = get_com_ports()
        self.port_names = port_names
        self.com_port_value = tk.StringVar()
        if len(ports) > 0:
            self.com_port_value.set(ports[0])
        self.cbx_com_ports = ttk.Combobox(master=self.frm_controls, state='readonly', textvariable=self.com_port_value)
        self.cbx_com_ports.bind("<<ComboboxSelected>>", self.com_port_selected)
        self.cbx_com_ports["values"] = ports
        self.connect_value = tk.StringVar()
        self.connect_value.set("Connect")
        self.btn_connect = tk.Button(master=self.frm_controls, textvariable=self.connect_value, command=self.connect_button_pressed)
        self.lbl_com_ports.grid(row=1, column=col_1, columnspan=span_1, sticky=tk.W, padx=3, pady=1)
        self.cbx_com_ports.grid(row=1, column=col_2, columnspan=4, sticky=tk.W, padx=3, pady=1)
        self.btn_connect.grid(row=1, column=col_2 + 4, columnspan=4, sticky=(tk.W, tk.E), padx=3, pady=1)
        # Add controls label
        self.lbl_controls = tk.Label(master=self.frm_controls, text="Controls")
        self.lbl_controls.grid(row=2, column=col_1, columnspan=span_1, sticky=tk.W, padx=3, pady=1)
        # Add depth indicator and zero button
        self.lbl_position = tk.Label(master=self.frm_controls, text='Position')
        self.txt_position = tk.Text(master=self.frm_controls, width=8, height=1)
        self.update_position_field()
        self.zero_pos_value = tk.StringVar()
        self.zero_pos_value.set("Zero")
        self.btn_zero_pos = tk.Button(master=self.frm_controls, textvariable=self.zero_pos_value, command=self.zero_button_pressed)
        self.lbl_position.grid(row=3, column=col_1, columnspan=span_1, sticky=tk.W, padx=3, pady=1)
        self.txt_position.grid(row=3, column=col_2, columnspan=4, sticky=(tk.W, tk.E), padx=3, pady=1)
        self.btn_zero_pos.grid(row=3, column=col_2 + 4, columnspan=4, sticky=(tk.W, tk.E), padx=3, pady=1)

    def connection_update_loop(self):
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
            self.parent.after(1, self.connection_update_loop)
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
        # No operations needed
        pass

    def connect_button_pressed(self):
        # get target port
        target_port = self.get_com_port()
        if target_port is None:
            # log error and return
            self.log('Can not connect to a motor as there are no available ports.')
            return
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
        self.parent.after(1, self.connection_update_loop)

    def zero_button_pressed(self):
        # reset the position to zero
        self.position = 0.000
        # update the position field
        self.update_position_field()

    def get_com_port(self):
        if len(self.port_names) <= 0:
            return None
        index = self.cbx_com_ports.current()
        if 0 <= index < len(self.port_names):
            return self.port_names[index]
        else:
            return self.port_names[0]

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

    def update_position_field(self):
        # determine current depth as string
        new_pos = ('%.3f' % self.position) + ' mm'
        # get the current depth
        current = self.txt_position.get("1.0", "end-1c")
        # if the current and new position are the same, no update needed
        if current == new_pos:
            return
        # enable the text box
        self.txt_position.configure(state="normal")
        # delete the previous value
        self.txt_position.delete("1.0", "end-1c")
        # set the new value
        self.txt_position.insert(Tk.END, new_pos)
        # disable the text box again
        self.txt_position.configure(state="disabled")

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

    def on_close(self):
        if self.mc is not None:
            self.mc.stop_connection()
            self.mc = None


def get_com_ports():
    port_info_list = sc.list_serial_ports()
    ports = []
    port_names = []
    for port_info in port_info_list:
        port_names.append(port_info.name)
        ports.append(port_info.name + ' - ' + port_info.description)
    return ports, port_names
