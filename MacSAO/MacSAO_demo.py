# MacSAO_demo.py
# MIT License
# See https://github.com/MakeItHackin/Supercon_8_2024_Badge_Hack for more information.


'''
MacSAO Demo Script for Supercon 8 Badge
Conference Details:

Event: Supercon 8
Location: Pasadena, CA
Dates: November 1-3, 2024
Organizer: Hackaday
Authors: MakeItHackin, CodeAllNight, Danner
Project Overview: This script is designed for the Raspberry Pi Pico Wireless used in the Supercon 8 conference badge. The badge features six Simple Add-On (SAO) ports that provide power, I2C communication, and GPIO pins. This demo integrates six SAOs, including the MacSAO by SirCastor, to showcase various functionalities.

Detailed Explanation of the Code
1. Configuration Section
I2C Pin Definitions: Specifies which GPIO pins are used for SDA and SCL communication.
I2C Initialization: Sets up the I2C bus with the defined pins and a frequency of 100kHz.
MacSAO Address: Defines the I2C address for the MacSAO device.

2. Control Byte Constants
Defines constants for various control bytes used in communication with the MacSAO, such as writing to the display buffer or EEPROM.

3. Variable IDs
Specifies identifiers for variables that can be set or read from the MacSAO, like mode and mouse position.

4. Mode Constants
Defines constants to represent the two primary modes of the MacSAO:
MODE_ANIMATION: Passive display mode.
MODE_LIVEDRIVE: Interactive mode for real-time updates.

5. Initialization Functions
init_serial(): Initializes serial communication for debugging purposes.
init_i2c(): Initializes the I2C bus and scans for connected devices, providing debug information.

6. I2C Control Functions
Functions that handle low-level I2C communication with the MacSAO, including writing to the display buffer, writing to EEPROM, reading bytes, loading sequences, and setting/reading variables.

7. Drawing Functions
High-level functions to perform various drawing operations on the MacSAO's OLED display:
Drawing shapes like rectangles, circles, lines, and pixels.
Moving and animating the mouse cursor.
Displaying text.
Clearing the display buffer.

8. EEPROM Functions
Functions to handle writing and reading sequences of commands to and from the EEPROM, facilitating the storage of animation sequences.

9. Mode Example Functions
Example functions demonstrating how to use Animation and Live-Drive modes:
animation_example(): Sets up an animation sequence where the mouse moves between specified coordinates.
livedrive_example(): Demonstrates Live-Drive mode by drawing a window and moving the mouse cursor interactively.

10. Command Interface Functions
print_help(): Displays a list of available commands to the user.
parse_command(): Parses and executes user-input commands.
command_interface(): Runs an interactive loop, allowing the user to input commands via the serial interface.

11. Main Function
main(): Initializes serial and I2C communication, prints a readiness message, displays help information, and starts the command interface.

12. Entry Point
Ensures that the main() function is called when the script is executed.

Additional Notes
Error Handling: The script includes basic error handling to notify users of any issues during I2C communication or command execution.
Debugging: Debug messages are printed to assist with troubleshooting and to provide insights into the operations being performed.
Extensibility: The structured approach with separate functions for each operation allows for easy extension and maintenance of the codebase.
Documentation Links: For more detailed information on specific SAOs or additional functionalities, refer to the provided GitHub repository and project pages.

'''


from machine import I2C, Pin
import time
import sys

# =============================
# Configuration Section
# =============================

# Define I2C Pins based on your hardware configuration
SDA_PIN = 0  # SDA is connected to Pin 0
SCL_PIN = 1  # SCL is connected to Pin 1

# Initialize I2C bus with the correct pins and frequency
i2c = I2C(0, scl=Pin(SCL_PIN), sda=Pin(SDA_PIN), freq=100000)

# MacSAO I2C address (7-bit address)
MACSAO_ADDRESS = 0x0A

# =============================
# Control Byte Constants
# =============================

