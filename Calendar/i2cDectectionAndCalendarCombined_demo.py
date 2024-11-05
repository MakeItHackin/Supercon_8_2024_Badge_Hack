# i2cDectectionAndCalendarCombined_demo.py
# MIT License
# see github.com/MakeItHackin/Supercon_8_2024_Badge_Hack for more information.

'''
Supercon 8 2024 Badge Code
Authors: MakeItHackin, CodeAllNight, Danner
Conference: Supercon 8, Pasadena, CA (Nov 1-3, 2024)
Hosted by: Hackaday
Repository: github.com/MakeItHackin/Supercon_8_2024_Badge_Hack
License: MIT License

Description:
This Micropython code is designed for the Raspberry Pi Pico Wireless badge featured at Supercon 8. The badge includes six ports supporting Simple Add-Ons (SAOs) via power, I2C, and two GPIO pins. The code integrates six SAOs, with this specific script focusing on "The Schedule SAO" by DaveDarko. It detects connected I2C devices and displays relevant information on an OLED screen, including event details from a calendar.

Code Structure and Functionality
Initialization from boot.py:

I2C Configuration: Defines I2C addresses for various devices and initializes two I2C buses (i2c0 and i2c1).
OLED Display: Sets up the OLED display using the ssd1306 library.
Boot LED and Buttons: Initializes the boot LED and three buttons (buttonA, buttonB, buttonC) with pull-up resistors.
GPIOs: Sets up GPIO pins for each of the six ports, grouped for easier management.
Petal SAO Initialization: Configures the Petal SAO if connected, handling its LED indicators.
Touchwheel SAO Initialization: Detects and initializes the Touchwheel SAO on either I2C bus, setting up its RGB display.
Initialization from main.py:

BCD Conversion: Provides utility functions to convert between decimal and Binary-Coded Decimal (BCD) formats, essential for RTC communication.
DS3231 RTC Functions: Includes functions to set and read the current time and temperature from the DS3231 RTC module.
EEPROM Read/Write Functions: Facilitates reading from and writing to the EEPROM, supporting string data storage with proper encoding and length checks.
Event Class: Defines an Event class to encapsulate event details like name, timing, speaker, and description.
Event Storage Functions: Allows serialization (save_event_to_eeprom) and deserialization (load_event_from_eeprom) of Event objects to/from EEPROM.
I2C Device Scanning and Display Functions:

Device Mapping: Maintains dictionaries mapping I2C addresses to device names and additional information for both I2C buses.
Device Scanning: Implements scan_devices to detect connected I2C devices, excluding certain addresses (e.g., OLED and EEPROM).
Display Functions: Provides functions to display a list of detected devices (display_list) and detailed information about a selected device (display_details) on the OLED.
Combining Functionalities:

Display Modes: Defines different modes for the OLED display, including main menu, I2C detection, device detail view, and event display.
User Interaction: The main function handles user input via buttons to navigate between modes, select options, and view details.
Event Display: Shows event details along with a countdown timer, indicating when the event will start or if it has already begun.
Running the Main Function:

The script starts by calling the main function, which enters an infinite loop handling display updates and user interactions. There's also a commented-out line to create a test event for demonstration purposes.
Additional Information
SAOs Integrated:

Skull of Fate: Mystical artifact for determining one's fate.
Etch-SAO-Sketch: Digital drawing pad.
Touchwheel: Interactive touch-based input device.
BlinkyLoop: Provides mesmerizing blinking patterns.
The Schedule SAO: Manages and displays event schedules.
MacSAO: Emulates a Macintosh interface.
Project References:

Skull of Fate: Hackaday Project 198974
Etch-SAO-Sketch: Hackaday Project 197581
Touchwheel: GitHub - todbot/TouchwheelSAO
BlinkyLoop: Hackaday Project 198163
The Schedule SAO: Hackaday Project 198229
MacSAO: Hackaday Project 196403
For more detailed information, refer to the GitHub repository.

Usage Notes
Button Controls:

Button A: Navigate through menu options.
Button B: Select the highlighted option.
Button C: Return to the previous menu or main menu.
Creating Events:

Uncomment the create_test_event() line in the __main__ section to generate a test event in EEPROM.
Error Handling:

The code includes print statements to notify about any issues during I2C communication, EEPROM operations, or display updates.
Customization:

Adjust I2C addresses and GPIO pin assignments as necessary based on specific hardware configurations.

'''


