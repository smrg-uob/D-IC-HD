# coding=utf-8

import Tkinter as Tk
import ttk
import tkFont
from xvh.d_ic_hd.stepper_control import stepper_control as sc
from xvh.d_ic_hd.util import input_validation


class DrillControlElement:
    def __init__(self, tk, parent, logger, title_font_type, title_font_size):
        # Set the parent
        self.parent = parent
        self.parent.pack_propagate(False)
        # set the logging method
        self.logger = logger
        # motor controller
        self.mc = None
        # movement properties
        self.lead = 0
        self.steps_for_rev = 0
        self.steps_for_inc = 0
        self.move_type_index = 0
        self.forwards = True
        # position trackers
        self.step_position = 0
        self.position = 0.000
        # Title
        self.lbl_position_control = tk.Label(master=self.parent, text='Drill Position Control',
                                             font=(title_font_type, title_font_size))
        self.lbl_position_control.grid(row=0, column=0, sticky="w", pady=2)
        # Add controls frame
        self.frm_controls = tk.Frame(master=self.parent)
        self.frm_controls.grid(row=1, column=0, sticky="nesw",)
        # column configuration
        row = 0
        span_1 = 5
        span_2 = 8
        span_3 = 3
        span_4 = 3
        span_5 = 4
        span_full = span_1 + span_2 + span_3 + span_4 + span_5
        col_1 = 0
        col_2 = col_1 + span_1
        col_3 = col_2 + span_2
        col_4 = col_3 + span_3
        col_5 = col_4 + span_4
        for col in range(0, col_5 + span_5):
            self.frm_controls.grid_columnconfigure(col, weight=1)
        # define the title font
        title_font = tkFont.Font(None, tkFont.nametofont("TkDefaultFont"))
        title_font.configure(underline=True)
        # add status field
        self.lbl_status = tk.Label(master=self.frm_controls, text="Status", font=title_font)

        self.txt_status = tk.Text(master=self.frm_controls, width=8, height=1)
        self.set_connection_status('Disconnected')
        self.lbl_status.grid(row=row, column=col_1, columnspan=span_full, sticky=tk.W, padx=3, pady=1)
        self.txt_status.grid(row=row + 1, column=col_1, columnspan=span_full, sticky=(tk.W, tk.E), padx=3, pady=1)
        row = row + 2
        # add com port selection box and connection button
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
        self.cbx_com_ports.grid(row=row, column=col_1, columnspan=span_1 + span_2 + span_3 + span_4, sticky=(tk.W, tk.E), padx=3, pady=1)
        self.btn_connect.grid(row=row, column=col_5, columnspan=span_5, sticky=None, padx=3, pady=1)
        row = row + 1
        # Add configuration controls
        self.lbl_configuration = tk.Label(master=self.frm_controls, text='Configuration', font=title_font)
        self.lbl_drive = tk.Label(master=self.frm_controls, text='Drive')
        self.lbl_lead = tk.Label(master=self.frm_controls, text='Lead')
        self.lbl_steps_per_rev = tk.Label(master=self.frm_controls, text='Steps/Revolution')
        self.lbl_mm_per_rev = tk.Label(master=self.frm_controls, text='mm/Revolution')
        self.lbl_configuration.grid(row=row, column=col_1, columnspan=span_full, sticky=tk.W, padx=3, pady=1)

        int_validation = (self.frm_controls.register(input_validation.validate_int_positive), '%P')
        float_validation = (self.frm_controls.register(input_validation.validate_float_positive), '%P')
        self.drive_value = tk.StringVar()
        self.drive_value.set('%.0f' % 6000)
        self.drive_value.trace_variable("w", self.update_movement_properties)
        self.lead_value = tk.StringVar()
        self.lead_value.set('%0.3f' % 2)
        self.lead_value.trace_variable("w", self.update_movement_properties)
        self.ety_drive = tk.Entry(master=self.frm_controls, width=3, textvariable=self.drive_value, validate='key', validatecommand=int_validation)
        self.ety_lead = tk.Entry(master=self.frm_controls, width=3, textvariable=self.lead_value, validate='key', validatecommand=float_validation)
        self.lbl_drive.grid(row=row + 1, column=col_1, columnspan=span_1 - 3, sticky=tk.W, padx=3, pady=1)
        self.lbl_lead.grid(row=row + 2, column=col_1, columnspan=span_1 - 3, sticky=tk.W, padx=3, pady=1)
        self.ety_drive.grid(row=row + 1, column=col_2 - 3, columnspan=span_2 + span_3, sticky=(tk.W, tk.E), padx=1, pady=1)
        self.ety_lead.grid(row=row + 2, column=col_2 - 3, columnspan=span_2 + span_3, sticky=(tk.W, tk.E), padx=1, pady=1)
        self.lbl_steps_per_rev.grid(row=row + 1, column=col_4, columnspan=span_4, sticky=tk.W, padx=1, pady=1)
        self.lbl_mm_per_rev.grid(row=row + 2, column=col_4, columnspan=span_4, sticky=tk.W, padx=1, pady=1)
        row = row + 3
        # Add depth indicator and zero button
        self.lbl_position = tk.Label(master=self.frm_controls, text='Position', font=title_font)
        self.txt_position = tk.Text(master=self.frm_controls, width=8, height=1)
        self.txt_step_pos = tk.Text(master=self.frm_controls, width=8, height=1)
        self.update_position_fields()
        self.zero_pos_value = tk.StringVar()
        self.zero_pos_value.set("Zero")
        self.btn_zero_pos = tk.Button(master=self.frm_controls, textvariable=self.zero_pos_value, command=self.zero_button_pressed)
        self.lbl_position.grid(row=row, column=col_1, columnspan=span_1, sticky=tk.W, padx=3, pady=1)
        self.txt_position.grid(row=row + 1, column=col_1, columnspan=span_1 + span_2 + span_3 + span_4, sticky=(tk.W, tk.E), padx=3, pady=1)
        self.txt_step_pos.grid(row=row + 2, column=col_1, columnspan=span_1 + span_2 + span_3 + span_4, sticky=(tk.W, tk.E), padx=3, pady=1)
        self.btn_zero_pos.grid(row=row + 1, column=col_5, rowspan=2, columnspan=span_5, sticky=(tk.N, tk.S, tk.W, tk.E), padx=3, pady=1)
        row = row + 3
        # Add movement controls
        self.lbl_move = tk.Label(master=self.frm_controls, text="Movement", font=title_font)
        self.cbx_move_type = None
        move_validation = (self.frm_controls.register(self.validate_movement_input), '%P')
        self.move_value = tk.StringVar()
        self.move_value.set(('%.3f' % self.position))
        self.ety_move = tk.Entry(master=self.frm_controls, width=3, textvariable=self.move_value, validate='key', validatecommand=move_validation)
        self.move_type_value = tk.StringVar()
        self.move_type_value.set('mm')
        self.cbx_move_type = ttk.Combobox(master=self.frm_controls, state='readonly', width=span_4 + span_5, textvariable=self.move_type_value)
        self.cbx_move_type.bind("<<ComboboxSelected>>", self.move_type_selected)
        self.cbx_move_type["values"] = ['mm', 'steps']
        self.rel_value = tk.StringVar()
        self.rel_value.set('Relative')
        self.abs_value = tk.StringVar()
        self.abs_value.set('Absolute')
        self.stop_value = tk.StringVar()
        self.stop_value.set('Stop')
        self.btn_move_rel = tk.Button(master=self.frm_controls, textvariable=self.rel_value, width=10, command=self.move_relative)
        self.btn_move_abs = tk.Button(master=self.frm_controls, textvariable=self.abs_value, width=10, command=self.move_absolute)
        self.btn_move_stop = tk.Button(master=self.frm_controls, textvariable=self.stop_value, width=10, command=self.stop)
        self.lbl_move.grid(row=row, column=col_1, columnspan=span_1, sticky=tk.W, padx=3, pady=1)
        self.ety_move.grid(row=row + 1, column=col_1, columnspan=span_1 + span_2 + span_3 + 4, sticky=(tk.W, tk.E), padx=3, pady=1)
        self.cbx_move_type.grid(row=row + 1, column=col_4 + 4, columnspan=span_4 + span_5, sticky=(tk.W, tk.E), padx=3, pady=1)
        self.btn_move_rel.grid(row=row + 2, column=0, columnspan=9, sticky=(tk.W, tk.E), padx=1, pady=1)
        self.btn_move_abs.grid(row=row + 2, column=10, columnspan=9, sticky=(tk.W, tk.E), padx=1, pady=1)
        self.btn_move_stop.grid(row=row + 2, column=20, columnspan=9, sticky=(tk.W, tk.E), padx=1, pady=1)
        # update the movement properties
        self.update_movement_properties()
        # toggle widgets
        self.toggle_connection_widgets(True)
        self.toggle_control_widgets(False)

    def connection_update_loop(self):
        if self.mc is None:
            # no motor connection, update the status
            self.set_connection_status('Disconnected')
            # toggle the widgets
            self.toggle_connection_widgets(True)
            self.toggle_control_widgets(False)
            # log
            self.log('Disconnected from motor')
            # stop looping
            return
        # there is a motor connection
        if self.mc.is_valid():
            # set the status
            self.set_connection_status('Connected')
            # toggle the widgets
            self.toggle_control_widgets(True)
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
            # toggle the widgets
            self.toggle_connection_widgets(True)
            self.toggle_control_widgets(False)
            # stop looping,
            return

    def motor_step_loop(self):
        if self.mc is None:
            # No motor connection, update the status
            self.set_connection_status('Disconnected')
            # toggle the widgets
            self.toggle_connection_widgets(True)
            self.toggle_control_widgets(False)
            # log
            self.log('Disconnected from motor, cancelling steps')
            # stop looping
            return
        if self.mc.is_valid():
            if self.mc.is_stepping():
                # The motor is still stepping, loop
                self.parent.after(1, self.motor_step_loop)
                return
            else:
                # the motor has finished stepping, update the step counter and position
                steps = self.mc.get_last_step_count()
                self.log('Finished stepping ' + str(steps) + ' steps')
                if self.forwards:
                    self.step_position = self.step_position + steps
                else:
                    self.step_position = self.step_position - steps
                self.position = (self.step_position*self.lead)/self.steps_for_rev
                self.update_position_fields()
                # toggle the widgets
                self.toggle_control_widgets(True)
                # stop looping
                return
        else:
            # motor connection timed out, update the status
            self.set_connection_status('Disconnected')
            # reset the motor
            self.mc = None
            # toggle the widgets
            self.toggle_connection_widgets(True)
            self.toggle_control_widgets(False)
            # log
            self.log('Motor timed out, cancelling steps')
            # stop looping,
            return

    def com_port_selected(self, event=None):
        # No operations needed
        pass

    def move_type_selected(self, event=None):
        # get the new index
        new_index = self.cbx_move_type.current()
        # if the index is the same, do nothing
        if new_index == self.move_type_index:
            return
        # get current movement value
        old_value = self.get_movement_value()
        if new_index == 0:
            # convert from steps to mm
            new_value = (old_value*self.lead)/self.steps_for_rev
        else:
            # convert from mm to steps
            new_value = int((old_value*self.steps_for_rev)/self.lead)
        # update the move type index
        self.move_type_index = new_index
        # set the new value
        self.move_value.set(str(new_value))

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
        # disable the control widgets
        self.toggle_connection_widgets(False)
        # Launch event loop
        self.parent.after(1, self.connection_update_loop)

    def zero_button_pressed(self):
        # reset the positions to zero
        self.position = 0.000
        self.step_position = 0
        # update the position field
        self.update_position_fields()

    def move_relative(self):
        move_type = self.move_type_index
        move_value = self.get_movement_value()
        if move_type == 0:
            # movement requested in millimeters: convert to steps
            self.step_relative(int((move_value*self.steps_for_rev)/self.lead))
        else:
            # movement requested in steps: simply forward
            self.step_relative(move_value)

    def move_absolute(self):
        move_type = self.move_type_index
        move_value = self.get_movement_value()
        if move_type == 0:
            # movement requested in millimeters: convert to steps
            self.step_absolute(int((move_value*self.steps_for_rev)/self.lead))
        else:
            # movement requested in steps: simply forward
            self.step_absolute(move_value)

    def step_relative(self, steps):
        # if zero steps are requested, do nothing
        if steps == 0:
            return
        # if there is no active motor, do nothing
        if self.mc is None or not self.mc.is_valid:
            self.log('Not connected to a motor, can not step')
        # set forwards flag
        self.forwards = steps > 0
        # check the step limit
        if steps > 32767:
            self.log('Can not step more than 32 767 steps at a time, limiting steps to 32 767')
            steps = 32767
        # perform the steps
        self.mc.do_steps(steps)
        # disable the control widgets
        self.toggle_control_widgets(False)
        # Launch event loop
        self.parent.after(1, self.motor_step_loop)

    def step_absolute(self, steps):
        # calculate the relative movement and forward
        self.step_relative(steps - self.step_position)

    def stop(self):
        if self.mc is not None and self.mc.is_stepping():
            self.mc.stop_stepping()

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

    def get_movement_value(self):
        string_val = self.move_value.get()
        if string_val is None or string_val == '' or len(string_val) == 0:
            return 0
        if self.move_type_index == 0:
            return float(string_val)
        else:
            return int(string_val)

    def on_motor_connected(self):
        self.toggle_control_widgets(True)

    def on_motor_disconnected(self):
        self.toggle_control_widgets(False)

    def update_position_fields(self):
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
        # determine current step position as string
        new_pos = ('%.0f' % self.step_position)
        if new_pos == 1:
            new_pos = new_pos + ' step'
        else:
            new_pos = new_pos + ' steps'
        # get the current step position
        current = self.txt_step_pos.get("1.0", "end-1c")
        # if the current and new position are the same, no update needed
        if current == new_pos:
            return
        # enable the text box
        self.txt_step_pos.configure(state="normal")
        # delete the previous value
        self.txt_step_pos.delete("1.0", "end-1c")
        # set the new value
        self.txt_step_pos.insert(Tk.END, new_pos)
        # disable the text box again
        self.txt_step_pos.configure(state="disabled")

    def update_movement_properties(self, *args):
        # lead
        lead_string = self.lead_value.get()
        if len(lead_string) > 0:
            self.lead = float(lead_string)
        # steps per revolution
        rev_string = self.drive_value.get()
        if len(rev_string) > 0:
            self.steps_for_rev = int(rev_string)

    def toggle_connection_widgets(self, status):
        if status:
            state = "normal"
        else:
            state = "disabled"
        self.cbx_com_ports.configure(state=state)
        self.btn_connect.configure(state=state)
        self.cbx_com_ports.configure(state=state)

    def toggle_control_widgets(self, status):
        if status:
            state = "normal"
        else:
            state = "disabled"
        self.ety_drive.configure(state=state)
        self.ety_lead.configure(state=state)
        self.btn_zero_pos.configure(state=state)
        self.ety_move.configure(state=state)
        self.cbx_move_type.configure(state=state)
        self.btn_move_rel.configure(state=state)
        self.btn_move_abs.configure(state=state)

    def validate_movement_input(self, val):
        if self.move_type_index == 0:
            return input_validation.validate_float(val)
        else:
            return input_validation.validate_int(val)

    def log(self, line):
        self.logger("Motor Control: " + line)

    def on_close(self):
        if self.mc is not None:
            self.mc.stop_stepping()
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