WRITE_DISPLAY_BUFFER = 1
WRITE_EEPROM = 2
READ_BYTES = 3
LOAD_SEQUENCE_FROM_EEPROM = 4
SET_VARIABLE = 5
READ_VARIABLE = 6

# =============================
# Variable IDs
# =============================

VARIABLE_MODE = 1
VARIABLE_MOUSE_POSITION = 2

# =============================
# Mode Constants
# =============================

MODE_ANIMATION = 0
MODE_LIVEDRIVE = 1

# =============================
# Initialization Functions
# =============================

def init_serial():
    """
    Initialize Serial Communication for Debugging.
    Assumes default UART (UART0). Modify if using a different UART.
    """
    print("Initializing Serial Communication for Debugging...")
    # No additional setup required as print() uses UART0 by default.

def init_i2c():
    """
    Initialize I2C bus and scan for connected devices.
    """
    print("Initializing I2C Bus...")
    devices = i2c.scan()
    if not devices:
        print("Warning: No I2C devices found. Please check connections.")
    else:
        print("Found I2C device(s) at address(es):")
        for device in devices:
            print(f"  - {hex(device)}")
        if MACSAO_ADDRESS not in devices:
            print(f"Warning: MacSAO address {hex(MACSAO_ADDRESS)} not found.")
        else:
            print(f"MacSAO found at address {hex(MACSAO_ADDRESS)}.")

# =============================
# I2C Control Functions
# =============================

def write_display_buffer(data):
    """
    Write data to the display buffer.
    
    Args:
        data (list): List of bytes to send.
    """
    try:
        control_byte = WRITE_DISPLAY_BUFFER
        buffer = bytes([control_byte]) + bytes(data)
        i2c.writeto(MACSAO_ADDRESS, buffer)
        print(f"DEBUG: Wrote to Display Buffer: {data}")
    except Exception as e:
        print(f"ERROR: Failed to write to Display Buffer: {e}")

def write_eeprom(address_high, address_low, data):
    """
    Write data to EEPROM at the specified address.
    
    Args:
        address_high (int): High byte of EEPROM address.
        address_low (int): Low byte of EEPROM address.
        data (list): Data bytes to write.
    """
    try:
        control_byte = WRITE_EEPROM
        buffer = bytes([control_byte, address_high, address_low]) + bytes(data)
        i2c.writeto(MACSAO_ADDRESS, buffer)
        print(f"DEBUG: Wrote to EEPROM at {hex((address_high << 8) | address_low)}: {data}")
    except Exception as e:
        print(f"ERROR: Failed to write to EEPROM: {e}")

def read_bytes(address_high, address_low, num_bytes):
    """
    Read bytes from EEPROM or display buffer.
    
    Args:
        address_high (int): High byte of EEPROM address.
        address_low (int): Low byte of EEPROM address.
        num_bytes (int): Number of bytes to read.
        
    Returns:
        bytes: Data read from the device.
    """
    try:
        control_byte = READ_BYTES
        buffer = bytes([control_byte, address_high, address_low, num_bytes])
        i2c.writeto(MACSAO_ADDRESS, buffer)
        data = i2c.readfrom(MACSAO_ADDRESS, num_bytes)  # Single address for read
        print(f"DEBUG: Read {num_bytes} bytes from {hex((address_high << 8) | address_low)}: {list(data)}")
        return data
    except Exception as e:
        print(f"ERROR: Failed to read bytes: {e}")
        return []

def load_sequence_from_eeprom(address_high, address_low, num_bytes):
    """
    Load an animation sequence from EEPROM into the display buffer.
    
    Args:
        address_high (int): High byte of EEPROM address.
        address_low (int): Low byte of EEPROM address.
        num_bytes (int): Number of bytes to load.
    """
    try:
        control_byte = LOAD_SEQUENCE_FROM_EEPROM
        buffer = bytes([control_byte, address_high, address_low, num_bytes])
        i2c.writeto(MACSAO_ADDRESS, buffer)
        print(f"DEBUG: Loaded sequence from EEPROM address {hex((address_high << 8) | address_low)} with length {num_bytes}")
    except Exception as e:
        print(f"ERROR: Failed to load sequence from EEPROM: {e}")