from machine import I2C, Pin
import time
import sys
import ssd1306

# =========================
# Initialization from boot.py
# =========================

# -------------------------
# I2C Addresses Configuration
# -------------------------
PETAL_ADDRESS = 0x00
TOUCHWHEEL_ADDRESS = 0x54
OLED_ADDRESS = 0x3C
DS3231_I2C_ADDR = 0x68
EEPROM_I2C_ADDR = 0x57  # Adjust based on your EEPROM's address pins

# -------------------------
# Initialize I2C Buses
# -------------------------
i2c0 = I2C(0, sda=Pin(0), scl=Pin(1), freq=400_000)
i2c1 = I2C(1, sda=Pin(26), scl=Pin(27), freq=400_000)

# -------------------------
# Initialize OLED Display
# -------------------------
display = ssd1306.SSD1306_I2C(128, 64, i2c0)

# -------------------------
# Initialize Boot LED
# -------------------------
bootLED = Pin("LED", Pin.OUT)
bootLED.on()

# -------------------------
# Initialize Buttons
# -------------------------
buttonA = Pin(8, Pin.IN, Pin.PULL_UP)
buttonB = Pin(9, Pin.IN, Pin.PULL_UP)
buttonC = Pin(28, Pin.IN, Pin.PULL_UP)

# -------------------------
# Initialize GPIOs for Each Port
# -------------------------
gpio11 = Pin(7, Pin.OUT)
gpio12 = Pin(6, Pin.OUT)

gpio21 = Pin(5, Pin.OUT)
gpio22 = Pin(4, Pin.OUT)

gpio31 = Pin(3, Pin.OUT)
gpio32 = Pin(2, Pin.OUT)

gpio41 = Pin(22, Pin.OUT)
gpio42 = Pin(21, Pin.OUT)

gpio51 = Pin(20, Pin.OUT)
gpio52 = Pin(19, Pin.OUT)

gpio61 = Pin(18, Pin.OUT)
gpio62 = Pin(17, Pin.OUT)

# Group GPIOs for easier management
GPIOs = [
    [gpio11, gpio12],
    [gpio21, gpio22],
    [gpio31, gpio32],
    [gpio41, gpio42],
    [gpio51, gpio52],
    [gpio61, gpio62],
]

# -------------------------
# Petal SAO Initialization Function
# -------------------------
def petal_init(bus):
    """Configure the petal SAO."""
    bus.writeto_mem(PETAL_ADDRESS, 0x09, bytes([0x00]))  # raw pixel mode (not 7-seg)
    bus.writeto_mem(PETAL_ADDRESS, 0x0A, bytes([0x09]))  # intensity (of 16)
    bus.writeto_mem(PETAL_ADDRESS, 0x0B, bytes([0x07]))  # enable all segments
    bus.writeto_mem(PETAL_ADDRESS, 0x0C, bytes([0x81]))  # undo shutdown bits
    bus.writeto_mem(PETAL_ADDRESS, 0x0D, bytes([0x00]))
    bus.writeto_mem(PETAL_ADDRESS, 0x0E, bytes([0x00]))  # no crazy features (default?)
    bus.writeto_mem(PETAL_ADDRESS, 0x0F, bytes([0x00]))  # turn off display test mode

# -------------------------
# Initialize Petal SAO on Available I2C Bus
# -------------------------
petal_bus = None
try:
    petal_init(i2c0)
    petal_bus = i2c0
except:
    pass

try:
    petal_init(i2c1)
    petal_bus = i2c1
except:
    pass

if not petal_bus:
    print("Warning: Petal not found.")