def set_variable(variable_id, *args):
    """
    Set a variable value on the MacSAO.
    
    Args:
        variable_id (int): ID of the variable to set.
        *args: Variable arguments depending on the variable.
    """
    try:
        control_byte = SET_VARIABLE
        buffer = bytes([control_byte, variable_id]) + bytes(args)
        i2c.writeto(MACSAO_ADDRESS, buffer)
        print(f"DEBUG: Set Variable {variable_id} with args {args}")
    except Exception as e:
        print(f"ERROR: Failed to set variable: {e}")

def read_variable(variable_id, num_bytes):
    """
    Read a variable value from the MacSAO.
    
    Args:
        variable_id (int): ID of the variable to read.
        num_bytes (int): Number of bytes to read.
        
    Returns:
        bytes: Data read from the variable.
    """
    try:
        control_byte = READ_VARIABLE
        buffer = bytes([control_byte, variable_id])
        i2c.writeto(MACSAO_ADDRESS, buffer)
        data = i2c.readfrom(MACSAO_ADDRESS, num_bytes)  # Single address for read
        print(f"DEBUG: Read Variable {variable_id}: {list(data)}")
        return data
    except Exception as e:
        print(f"ERROR: Failed to read variable: {e}")
        return []

# =============================
# Drawing Functions
# =============================

def set_mode(mode):
    """
    Set the MacSAO mode.
    
    Args:
        mode (int): 0 for Animation, 1 for Live-Drive.
    """
    if mode not in [MODE_ANIMATION, MODE_LIVEDRIVE]:
        print("ERROR: Invalid mode. Use 0 for Animation or 1 for Live-Drive.")
        return
    set_variable(VARIABLE_MODE, mode)
    print(f"INFO: Mode set to {'Animation' if mode == MODE_ANIMATION else 'Live-Drive'}")

def set_mouse_position(x, y):
    """
    Set the mouse position on the display.
    
    Args:
        x (int): X-coordinate (0-64).
        y (int): Y-coordinate (0-48).
    """
    if not (0 <= x <= 64 and 0 <= y <= 48):
        print("ERROR: Mouse coordinates out of range. X:0-64, Y:0-48")
        return
    set_variable(VARIABLE_MOUSE_POSITION, x, y)
    print(f"INFO: Mouse position set to ({x}, {y})")

def set_livedrive_background(commands):
    """
    Set the background in Live-Drive mode.
    
    Args:
        commands (list): List of drawing commands.
    """
    try:
        control_byte = WRITE_DISPLAY_BUFFER
        data = commands + [254]  # Append END of background
        buffer = bytes([control_byte]) + bytes(data)
        i2c.writeto(MACSAO_ADDRESS, buffer)
        print(f"DEBUG: Set Live-Drive background with commands: {commands}")
    except Exception as e:
        print(f"ERROR: Failed to set Live-Drive background: {e}")

def draw_window(x, y, width, height, scrollbars):
    """
    Draw a window on the display.
    
    Args:
        x (int): X-coordinate.
        y (int): Y-coordinate.
        width (int): Width of the window.
        height (int): Height of the window.
        scrollbars (int): 1 to include scrollbars, 0 otherwise.
    """
    data = [5, x, y, width, height, scrollbars]
    write_display_buffer(data)
    print(f"INFO: Drew window at ({x}, {y}) with width {width}, height {height}, scrollbars {scrollbars}")

def draw_pixel(x, y, color):
    """
    Draw a single pixel on the display.
    
    Args:
        x (int): X-coordinate.
        y (int): Y-coordinate.
        color (int): Color value.
    """
    data = [2, 9, x, y, color, 254]
    write_display_buffer(data)
    print(f"INFO: Drew pixel at ({x}, {y}) with color {color}")

def draw_horizontal_line(x, y, length, color):
    """
    Draw a horizontal line.
    
    Args:
        x (int): Starting X-coordinate.
        y (int): Y-coordinate.
        length (int): Length of the line.
        color (int): Color value.
    """
    data = [10, x, y, length, color]
    write_display_buffer(data)
    print(f"INFO: Drew horizontal line starting at ({x}, {y}) with length {length} and color {color}")

def draw_vertical_line(x, y, length, color):
    """
    Draw a vertical line.
    
    Args:
        x (int): X-coordinate.
        y (int): Starting Y-coordinate.
        length (int): Length of the line.
        color (int): Color value.
    """
    data = [11, x, y, length, color]
    write_display_buffer(data)
    print(f"INFO: Drew vertical line starting at ({x}, {y}) with length {length} and color {color}")

def draw_filled_rectangle(x, y, width, height, color):
    """
    Draw a filled rectangle.
    
    Args:
        x (int): X-coordinate.
        y (int): Y-coordinate.
        width (int): Width of the rectangle.
        height (int): Height of the rectangle.
        color (int): Color value.
    """
    data = [2, 12, x, y, width, height, color, 254]
    write_display_buffer(data)
    print(f"INFO: Drew filled rectangle at ({x}, {y}) with width {width}, height {height}, color {color}")

def draw_rectangle(x, y, width, height, color):
    """
    Draw an unfilled rectangle.
    
    Args:
        x (int): X-coordinate.
        y (int): Y-coordinate.
        width (int): Width of the rectangle.
        height (int): Height of the rectangle.
        color (int): Color value.
    """
    data = [2, 13, x, y, width, height, color, 254]
    write_display_buffer(data)
    print(f"INFO: Drew rectangle at ({x}, {y}) with width {width}, height {height}, color {color}")

def draw_filled_circle(x, y, radius, color):
    """
    Draw a filled circle.
    
    Args:
        x (int): X-coordinate of the center.
        y (int): Y-coordinate of the center.
        radius (int): Radius of the circle.
        color (int): Color value.
    """
    data = [2, 14, x, y, radius, color, 254]
    write_display_buffer(data)
    print(f"INFO: Drew filled circle at ({x}, {y}) with radius {radius}, color {color}")

def draw_circle(x, y, radius, color):
    """
    Draw an unfilled circle.
    
    Args:
        x (int): X-coordinate of the center.
        y (int): Y-coordinate of the center.
        radius (int): Radius of the circle.
        color (int): Color value.
    """
    data = [2, 15, x, y, radius, color, 254]
    write_display_buffer(data)
    print(f"INFO: Drew circle at ({x}, {y}) with radius {radius}, color {color}")

def move_mouse_anim(x, y):
    """
    Animate mouse movement to specified coordinates.
    
    Args:
        x (int): Target X-coordinate.
        y (int): Target Y-coordinate.
    """
    if not (0 <= x <= 64 and 0 <= y <= 48):
        print("ERROR: Mouse coordinates out of range. X:0-64, Y:0-48")
        return
    data = [16, x, y]
    write_display_buffer(data)
    print(f"INFO: Animating mouse movement to ({x}, {y})")

def buffer_pixel(x, y, color):
    """
    Draw a pixel in the MacPaint Buffer.
    
    Args:
        x (int): X-coordinate.
        y (int): Y-coordinate.
        color (int): Color value.
    """
    data = [2, 17, x, y, color, 254]
    write_display_buffer(data)
    print(f"INFO: Buffered pixel at ({x}, {y}) with color {color}")

def wait_time(time_units):
    """
    Wait for a specified amount of time.
    
    Args:
        time_units (int): Number of 100ms intervals to wait.
    """
    if time_units < 0:
        print("ERROR: Wait time cannot be negative.")
        return
    data = [18, time_units]
    write_display_buffer(data)
    print(f"INFO: Waiting for {time_units * 100} ms")
    time.sleep(time_units * 0.1)  # Convert to seconds