# -------------------------
# Configure Petal LEDs if Found
# -------------------------
if petal_bus:
    petal_bus.writeto_mem(PETAL_ADDRESS, 3, bytes([0x80]))
    petal_bus.writeto_mem(PETAL_ADDRESS, 2, bytes([0x80]))
    petal_bus.writeto_mem(PETAL_ADDRESS, 3, bytes([0x00]))
    petal_bus.writeto_mem(PETAL_ADDRESS, 2, bytes([0x80]))
    time.sleep_ms(200)
    petal_bus.writeto_mem(PETAL_ADDRESS, 2, bytes([0x00]))

# -------------------------
# Initialize Touchwheel SAO
# -------------------------
touchwheel_bus = None
touchwheel_counter = 0
while not touchwheel_bus:
    try:
        # Scan i2c0 for touchwheel
        if TOUCHWHEEL_ADDRESS in i2c0.scan():
            touchwheel_bus = i2c0
        # If not found, scan i2c1
        elif TOUCHWHEEL_ADDRESS in i2c1.scan():
            touchwheel_bus = i2c1
    except:
        pass
    time.sleep_ms(100)
    touchwheel_counter += 1
    if touchwheel_counter > 50:
        break

if not touchwheel_bus:
    print("Warning: Touchwheel not found.")

# -------------------------
# Touchwheel SAO Functions
# -------------------------
def touchwheel_read(bus):
    """Returns 0 for no touch, 1-255 clockwise around the circle from the south."""
    return bus.readfrom_mem(TOUCHWHEEL_ADDRESS, 0, 1)[0]

def touchwheel_rgb(bus, r, g, b):
    """Set RGB color on the central display. Each value ranges from 0-255."""
    bus.writeto_mem(TOUCHWHEEL_ADDRESS, 15, bytes([r]))
    bus.writeto_mem(TOUCHWHEEL_ADDRESS, 16, bytes([g]))
    bus.writeto_mem(TOUCHWHEEL_ADDRESS, 17, bytes([b]))

# -------------------------
# Enable Green LED if Wheel Configured
# -------------------------
if touchwheel_bus and petal_bus:
    petal_bus.writeto_mem(PETAL_ADDRESS, 3, bytes([0x00]))
if petal_bus:
    petal_bus.writeto_mem(PETAL_ADDRESS, 2, bytes([0x80]))
    time.sleep_ms(200)
    petal_bus.writeto_mem(PETAL_ADDRESS, 2, bytes([0x00]))

# =========================
# Initialization from main.py
# =========================