def put_text_command(x, y, text):
    """
    Place text at the specified location.
    
    Args:
        x (int): X-coordinate.
        y (int): Y-coordinate.
        text (str): Text to display.
    """
    ascii_text = [ord(c) for c in text] + [0]
    data = [2, 19, x, y] + ascii_text + [254]
    write_display_buffer(data)
    print(f"INFO: Put text '{text}' at ({x}, {y})")

def type_text_command(text):
    """
    Type text characters out at a rate of 0.1s per character.
    
    Args:
        text (str): Text to type.
    """
    ascii_text = [ord(c) for c in text] + [0]
    data = [20] + ascii_text
    write_display_buffer(data)
    print(f"INFO: Typed text '{text}'")

def clear_buffer(color):
    """
    Clear MacPaint Buffer.
    
    Args:
        color (int): 1 for white, 0 for black.
    """
    if color not in [0, 1]:
        print("ERROR: Invalid color. Use 0 for black or 1 for white.")
        return
    data = [21, color]
    write_display_buffer(data)
    print(f"INFO: Cleared buffer with color {'white' if color == 1 else 'black'}")

def mouse_to_menu(menu, menu_item):
    """
    Move the mouse to a specific menu and item.
    
    Args:
        menu (int): Menu number.
        menu_item (int): Item number within the menu.
    """
    data = [22, menu, menu_item]
    write_display_buffer(data)
    print(f"INFO: Moved mouse to menu {menu}, item {menu_item}")

# =============================
# EEPROM Functions
# =============================

def write_sequence_to_eeprom(address, data):
    """
    Write a sequence to EEPROM, handling data longer than 29 bytes.
    
    Args:
        address (int): Starting EEPROM address.
        data (list): Sequence data bytes.
    """
    max_chunk_size = 29  # 32 bytes - 3 bytes for control and address
    data_len = len(data)
    offset = 0
    while offset < data_len:
        chunk = data[offset:offset+max_chunk_size]
        addr = address + offset
        address_high = (addr >> 8) & 0xFF
        address_low = addr & 0xFF
        write_eeprom(address_high, address_low, chunk)
        offset += len(chunk)
        print(f"DEBUG: Written {len(chunk)} bytes to EEPROM at offset {offset}")
        time.sleep(0.1)  # Small delay between writes

def read_sequence_from_eeprom(address, num_bytes):
    """
    Read a sequence from EEPROM.
    
    Args:
        address (int): EEPROM address to start reading from.
        num_bytes (int): Number of bytes to read.
        
    Returns:
        list: Sequence data read from EEPROM.
    """
    address_high = (address >> 8) & 0xFF
    address_low = address & 0xFF
    data = read_bytes(address_high, address_low, num_bytes)
    print(f"INFO: Sequence data: {data}")
    return data

# =============================
# Mode Example Functions
# =============================

def animation_example():
    """
    Example of Animation mode: Mouse moves from (10,10) to (50,40).
    """
    print("INFO: Running Animation Example...")
    set_mode(MODE_ANIMATION)

    # Build sequence data
    data = [
        1,    # Command: Display Desktop
        1,    # Arg: Disk Unselected
        254,  # END of Background

        16,   # Command: Move Mouse to (10, 10)
        10,
        10,

        16,   # Command: Move Mouse to (50, 40)
        50,
        40,

        255,  # END of Actions
        255   # END of Sequence
    ]

    # Write sequence to EEPROM starting at address 0x0010 (16)
    sequence_address = 0x0010
    write_sequence_to_eeprom(sequence_address, data)
    print("INFO: Sequence written to EEPROM.")

    # Set preferences to load this sequence on startup
    # Preferences: bytes 2, 3: address high and low, byte 4: length
    prefs = [0, 0x00, 0x10, len(data)]
    write_eeprom(0x00, 0x02, prefs)
    print("INFO: Preferences set to load the sequence on startup.")

def livedrive_example():
    """
    Example of Live-Drive mode: Draws a window and moves the mouse.
    """
    print("INFO: Running Live-Drive Example...")
    set_mode(MODE_LIVEDRIVE)

    # Set background (Desktop with Disk Unselected)
    background_commands = [
        1,    # Command: Display Desktop
        1     # Arg: Disk Unselected
        # Additional background commands can be added here
    ]
    set_livedrive_background(background_commands)

    # Draw a window on the background
    draw_window(10, 10, 40, 30, 1)  # x, y, width, height, scrollbars

    # Move mouse to (25, 25)
    set_mouse_position(25, 25)

    # Wait and move mouse to a new position
    time.sleep(1)
    set_mouse_position(45, 35)

# =============================
# Command Interface Functions
# =============================

def print_help():
    """
    Print the list of available commands.
    """
    help_text = """
Available Commands:
-------------------
help                            - Show this help message
mode <0|1>                      - Set mode (0: Animation, 1: Live-Drive)
mouse <x> <y>                   - Set mouse position (x:0-64, y:0-48)
draw_window <x> <y> <w> <h> <s> - Draw window at (x,y) with width w, height h, scrollbars s (0 or 1)
draw_pixel <x> <y> <color>      - Draw pixel at (x,y) with color
draw_hline <x> <y> <len> <c>    - Draw horizontal line
draw_vline <x> <y> <len> <c>    - Draw vertical line
draw_filled_rect <x> <y> <w> <h> <c> - Draw filled rectangle
draw_rect <x> <y> <w> <h> <c>  - Draw rectangle (not filled)
draw_filled_circle <x> <y> <r> <c> - Draw filled circle
draw_circle <x> <y> <r> <c>     - Draw circle (not filled)
move_mouse_anim <x> <y>         - Animate mouse to (x,y)
buffer_pixel <x> <y> <c>        - Buffer pixel at (x,y) with color
wait <n>                        - Wait for n * 100ms
put_text <x> <y> <text>          - Put text at (x,y)
type_text <text>                - Type text characters out
clear_buffer <0|1>               - Clear buffer with color (0: black, 1: white)
mouse_to_menu <menu> <item>      - Move mouse to menu and item
animation_example                - Run Animation Mode Example
livedrive_example                - Run Live-Drive Mode Example
exit                             - Exit command interface
"""
    print(help_text)