# -------------------------
# BCD Conversion Functions
# -------------------------
def dec_to_bcd(val):
    """Convert decimal to Binary-Coded Decimal (BCD)."""
    return (val // 10 << 4) + (val % 10)

def bcd_to_dec(val):
    """Convert Binary-Coded Decimal (BCD) to decimal."""
    return ((val >> 4) * 10) + (val & 0x0F)

# -------------------------
# DS3231 RTC Functions
# -------------------------
def set_time(year, month, date, day, hour, minute, second):
    """Set the DS3231 RTC time."""
    year = year % 100  # Ensure two-digit year
    data = bytes([
        dec_to_bcd(second),
        dec_to_bcd(minute),
        dec_to_bcd(hour),
        dec_to_bcd(day),
        dec_to_bcd(date),
        dec_to_bcd(month),
        dec_to_bcd(year)
    ])
    try:
        i2c0.writeto_mem(DS3231_I2C_ADDR, 0x00, data)
        print("Time set successfully.")
    except OSError as e:
        print("Failed to set time:", e)

def read_time():
    """Read the current time from DS3231 RTC."""
    try:
        data = i2c0.readfrom_mem(DS3231_I2C_ADDR, 0x00, 7)
        second = bcd_to_dec(data[0])
        minute = bcd_to_dec(data[1])
        hour = bcd_to_dec(data[2])
        day = bcd_to_dec(data[3])
        date = bcd_to_dec(data[4])
        month = bcd_to_dec(data[5] & 0x1F)
        year = bcd_to_dec(data[6]) + 2000
        return (year, month, date, day, hour, minute, second)
    except OSError as e:
        print("Failed to read time:", e)
        return None

def read_temperature():
    """Read the temperature from DS3231 RTC."""
    try:
        temp_msb = i2c0.readfrom_mem(DS3231_I2C_ADDR, 0x11, 1)[0]
        temp_lsb = i2c0.readfrom_mem(DS3231_I2C_ADDR, 0x12, 1)[0]
        temp = temp_msb + ((temp_lsb >> 6) * 0.25)
        print(f"Read Temperature: {temp:.2f}°C")
        return temp
    except OSError as e:
        print("Failed to read temperature:", e)
        return None

# -------------------------
# EEPROM Read/Write Functions
# -------------------------
EEPROM_SIZE = 4096  # 4KB EEPROM
PAGE_SIZE = 32       # EEPROM page size

def write_bytes_to_eeprom(address, data):
    """
    Write bytes to EEPROM starting at the specified address.
    Utilizes writeto_mem with two-byte addressing for EEPROMs larger than 256 bytes.
    """
    while data:
        chunk = data[:PAGE_SIZE]
        data = data[PAGE_SIZE:]
        try:
            # Use writeto_mem with two-byte address by specifying addrsize=16
            i2c0.writeto_mem(EEPROM_I2C_ADDR, address, chunk, addrsize=16)
            time.sleep_ms(10)  # Increased delay to ensure EEPROM write cycle completes
            address += len(chunk)
        except OSError as e:
            print("Failed to write to EEPROM:", e)
            break
    print("Bytes written to EEPROM successfully.")

def read_bytes_from_eeprom(address, length):
    """
    Read a specified number of bytes from EEPROM starting at the given address.
    Utilizes readfrom_mem with two-byte addressing.
    """
    try:
        # Use readfrom_mem with two-byte address by specifying addrsize=16
        data = i2c0.readfrom_mem(EEPROM_I2C_ADDR, address, length, addrsize=16)
        return data
    except OSError as e:
        print("Failed to read from EEPROM:", e)
        return None

def write_string_to_eeprom(address, string):
    """Write a string to EEPROM at the specified address."""
    data = string.encode('utf-8')
    write_bytes_to_eeprom(address, data)
    print("String written to EEPROM successfully.")

def read_string_from_eeprom(address, length):
    """Read a string of a specified length from EEPROM starting at the given address."""
    data = read_bytes_from_eeprom(address, length)
    if data is not None and len(data) == length:
        try:
            string = data.decode('utf-8')
            return string
        except ValueError as e:
            print("Failed to decode string from EEPROM:", e)
            return None
    else:
        print(f"Failed to read {length} bytes from EEPROM at address {address}")
        return None

# -------------------------
# Event Class Definition
# -------------------------
class Event:
    """Class representing an event in the schedule."""
    def __init__(self, event_name, start_time, end_time, speaker_name, description):
        self.event_name = event_name
        self.start_time = start_time  # Epoch time
        self.end_time = end_time      # Epoch time
        self.speaker_name = speaker_name
        self.description = description

# -------------------------
# Event Storage Functions
# -------------------------
def save_event_to_eeprom(event, address):
    """Serialize and save an event to EEPROM at the specified address."""
    data = bytearray()
    
    # Event Name
    event_name_bytes = event.event_name.encode('utf-8')
    if len(event_name_bytes) > 50:
        print("Event name too long! Maximum 50 bytes allowed.")
        return
    data.append(len(event_name_bytes))
    data.extend(event_name_bytes)
    
    # Start Time (4 bytes)
    data.extend(event.start_time.to_bytes(4, 'big'))
    
    # End Time (4 bytes)
    data.extend(event.end_time.to_bytes(4, 'big'))
    
    # Speaker Name
    speaker_name_bytes = event.speaker_name.encode('utf-8')
    if len(speaker_name_bytes) > 50:
        print("Speaker name too long! Maximum 50 bytes allowed.")
        return
    data.append(len(speaker_name_bytes))
    data.extend(speaker_name_bytes)
    
    # Description
    description_bytes = event.description.encode('utf-8')
    if len(description_bytes) > 138:
        print("Description too long! Maximum 138 bytes allowed.")
        return
    data.extend(len(description_bytes).to_bytes(2, 'big'))
    data.extend(description_bytes)
    
    # Ensure total data length does not exceed 250 bytes
    if len(data) > 250:
        print(f"Serialized event size {len(data)} exceeds 250 bytes. Cannot save.")
        return
    
    # Write data to EEPROM
    write_bytes_to_eeprom(address, data)
    print("Event saved successfully.")
    
    # Optional Verification: Read back the written data to confirm
    verification_data = read_bytes_from_eeprom(address, len(data))
    if verification_data == data:
        print("Verification Successful: Data written correctly.")
    else:
        print("Verification Failed: Data mismatch.")

def load_event_from_eeprom(address):
    """Load and deserialize an event from EEPROM starting at the specified address."""
    print(f"Loading event from EEPROM address {address}")
    
    # Read Event Name Length
    event_name_length_bytes = read_bytes_from_eeprom(address, 1)
    if event_name_length_bytes is None:
        print("Failed to read event name length.")
        return None
    event_name_length = event_name_length_bytes[0]
    print(f"Event Name Length: {event_name_length}")
    
    # Check if the entire event slot is empty (all bytes set to 0xFF)
    if event_name_length == 0xFF:
        print(f"Event slot at address {address} is empty.")
        return None
    
    # Validate event_name_length
    if event_name_length == 0 or event_name_length > 50:
        print(f"Invalid event name length ({event_name_length}) at address {address}. Skipping.")
        return None
    address += 1
    
    # Read Event Name
    event_name = read_string_from_eeprom(address, event_name_length)
    if event_name is None:
        print(f"Invalid event name at address {address}. Skipping event.")
        return None
    address += event_name_length
    
    # Read Start Time
    start_time_bytes = read_bytes_from_eeprom(address, 4)
    if start_time_bytes is None or len(start_time_bytes) != 4:
        print("Failed to read start time.")
        return None
    start_time = int.from_bytes(start_time_bytes, 'big')
    print(f"Start Time (Epoch): {start_time}")
    address += 4
    
    # Read End Time
    end_time_bytes = read_bytes_from_eeprom(address, 4)
    if end_time_bytes is None or len(end_time_bytes) != 4:
        print("Failed to read end time.")
        return None
    end_time = int.from_bytes(end_time_bytes, 'big')
    print(f"End Time (Epoch): {end_time}")
    address += 4
    
    # Read Speaker Name Length
    speaker_name_length_bytes = read_bytes_from_eeprom(address, 1)
    if speaker_name_length_bytes is None:
        print("Failed to read speaker name length.")
        return None
    speaker_name_length = speaker_name_length_bytes[0]
    print(f"Speaker Name Length: {speaker_name_length}")
    
    # Check if the speaker name field is entirely empty
    if speaker_name_length == 0xFF:
        print(f"Speaker name field at address {address} is empty.")
        return None
    
    # Validate speaker_name_length
    if speaker_name_length == 0 or speaker_name_length > 50:
        print(f"Invalid speaker name length ({speaker_name_length}) at address {address}. Skipping.")
        return None
    address += 1
    
    # Read Speaker Name
    speaker_name = read_string_from_eeprom(address, speaker_name_length)
    if speaker_name is None:
        print(f"Invalid speaker name at address {address}. Skipping event.")
        return None
    address += speaker_name_length
    
    # Read Description Length
    description_length_bytes = read_bytes_from_eeprom(address, 2)
    if description_length_bytes is None or len(description_length_bytes) != 2:
        print("Failed to read description length.")
        return None
    description_length = int.from_bytes(description_length_bytes, 'big')
    print(f"Description Length: {description_length}")
    
    # Check if the description field is entirely empty
    if description_length == 0xFFFF:
        print(f"Description field at address {address} is empty.")
        return None
    
    # Validate description_length
    if description_length == 0 or description_length > 138:
        print(f"Invalid description length ({description_length}) at address {address}. Skipping.")
        return None
    address += 2
    
    # Read Description
    description = read_string_from_eeprom(address, description_length)
    if description is None:
        print(f"Invalid description at address {address}. Skipping event.")
        return None
    address += description_length
    
    # Create event object
    event = Event(event_name, start_time, end_time, speaker_name, description)
    print("Event loaded successfully.")
    return event

# =========================
# I2C Device Scanning and Display Functions from boot.py
# =========================

# -------------------------
# Device Names Mapping for Each I2C Bus
# -------------------------
device_names_i2c0 = {
    0x54: "Touchwheel",
    0x55: "BadgeTagNFC",
    0x15: "Skull of Fate",
    0x14: "Skull of Fate",
    0x13: "Skull of Fate",
    0x19: "Blinky Loop",
    0x57: "Calendar"
}

device_names_i2c1 = {
    0x54: "Touchwheel",
    0x55: "BadgeTagNFC",
    0x15: "Skull of Fate",
    0x14: "Skull of Fate",
    0x13: "Skull of Fate",
    0x19: "Etch sAo Sketch",
    0x57: "Calendar"
}

# -------------------------
# Devices to Exclude from Display
# -------------------------
exclude_list = {
    0x3C: "OLED Display",
    0x68: "EEprom Calendar"
}

# -------------------------
# Device Information Mapping
# -------------------------
device_info = {
    (0x19, "i2c0"): "Blinky Loop provides mesmerizing blinking patterns.",
    (0x19, "i2c1"): "Etch sAo Sketch is a digital drawing pad.",
    0x54: "TouchwheelSAO by @todbot github.com/todbot/TouchWheelSAO",
    0x55: "BadgeTagNFC is a versatile NFC badge.",
    0x15: "Skull of Fate is a mystical artifact for determining one's fate.",
    0x14: "Another variant of the Skull of Fate.",
    0x13: "Yet another version of the Skull of Fate.",
    0x57: "This is a calendar"
}

# -------------------------
# Function to Scan I2C Buses for Devices
# -------------------------
def scan_devices():
    """Scan I2C buses and return a list of detected devices."""
    detected_devices = []

    # Scan i2c0
    i2c0_array = i2c0.scan()
    for device in i2c0_array:
        if device not in exclude_list and device not in [d["name"] for d in detected_devices]:
            if device in device_names_i2c0:
                detected_devices.append({"address": device, "name": device_names_i2c0[device], "bus": "i2c0"})
            else:
                detected_devices.append({"address": device, "name": hex(device), "bus": "i2c0"})

    # Scan i2c1
    i2c1_array = i2c1.scan()
    for device in i2c1_array:
        if device not in exclude_list and device not in [d["name"] for d in detected_devices]:
            if device in device_names_i2c1:
                detected_devices.append({"address": device, "name": device_names_i2c1[device], "bus": "i2c1"})
            else:
                detected_devices.append({"address": device, "name": hex(device), "bus": "i2c1"})

    return detected_devices

# -------------------------
# Function to Display Device Details with Text Wrapping
# -------------------------
def display_details(device):
    """Display detailed information about a specific device on the OLED."""
    try:
        display.fill(0)
        display.text(device["name"], 0, 0, 1)
        info_key = (device["address"], device["bus"])
        if info_key in device_info:
            info = device_info[info_key]
        elif device["address"] in device_info:
            info = device_info[device["address"]]
        else:
            info = "No additional info available."

        y_position = 16
        line_length = 16  # Approximate number of characters that fit in 128px width
        info = info.strip()  # Remove any leading/trailing whitespace
        for i in range(0, len(info), line_length):
            line = info[i:i + line_length].strip()  # Remove leading whitespace for each line
            display.text(line, 0, y_position, 1)
            y_position += 9
            if y_position > 55:  # Prevent text from going off the screen
                break
        display.show()
    except OSError as e:
        print(f"OSError while displaying details: {e}")

# -------------------------
# Function to Display List of Detected Devices
# -------------------------
def display_list(devices, current_selection):
    """Display a list of detected I2C devices with the current selection highlighted."""
    try:
        display.fill(0)
        display.text("Super Add Ons:", 0, 0, 1)
        display.line(0, 9, 127, 9, 1) 
        
        y_position = 16
        for i, device in enumerate(devices):
            name = device["name"]
            if i == current_selection:
                name = ">" + name  # Add a marker to show the current selection
            display.text(name, 0, y_position, 1)
            y_position += 9
            if y_position > 55:  # Prevent text from going off the screen
                break

        display.show()
    except OSError as e:
        print(f"OSError while displaying list: {e}")

# =========================
# Combining Both Functionalities
# =========================

# -------------------------
# Display Mode Definitions
# -------------------------
MODE_MAIN_MENU = 0
MODE_I2C_DETECT = 1
MODE_I2C_DETAIL = 2
MODE_EVENT_DISPLAY = 3

# -------------------------
# Function to Create and Save a Test Event (For Demonstration)
# -------------------------
def create_test_event():
    """Create and save a test event to EEPROM for demonstration purposes."""
    # Define test event details
    event_name = "Test Event"
    speaker_name = "John Doe"
    description = "This is a test event description."
    
    # Set start and end times (e.g., current time and one hour later)
    current_time = int(time.time())
    start_time = current_time + 60  # Starts in 1 minute
    end_time = start_time + 3600     # Ends in 1 hour

    # Create Event object
    test_event = Event(event_name, start_time, end_time, speaker_name, description)

    # Save to EEPROM at address 0
    save_event_to_eeprom(test_event, 0)

# -------------------------
# Main Function to Handle Display Modes and User Interaction
# -------------------------
def main():
    """Main loop handling different display modes and user interactions."""
    # Initialize variables for main menu
    current_mode = MODE_MAIN_MENU
    main_menu_options = ["I2C Detect", "Event Display"]
    main_menu_selection = 0
    main_menu_length = len(main_menu_options)

    # Initialize variables for I2C navigation
    i2c_devices = scan_devices()
    i2c_selection = 0

    # Load an event (for demonstration purposes, loading from address 0)
    event = load_event_from_eeprom(0)  # Modify as needed

    while True:
        # Handle Mode-Based Display
        if current_mode == MODE_MAIN_MENU:
            display_main_menu(main_menu_options, main_menu_selection)
        elif current_mode == MODE_I2C_DETECT:
            i2c_devices = scan_devices()  # Refresh device list
            display_list(i2c_devices, i2c_selection)
        elif current_mode == MODE_I2C_DETAIL:
            if i2c_devices and i2c_selection < len(i2c_devices):
                selected_device = i2c_devices[i2c_selection]
                display_details(selected_device)
            else:
                display.fill(0)
                display.text("No device selected", 0, 0, 1)
                display.show()
        elif current_mode == MODE_EVENT_DISPLAY:
            if event:
                display_event(event)
            else:
                display_no_event()

        # Handle button presses
        if buttonA.value() == 0:  # Button A: Move selection down
            if current_mode == MODE_MAIN_MENU:
                main_menu_selection = (main_menu_selection + 1) % main_menu_length
            elif current_mode == MODE_I2C_DETECT:
                if i2c_devices:
                    i2c_selection = (i2c_selection + 1) % len(i2c_devices)
            # Add more modes here if needed
            time.sleep(0.2)  # Debounce delay

        elif buttonB.value() == 0:  # Button B: Select
            if current_mode == MODE_MAIN_MENU:
                selected_option = main_menu_options[main_menu_selection]
                if selected_option == "I2C Detect":
                    current_mode = MODE_I2C_DETECT
                    i2c_selection = 0  # Reset selection
                elif selected_option == "Event Display":
                    current_mode = MODE_EVENT_DISPLAY
            elif current_mode == MODE_I2C_DETECT:
                if i2c_devices:
                    current_mode = MODE_I2C_DETAIL
            elif current_mode == MODE_I2C_DETAIL:
                # Optionally, implement actions when selecting a device detail
                pass
            elif current_mode == MODE_EVENT_DISPLAY:
                # Optionally, implement actions in event display
                pass
            # Add more modes here if needed
            time.sleep(0.2)  # Debounce delay

        elif buttonC.value() == 0:  # Button C: Return to Main Menu or previous menu
            if current_mode == MODE_I2C_DETAIL:
                current_mode = MODE_I2C_DETECT  # Return to I2C Detect device list
            elif current_mode in [MODE_I2C_DETECT, MODE_EVENT_DISPLAY]:
                current_mode = MODE_MAIN_MENU  # Return to Main Menu
            elif current_mode == MODE_MAIN_MENU:
                # Optionally, implement exit or do nothing
                pass
            # Add more modes here if needed
            time.sleep(0.2)  # Debounce delay

        # Add a small sleep to avoid excessive CPU usage
        time.sleep(0.05)

# -------------------------
# Function to Display Main Menu
# -------------------------
def display_main_menu(options, selection):
    """Display the main menu with given options and current selection."""
    try:
        display.fill(0)
        display.text("Main Menu:", 0, 0, 1)
        display.line(0, 9, 127, 9, 1)
        
        y_position = 16
        for i, option in enumerate(options):
            display_text = option
            if i == selection:
                display_text = ">" + option  # Highlight selected option
            display.text(display_text, 0, y_position, 1)
            y_position += 9
            if y_position > 55:  # Prevent text from going off the screen
                break

        display.show()
    except OSError as e:
        print(f"OSError while displaying main menu: {e}")

# -------------------------
# Function to Display "No Event" Message
# -------------------------
def display_no_event():
    """Display a message indicating no event is scheduled."""
    try:
        display.fill(0)
        display.text("No Event Scheduled", 0, 0, 1)
        display.show()
    except OSError as e:
        print(f"OSError while displaying no event: {e}")

# -------------------------
# Function to Display Current Time on OLED
# -------------------------
def display_current_time():
    """Read and display the current time on the OLED."""
    display.fill(0)  # Clear the display
    display.text("Current Time:", 0, 0, 1)  # Display "Current Time:" label
    
    try:
        time_data = read_time()
        if time_data:
            year, month, date, day, hour, minute, second = time_data
            time_string = "{:02}:{:02}:{:02}".format(hour, minute, second)  # Format the time
            date_string = "{:04}-{:02}-{:02}".format(year, month, date)
            display.text(time_string, 0, 20, 1)  # Display formatted time
            display.text(date_string, 0, 30, 1)  # Display formatted date
    except Exception as e:
        print("Error:", e)
    
    display.show()  # Refresh the OLED display

# -------------------------
# Function to Display Event Details with Countdown
# -------------------------
def display_event(event):
    """Display event details with a countdown on the OLED."""
    try:
        # Clear the display
        display.fill(0)

        # Get the current time
        current_time_data = read_time()
        if current_time_data:
            current_time = int(time.mktime(current_time_data))
        else:
            current_time = int(time.time())  # Fallback to epoch time if RTC fails

        time_left = event.start_time - current_time

        # Determine what to display based on the countdown
        if time_left > 10:
            hours, remainder = divmod(time_left, 3600)
            minutes, seconds = divmod(remainder, 60)
            countdown_string = "Starts:{:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds))
        elif time_left > 0:
            countdown_string = "10 Minutes!"
        else:
            countdown_string = "Event started!"

        # Display the countdown or event started message on the first line
        display.text(countdown_string, 0, 0, 1)

        # Initialize y_offset for event details
        y_offset = 16  # Start after a 16-pixel offset

        # Event Name
        display.text("Name: " + event.event_name, 0, y_offset, 1)
        y_offset += 9

        # Convert start time and end time from epoch to struct_time
        start_time_struct = time.localtime(event.start_time)
        end_time_struct = time.localtime(event.end_time)

        # Event Start Time
        start_time_str = "Start: {:02}:{:02}".format(
            start_time_struct[3], start_time_struct[4])
        display.text(start_time_str, 0, y_offset, 1)
        y_offset += 9

        # Event End Time
        end_time_str = "End: {:02}:{:02}".format(
            end_time_struct[3], end_time_struct[4])
        display.text(end_time_str, 0, y_offset, 1)
        y_offset += 9

        # Speaker Name
        display.text("Speaker: " + event.speaker_name, 0, y_offset, 1)
        y_offset += 9

        # Description (truncated if too long)
        display.text("Desc: " + event.description[:20], 0, y_offset, 1)

        # Refresh OLED display
        display.show()
    except OSError as e:
        print(f"OSError while displaying event: {e}")

# =========================
# Run the Main Function
# =========================

if __name__ == "__main__":
    # Uncomment the following line to create a test event
    # create_test_event()
    main()