def parse_command(command_str):
    """
    Parse and execute a command from the user.
    
    Args:
        command_str (str): The command string input by the user.
    """
    tokens = command_str.strip().split()
    if not tokens:
        return

    cmd = tokens[0].lower()

    try:
        if cmd == "help":
            print_help()

        elif cmd == "mode":
            if len(tokens) != 2:
                print("Usage: mode <0|1>")
                return
            mode = int(tokens[1])
            set_mode(mode)

        elif cmd == "mouse":
            if len(tokens) != 3:
                print("Usage: mouse <x> <y>")
                return
            x = int(tokens[1])
            y = int(tokens[2])
            set_mouse_position(x, y)

        elif cmd == "draw_window":
            if len(tokens) != 6:
                print("Usage: draw_window <x> <y> <w> <h> <s>")
                return
            x, y, w, h, s = map(int, tokens[1:6])
            draw_window(x, y, w, h, s)

        elif cmd == "draw_pixel":
            if len(tokens) != 4:
                print("Usage: draw_pixel <x> <y> <color>")
                return
            x, y, color = map(int, tokens[1:4])
            draw_pixel(x, y, color)

        elif cmd == "draw_hline":
            if len(tokens) != 5:
                print("Usage: draw_hline <x> <y> <len> <c>")
                return
            x, y, length, color = map(int, tokens[1:5])
            draw_horizontal_line(x, y, length, color)

        elif cmd == "draw_vline":
            if len(tokens) != 5:
                print("Usage: draw_vline <x> <y> <len> <c>")
                return
            x, y, length, color = map(int, tokens[1:5])
            draw_vertical_line(x, y, length, color)

        elif cmd == "draw_filled_rect":
            if len(tokens) != 6:
                print("Usage: draw_filled_rect <x> <y> <w> <h> <c>")
                return
            x, y, w, h, color = map(int, tokens[1:6])
            draw_filled_rectangle(x, y, w, h, color)

        elif cmd == "draw_rect":
            if len(tokens) != 6:
                print("Usage: draw_rect <x> <y> <w> <h> <c>")
                return
            x, y, w, h, color = map(int, tokens[1:6])
            draw_rectangle(x, y, w, h, color)

        elif cmd == "draw_filled_circle":
            if len(tokens) != 5:
                print("Usage: draw_filled_circle <x> <y> <r> <c>")
                return
            x, y, r, color = map(int, tokens[1:5])
            draw_filled_circle(x, y, r, color)

        elif cmd == "draw_circle":
            if len(tokens) != 5:
                print("Usage: draw_circle <x> <y> <r> <c>")
                return
            x, y, r, color = map(int, tokens[1:5])
            draw_circle(x, y, r, color)

        elif cmd == "move_mouse_anim":
            if len(tokens) != 3:
                print("Usage: move_mouse_anim <x> <y>")
                return
            x, y = map(int, tokens[1:3])
            move_mouse_anim(x, y)

        elif cmd == "buffer_pixel":
            if len(tokens) != 4:
                print("Usage: buffer_pixel <x> <y> <c>")
                return
            x, y, c = map(int, tokens[1:4])
            buffer_pixel(x, y, c)

        elif cmd == "wait":
            if len(tokens) != 2:
                print("Usage: wait <n>")
                return
            n = int(tokens[1])
            wait_time(n)

        elif cmd == "put_text":
            if len(tokens) < 4:
                print("Usage: put_text <x> <y> <text>")
                return
            x = int(tokens[1])
            y = int(tokens[2])
            text = ' '.join(tokens[3:])
            put_text_command(x, y, text)

        elif cmd == "type_text":
            if len(tokens) < 2:
                print("Usage: type_text <text>")
                return
            text = ' '.join(tokens[1:])
            type_text_command(text)

        elif cmd == "clear_buffer":
            if len(tokens) != 2:
                print("Usage: clear_buffer <0|1>")
                return
            color = int(tokens[1])
            clear_buffer(color)

        elif cmd == "mouse_to_menu":
            if len(tokens) != 3:
                print("Usage: mouse_to_menu <menu> <item>")
                return
            menu = int(tokens[1])
            item = int(tokens[2])
            mouse_to_menu(menu, item)

        elif cmd == "animation_example":
            animation_example()

        elif cmd == "livedrive_example":
            livedrive_example()

        elif cmd == "exit":
            print("INFO: Exiting command interface.")
            sys.exit()

        else:
            print("ERROR: Unknown command. Type 'help' to see available commands.")
    except:
        pass

def command_interface():
    """
    Interactive command interface via serial.
    Allows users to input commands to control the MacSAO.
    """
    print("INFO: Enter 'help' to see available commands.")
    while True:
        try:
            command_str = input(">> ")
            parse_command(command_str)
        except KeyboardInterrupt:
            print("\nINFO: Keyboard Interrupt detected. Exiting command interface.")
            break
        except EOFError:
            print("\nINFO: EOF detected. Exiting command interface.")
            break
        except Exception as e:
            print(f"ERROR: An unexpected error occurred: {e}")

# =============================
# Main Function
# =============================

def main():
    """
    Main function to initialize and run the command interface.
    """
    init_serial()
    init_i2c()
    print("INFO: MacSAO Interface Ready.")
    print_help()
    command_interface()

# =============================
# Entry Point
# =============================

if __name__ == "__main__":
    main()
