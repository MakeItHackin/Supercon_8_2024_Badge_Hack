# ConnectingWithFriends.py
# Demonstrated at Supercon 8 Nov 3, 2024
# MIT License
# see github.com/MakeItHackin/Supercon_8_2024_Badge_Hack for more information.

'''
**Authors:**
- MakeItHackin
- CodeAllNight
- Danner

**Simple Add-Ons (SAOs) Integrated:**
1. [Skull of Fate by p1x317h13f and MakeItHackin](https://hackaday.io/project/198974-skull-of-fate-sao)
2. [Etch-SAO-Sketch by Andy Geppert](https://hackaday.io/project/197581-etch-sao-sketch)
3. [Touchwheel by Todbot](https://github.com/todbot/TouchwheelSAO?tab=readme-ov-file)
4. [BlinkyLoop by Flummer](https://hackaday.io/project/198163-blinky-loop-sao)
5. [The Schedule SAO by DaveDarko](https://hackaday.io/project/198229-the-schedule-sao)
6. [MacSAO by SirCastor](https://hackaday.io/project/196403-macintosh-sao)

**Note:** For more detailed information, visit the [GitHub repository](https://github.com/MakeItHackin/Supercon_8_2024_Badge_Hack).


Detailed Breakdown
1. Configuration Constants
NeoPixel Configuration: Defines the number of NeoPixels and the GPIO pin they are connected to.
I2C Addresses: Assigns I2C addresses for various Simple Add-Ons (SAOs) and peripherals like the OLED display, RTC, and EEPROM.
EEPROM Configuration: Sets the size and page size for EEPROM operations.
Screen Dimensions & Animation Settings: Configures the OLED screen size and animation parameters.
2. Initialization and Setup
NeoPixel Initialization: Sets up the NeoPixels connected to the specified GPIO pin.
I2C Bus Initialization: Initializes two I2C buses (i2c0 and i2c1) with their respective SDA and SCL pins.
OLED Display Initialization: Sets up the OLED display using i2c0.
Etch SAO Initialization: Initializes the Etch SAO on i2c1 and clears its display.
Boot LED: Turns on the boot LED to indicate the device has started.
Button Initialization: Sets up three buttons (buttonA, buttonB, buttonC) with pull-up resistors for user input.
GPIO Initialization: Initializes GPIO pins for additional SAOs, grouped for easy management.
Petal SAO Initialization: Attempts to initialize the Petal SAO on both I2C buses and configures its LEDs if found.
Touchwheel Initialization: Scans both I2C buses to find and initialize the Touchwheel SAO, configuring LEDs accordingly.
3. Helper Functions
NeoPixel Control: Functions to clear NeoPixels, perform animations like theater chase and rainbow cycle, and set all pixels to a specific color.
Screen Saver Functions: Functions to draw rectangles and circles on the OLED display to create a screensaver effect.
4. I2C Communication Functions
Payload Sending: send_payload sends data to the MacSAO and handles any exceptions.
Rectangle Payload Creation: create_rectangle_payload creates a data payload to draw filled rectangles on the OLED.
Y-Coordinate Mapping: map_y maps input values to Y-coordinates for positioning elements on the screen.
Screen Saver Functions: screen_saver and screen_saver_circle handle drawing shapes on the OLED.
5. Event Handling and EEPROM Management
Event Class: Defines an Event class to store event details.
BCD Conversion: Utility functions dec_to_bcd and bcd_to_dec handle conversion between decimal and BCD formats for RTC operations.
RTC Time Management: Functions to set and read the current time from the DS3231 RTC.
EEPROM Operations: Functions to write and read bytes or strings to/from EEPROM, including wiping the EEPROM.
Event Serialization: save_event_to_eeprom and load_event_from_eeprom handle saving and loading event objects to/from EEPROM.
6. Touchwheel Functions
Reading Touch Input: touchwheel_read retrieves the current touch input from the Touchwheel SAO.
Setting RGB Colors: touchwheel_rgb sets the RGB color on the Touchwheel's central display.
7. I2C Device Scanning and Display
Device Mapping: Dictionaries device_names_i2c0 and device_names_i2c1 map I2C addresses to device names for both I2C buses.
Exclusion List: exclude_list contains I2C addresses of devices that should not be displayed.
Device Information: device_info provides detailed descriptions for each detected device.
Device Scanning: scan_devices scans both I2C buses, identifies connected devices, and excludes specified ones.
Display Functions: display_details and display_list handle showing device information on the OLED display.
8. I2C Device Command Functions
Command Sending: send_i2c_command sends specific commands to a client device over I2C and processes the response.
Response Decoding: decode_response interprets responses based on the command sent.
Float Conversion: float_from_bytes converts byte data to floating-point numbers (placeholder implementation).
9. Event Display Functions
Display Event: display_event shows event details and a countdown timer on the OLED.
No Event Display: display_no_event indicates when no event is scheduled.
Main Menu Display: display_main_menu presents the main menu options to the user.
10. Menu and Mode Definitions
Display Modes: Constants defining various display modes such as main menu, I2C detection, event display, and Pong animation.
11. Pong Animation Function
Pong: pong handles the Pong animation, featuring moving circles and rectangles on the OLED as a screensaver.
12. Main Loop and User Interaction
Main Function: main manages the primary loop, handling user input via buttons, updating displays based on the current mode, and interacting with SAOs.
13. Utility Functions
Create Test Event: create_test_event generates and saves a sample event to EEPROM for testing purposes.
Reset Time and Event: reset_time_and_event sets the RTC to a specific time and optionally creates an event.
14. Run the Main Function
The script checks if it's the main module and calls the main function to start execution. Optionally, you can create a test event by uncommenting the relevant line.
Additional Notes
Redundancies: The constants BLINKY_LOOP_NUM_PIXELS and BLINKY_LOOP_PIN_NUM are defined twice. You might want to remove the redundant definitions to prevent confusion.

Error Handling: The code includes basic error handling for I2C communications and display operations. Depending on the use case, you might want to enhance these to handle more specific scenarios.

Placeholder Functions: The float_from_bytes function is a placeholder. Ensure you replace it with the actual implementation required for your application.

Uncomment Sections: There are sections in the reset_time_and_event function that are commented out. Uncomment and modify them as needed for your specific event setup.

Documentation: Consider adding more docstrings and inline comments for complex logic sections to further enhance readability.

'''

from machine import I2C, Pin
import time
import sys
import ssd1306
import neopixel
import etch

# =========================
# Configuration Constants
# =========================

# -------------------------
# NeoPixel Configuration
# -------------------------
BLINKY_LOOP_NUM_PIXELS = 12       # Number of NeoPixels in the BlinkyLoop add-on
BLINKY_LOOP_PIN_NUM = 22          # GPIO pin number connected to NeoPixels

# -------------------------
# I2C Addresses for SAOs and Peripherals
# -------------------------
PETAL_ADDRESS = 0x00              # I2C address for the Petal SAO
TOUCHWHEEL_ADDRESS = 0x54         # I2C address for the Touchwheel SAO
OLED_ADDRESS = 0x3C                # I2C address for the OLED display
DS3231_I2C_ADDR = 0x68             # I2C address for the DS3231 RTC
EEPROM_I2C_ADDR = 0x57             # I2C address for the EEPROM (adjust based on address pins)

# -------------------------
# NeoPixel Colors and Animation Settings
# -------------------------
MACSAO_ADDRESS = 0x0A              # I2C address for the MacSAO
BLINKY_LOOP_NUM_PIXELS = 12        # Number of NeoPixels (redundant, same as above)
BLINKY_LOOP_PIN_NUM = 22           # GPIO pin number (redundant, same as above)

# -------------------------
# EEPROM Configuration
# -------------------------
EEPROM_SIZE = 4096                  # Total size of EEPROM in bytes (4KB)
PAGE_SIZE = 32                      # EEPROM page size in bytes

# -------------------------
# Screen Dimensions
# -------------------------
SCREEN_WIDTH = 64                   # Width of the OLED display in pixels
SCREEN_HEIGHT = 48                  # Height of the OLED display in pixels

# -------------------------
# Animation Settings
# -------------------------
RADIUS = 5                          # Radius for circle animations
ANIMATION_CYCLES = 10               # Number of animation cycles for Pong
MAX_BOUNCES = 20                    # Maximum number of bounces in Pong animation

# =========================
# Initialization and Setup
# =========================

# -------------------------
# Initialize NeoPixel
# -------------------------
np = neopixel.NeoPixel(machine.Pin(BLINKY_LOOP_PIN_NUM), BLINKY_LOOP_NUM_PIXELS)

# -------------------------
# Initialize I2C Buses
# -------------------------
i2c0 = I2C(0, sda=Pin(0), scl=Pin(1), freq=400_000)    # I2C0 for ports 1-3
i2c1 = I2C(1, sda=Pin(26), scl=Pin(27), freq=400_000)  # I2C1 for ports 4-6

# -------------------------
# Initialize OLED Display on I2C0
# -------------------------
display = ssd1306.SSD1306_I2C(128, 64, i2c0)

# -------------------------
# Initialize Etch SAO on I2C1
# -------------------------
etch_sao_sketch = etch.Etch(i2c1)
etch_sao_sketch.shake()  # Clear the Etch SAO display

# -------------------------
# Initialize Boot LED
# -------------------------
bootLED = Pin("LED", Pin.OUT)
bootLED.on()  # Turn on boot LED to indicate startup

# -------------------------
# Initialize Buttons with Pull-Up Resistors
# -------------------------
buttonA = Pin(8, Pin.IN, Pin.PULL_UP)   # Button A for navigation
buttonB = Pin(9, Pin.IN, Pin.PULL_UP)   # Button B for selection
buttonC = Pin(28, Pin.IN, Pin.PULL_UP)  # Button C for returning to menu

# -------------------------
# Initialize GPIOs for Add-Ons
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

# Group GPIOs for easy access
GPIOs = [
    [gpio11, gpio12],
    [gpio21, gpio22],
    [gpio31, gpio32],
    [gpio41, gpio42],
    [gpio51, gpio52]
    # [gpio61, gpio62],  # Uncomment if needed
]

# -------------------------
# Initialize Petal SAO
# -------------------------
def petal_init(bus):
    """Configure the Petal SAO with initial settings."""
    bus.writeto_mem(PETAL_ADDRESS, 0x09, bytes([0x00]))  # Set to raw pixel mode
    bus.writeto_mem(PETAL_ADDRESS, 0x0A, bytes([0x09]))  # Set intensity to 16
    bus.writeto_mem(PETAL_ADDRESS, 0x0B, bytes([0x07]))  # Enable all segments
    bus.writeto_mem(PETAL_ADDRESS, 0x0C, bytes([0x81]))  # Undo shutdown bits
    bus.writeto_mem(PETAL_ADDRESS, 0x0D, bytes([0x00]))  # Default settings
    bus.writeto_mem(PETAL_ADDRESS, 0x0E, bytes([0x00]))  # Default features
    bus.writeto_mem(PETAL_ADDRESS, 0x0F, bytes([0x00]))  # Turn off display test mode

# Attempt to initialize Petal on both I2C buses
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

# Configure Petal LEDs if found
if petal_bus:
    petal_bus.writeto_mem(PETAL_ADDRESS, 3, bytes([0x80]))
    petal_bus.writeto_mem(PETAL_ADDRESS, 2, bytes([0x80]))
    petal_bus.writeto_mem(PETAL_ADDRESS, 3, bytes([0x00]))
    petal_bus.writeto_mem(PETAL_ADDRESS, 2, bytes([0x80]))
    time.sleep_ms(200)
    petal_bus.writeto_mem(PETAL_ADDRESS, 2, bytes([0x00]))

# -------------------------
# Initialize Touchwheel on I2C0 or I2C1
# -------------------------
touchwheel_bus = None
touchwheel_counter = 0
while not touchwheel_bus:
    try:
        if TOUCHWHEEL_ADDRESS in i2c0.scan():
            touchwheel_bus = i2c0
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

# Configure Petal LEDs if both Touchwheel and Petal are present
if touchwheel_bus and petal_bus:
    petal_bus.writeto_mem(PETAL_ADDRESS, 3, bytes([0x00]))
if petal_bus:
    petal_bus.writeto_mem(PETAL_ADDRESS, 2, bytes([0x80]))
    time.sleep_ms(200)
    petal_bus.writeto_mem(PETAL_ADDRESS, 2, bytes([0x00]))

# =========================
# Helper Functions
# =========================

def clear_pixels():
    """Turn off all NeoPixels in the BlinkyLoop."""
    for i in range(BLINKY_LOOP_NUM_PIXELS):
        np[i] = (0, 0, 0)
    np.write()

def theater_chase(color, wait=50, iterations=2):
    """
    Perform a theater light-style chaser animation.

    Args:
        color (tuple): RGB color tuple for the chasing effect.
        wait (int): Delay in milliseconds between frames.
        iterations (int): Number of iterations for the chase.
    """
    for _ in range(iterations):
        for q in range(3):
            for i in range(BLINKY_LOOP_NUM_PIXELS):
                if (i + q) % 3 == 0:
                    np[i] = color
                else:
                    np[i] = (0, 0, 0)
            np.write()
            time.sleep_ms(wait)
    clear_pixels()

def rainbow_cycle(wait=10):
    """
    Display a rainbow animation across all NeoPixels.

    Args:
        wait (int): Delay in milliseconds between frames.
    """
    for j in range(256):
        for i in range(BLINKY_LOOP_NUM_PIXELS):
            idx = (i * 256 // BLINKY_LOOP_NUM_PIXELS) + j
            np[i] = wheel(idx & 255)
        np.write()
        time.sleep_ms(wait)

def wheel(pos):
    """
    Generate rainbow colors across 0-255 positions.

    Args:
        pos (int): Position on the color wheel (0-255).

    Returns:
        tuple: RGB color tuple.
    """
    if pos < 85:
        return (pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return (255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return (0, pos * 3, 255 - pos * 3)

def color_pixels(color):
    """
    Set all NeoPixels to the specified color.

    Args:
        color (tuple): RGB color tuple.
    """
    for i in range(BLINKY_LOOP_NUM_PIXELS):
        np[i] = color
    np.write()

# Clear NeoPixels at startup
clear_pixels()

# =========================
# I2C Communication Functions
# =========================

def send_payload(payload, description):
    """
    Send a payload via I2C to the MacSAO and handle exceptions.

    Args:
        payload (bytes): Data payload to send.
        description (str): Description of the payload for debugging.
    """
    try:
        i2c1.writeto(MACSAO_ADDRESS, payload)
        # Uncomment the line below to enable debug messages
        # print(f"Sent: {description}")
    except Exception as e:
        print(f"Failed to send {description}: {e}")

def create_rectangle_payload(x, y, width, height, color):
    """
    Create a payload to draw a filled rectangle.

    Parameters:
        x (int): Top-left x-coordinate.
        y (int): Top-left y-coordinate.
        width (int): Width of the rectangle.
        height (int): Height of the rectangle.
        color (int): 0 for black, 1 for white.

    Returns:
        bytes: The payload to send via I2C.
    """
    return bytes([0x01, 0x02, 0x0C, x, y, width, height, color, 0xFE])

def map_y(input_val, screen_height=48, rect_height=15):
    """
    Map an input value between 0 and 128 to a Y-coordinate.

    Parameters:
        input_val (int): Input value between 0 and 128.
        screen_height (int): Height of the screen in pixels.
        rect_height (int): Height of the rectangle in pixels.

    Returns:
        int: Mapped Y-coordinate.
    """
    y = int((input_val / 128) * screen_height)
    y = max(0, min(y, screen_height - rect_height))
    return y

def screen_saver(y_left, y_right):
    """
    Draw the current frame of the screensaver with two rectangles.

    Parameters:
        y_left (int): Y-coordinate for the left rectangle.
        y_right (int): Y-coordinate for the right rectangle.
    """
    # Set MODE to LIVEDRIVE (1)
    payload_set_mode = bytes([0x05, 0x01, 0x01])
    send_payload(payload_set_mode, "Set MODE to LIVEDRIVE (1)")
    time.sleep(0.02)

    # Set Mouse Position to (0, 0)
    payload_set_mouse_position = bytes([0x05, 0x02, 0x00, 0x00])
    send_payload(payload_set_mouse_position, "Reset Mouse Position to (0,0)")
    time.sleep(0.02)

    # Define Rectangle Payloads
    payload_draw_left_rect = create_rectangle_payload(
        x=0, y=y_left, width=5, height=15, color=0x00
    )
    payload_draw_right_rect = create_rectangle_payload(
        x=59, y=y_right, width=5, height=15, color=0x00
    )

    # Draw the rectangles
    send_payload(payload_draw_left_rect, f"Draw Left Rectangle at (0,{y_left})")
    send_payload(payload_draw_right_rect, f"Draw Right Rectangle at (59,{y_right})")

def screen_saver_circle(x, y, radius):
    """
    Draw a circle at the specified position.

    Parameters:
        x (int): X-coordinate of the circle's center.
        y (int): Y-coordinate of the circle's center.
        radius (int): Radius of the circle.
    """
    # Payload to draw the circle
    payload_draw_circle = bytes([0x01, 0x02, 0x0F, x, y, radius, 0x01, 0xFE])
    send_payload(payload_draw_circle, f"Draw Circle at ({x},{y})")
    time.sleep(0.02)  # Short delay

# =========================
# Event Handling and EEPROM Management
# =========================

class Event:
    """Class to represent an event with its details."""
    def __init__(self, event_name, start_time, end_time, speaker_name, description):
        self.event_name = event_name
        self.start_time = start_time  # Epoch time
        self.end_time = end_time      # Epoch time
        self.speaker_name = speaker_name
        self.description = description

def dec_to_bcd(val):
    """Convert decimal to BCD."""
    return (val // 10 << 4) + (val % 10)

def bcd_to_dec(val):
    """Convert BCD to decimal."""
    return ((val >> 4) * 10) + (val & 0x0F)

def set_time(year, month, date, day, hour, minute, second):
    """
    Set the DS3231 RTC time.

    Parameters:
        year (int): Full year (e.g., 2024).
        month (int): Month (1-12).
        date (int): Day of the month (1-31).
        day (int): Day of the week (1-7, Sunday=1).
        hour (int): Hour (0-23).
        minute (int): Minute (0-59).
        second (int): Second (0-59).
    """
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
    """
    Read the current time from DS3231 RTC.

    Returns:
        tuple or None: (year, month, date, day, hour, minute, second) or None if failed.
    """
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
    """
    Read the temperature from DS3231 RTC.

    Returns:
        float or None: Temperature in °C or None if failed.
    """
    try:
        temp_msb = i2c0.readfrom_mem(DS3231_I2C_ADDR, 0x11, 1)[0]
        temp_lsb = i2c0.readfrom_mem(DS3231_I2C_ADDR, 0x12, 1)[0]
        temp = temp_msb + ((temp_lsb >> 6) * 0.25)
        print(f"Read Temperature: {temp:.2f}°C")
        return temp
    except OSError as e:
        print("Failed to read temperature:", e)
        return None

def write_bytes_to_eeprom(address, data):
    """
    Write bytes to EEPROM starting at the specified address.

    Parameters:
        address (int): Starting address in EEPROM.
        data (bytes): Data to write.
    """
    while data:
        chunk = data[:PAGE_SIZE]
        data = data[PAGE_SIZE:]
        try:
            # Use writeto_mem with two-byte address
            i2c0.writeto_mem(EEPROM_I2C_ADDR, address, chunk, addrsize=16)
            time.sleep_ms(10)  # Ensure EEPROM write cycle completes
            address += len(chunk)
        except OSError as e:
            print("Failed to write to EEPROM:", e)
            break
    print("Bytes written to EEPROM successfully.")

def read_bytes_from_eeprom(address, length):
    """
    Read bytes from EEPROM starting at the specified address.

    Parameters:
        address (int): Starting address in EEPROM.
        length (int): Number of bytes to read.

    Returns:
        bytes or None: Data read from EEPROM or None if failed.
    """
    try:
        data = i2c0.readfrom_mem(EEPROM_I2C_ADDR, address, length, addrsize=16)
        return data
    except OSError as e:
        print("Failed to read from EEPROM:", e)
        return None

def wipe_eeprom():
    """Erase all data in the EEPROM without user confirmation."""
    print("Wiping EEPROM...")
    for addr in range(0, EEPROM_SIZE, PAGE_SIZE):
        remaining = EEPROM_SIZE - addr
        chunk_size = PAGE_SIZE if remaining >= PAGE_SIZE else remaining
        chunk = bytearray([0xFF] * chunk_size)
        try:
            write_bytes_to_eeprom(addr, chunk)
        except Exception as e:
            print(f"Failed to wipe EEPROM at address {addr}: {e}")
            return
    print("EEPROM wiped successfully.")

def write_string_to_eeprom(address, string):
    """
    Write a string to EEPROM at the specified address.

    Parameters:
        address (int): Starting address in EEPROM.
        string (str): String to write.
    """
    data = string.encode('utf-8')
    write_bytes_to_eeprom(address, data)
    print("String written to EEPROM successfully.")

def read_string_from_eeprom(address, length):
    """
    Read a string from EEPROM starting at the specified address.

    Parameters:
        address (int): Starting address in EEPROM.
        length (int): Number of bytes to read.

    Returns:
        str or None: Decoded string or None if failed.
    """
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

def save_event_to_eeprom(event, address):
    """
    Serialize and save an event to EEPROM at the specified address.

    Parameters:
        event (Event): Event object to save.
        address (int): Starting EEPROM address.
    """
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

    # Optional Verification
    verification_data = read_bytes_from_eeprom(address, len(data))
    if verification_data == data:
        print("Verification Successful: Data written correctly.")
    else:
        print("Verification Failed: Data mismatch.")

def load_event_from_eeprom(address):
    """
    Load and deserialize an event from EEPROM starting at the specified address.

    Parameters:
        address (int): Starting EEPROM address.

    Returns:
        Event or None: Loaded event object or None if failed.
    """
    # Read Event Name Length
    event_name_length_bytes = read_bytes_from_eeprom(address, 1)
    if event_name_length_bytes is None:
        print("Failed to read event name length.")
        return None
    event_name_length = event_name_length_bytes[0]

    # Check if the entire event slot is empty
    if event_name_length == 0xFF:
        print(f"Event slot at address {address} is empty.")
        return None

    # Validate event_name_length
    if event_name_length == 0 or event_name_length > 50:
        print(f"Invalid event name length ({event_name_length}) at address {address}.")
        return None
    address += 1

    # Read Event Name
    event_name = read_string_from_eeprom(address, event_name_length)
    if event_name is None:
        print(f"Invalid event name at address {address}.")
        return None
    address += event_name_length

    # Read Start Time
    start_time_bytes = read_bytes_from_eeprom(address, 4)
    if start_time_bytes is None or len(start_time_bytes) != 4:
        print("Failed to read start time.")
        return None
    start_time = int.from_bytes(start_time_bytes, 'big')
    address += 4

    # Read End Time
    end_time_bytes = read_bytes_from_eeprom(address, 4)
    if end_time_bytes is None or len(end_time_bytes) != 4:
        print("Failed to read end time.")
        return None
    end_time = int.from_bytes(end_time_bytes, 'big')
    address += 4

    # Read Speaker Name Length
    speaker_name_length_bytes = read_bytes_from_eeprom(address, 1)
    if speaker_name_length_bytes is None:
        print("Failed to read speaker name length.")
        return None
    speaker_name_length = speaker_name_length_bytes[0]

    # Validate speaker_name_length
    if speaker_name_length == 0 or speaker_name_length > 50:
        print(f"Invalid speaker name length ({speaker_name_length}) at address {address}.")
        return None
    address += 1

    # Read Speaker Name
    speaker_name = read_string_from_eeprom(address, speaker_name_length)
    if speaker_name is None:
        print(f"Invalid speaker name at address {address}.")
        return None
    address += speaker_name_length

    # Read Description Length
    description_length_bytes = read_bytes_from_eeprom(address, 2)
    if description_length_bytes is None or len(description_length_bytes) != 2:
        print("Failed to read description length.")
        return None
    description_length = int.from_bytes(description_length_bytes, 'big')

    # Validate description_length
    if description_length == 0 or description_length > 138:
        print(f"Invalid description length ({description_length}) at address {address}.")
        return None
    address += 2

    # Read Description
    description = read_string_from_eeprom(address, description_length)
    if description is None:
        print(f"Invalid description at address {address}.")
        return None
    address += description_length

    # Create Event object
    event = Event(event_name, start_time, end_time, speaker_name, description)
    print("Event loaded successfully.")
    return event

# =========================
# Touchwheel Functions
# =========================

def touchwheel_read(bus):
    """
    Read the touchwheel input.

    Returns:
        int: 0 for no touch, 1-255 clockwise around the circle from the south.
    """
    return bus.readfrom_mem(TOUCHWHEEL_ADDRESS, 0, 1)[0]

def touchwheel_rgb(bus, r, g, b):
    """
    Set RGB color on the central display of the Touchwheel.

    Parameters:
        r (int): Red value (0-255).
        g (int): Green value (0-255).
        b (int): Blue value (0-255).
    """
    bus.writeto_mem(TOUCHWHEEL_ADDRESS, 15, bytes([r]))
    bus.writeto_mem(TOUCHWHEEL_ADDRESS, 16, bytes([g]))
    bus.writeto_mem(TOUCHWHEEL_ADDRESS, 17, bytes([b]))

# =========================
# I2C Device Scanning and Display
# =========================

# -------------------------
# Device Names Mapping for I2C0 and I2C1
# -------------------------
device_names_i2c0 = {
    0x54: "Touchwheel",
    0x55: "BadgeTagNFC",
    0x15: "Skull of Fate",
    0x14: "Skull of Fate",
    0x13: "Skull of Fate",
    0x18: "Blinky Loop",
    0x57: "Calendar",
    0x0A: "Mac SAO"
}

device_names_i2c1 = {
    0x54: "Touchwheel",
    0x55: "BadgeTagNFC",
    0x15: "Skull of Fate",
    0x14: "Skull of Fate",
    0x13: "Skull of Fate",
    0x18: "Blinky Loop",
    0x19: "Etch sAo Sketch",  # Port 6
    0x57: "Calendar",
    0x0A: "Mac SAO"
}

# -------------------------
# Devices to Exclude from Display
# -------------------------
exclude_list = {
    0x3C: "OLED Display",
    0x68: "EEPROM Calendar"
}

# -------------------------
# Detailed Device Information
# -------------------------
device_info = {
    0x18: "BlinkyLoop by Flummer.",
    (0x19, "i2c1"): "Etch sAo Sketch by Core64.",
    0x54: "TouchwheelSAO by @todbot github.com/todbot/TouchWheelSAO",
    0x55: "BadgeTagNFC is a versatile NFC badge.",
    0x15: "Skull of Fate by p1x317h13f and MakeItHackin.",
    0x14: "Skull of Fate by p1x317h13f and MakeItHackin.",
    0x13: "Skull of Fate by p1x317h13f and MakeItHackin.",
    0x57: "Calendar by DaveDarko",
    0x0A: "Mac SAO by SirCastor"
}

def scan_devices():
    """
    Scan both I2C buses and return a list of detected devices excluding certain addresses.

    Returns:
        list: List of detected devices with their addresses, names, and bus.
    """
    detected_devices = []

    # Scan I2C0
    i2c0_array = i2c0.scan()
    for device in i2c0_array:
        if device not in exclude_list and device not in [d["address"] for d in detected_devices]:
            if device in device_names_i2c0:
                detected_devices.append({"address": device, "name": device_names_i2c0[device], "bus": "i2c0"})
            else:
                detected_devices.append({"address": device, "name": hex(device), "bus": "i2c0"})

    # Scan I2C1
    i2c1_array = i2c1.scan()
    for device in i2c1_array:
        if device not in exclude_list and device not in [d["address"] for d in detected_devices]:
            if device in device_names_i2c1:
                detected_devices.append({"address": device, "name": device_names_i2c1[device], "bus": "i2c1"})
            else:
                detected_devices.append({"address": device, "name": hex(device), "bus": "i2c1"})

    return detected_devices

def display_details(device):
    """
    Display detailed information of a specific device on the OLED.

    Parameters:
        device (dict): Device information containing address, name, and bus.
    """
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

def display_list(devices, current_selection):
    """
    Display the list of detected I2C devices with the current selection highlighted.

    Parameters:
        devices (list): List of detected devices.
        current_selection (int): Index of the currently selected device.
    """
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

def display_details(device):
    """
    Display detailed information about a specific I2C device on the OLED.

    Parameters:
        device (dict): Device information containing address, name, and bus.
    """
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

# =========================
# I2C Device Command Functions
# =========================

def send_i2c_command(command_char, data_bytes=None, response_length=1):
    """
    Send a command over I2C to the client and receive response if expected.

    Args:
        command_char (str): The command character to send.
        data_bytes (bytes): Additional data bytes to send.
        response_length (int): Number of bytes expected in response.
    """
    print(f"Sending command: {command_char}")
    data_to_send = bytes([ord(command_char)])
    if data_bytes:
        data_to_send += data_bytes
    try:
        i2c0.writeto(0x13, data_to_send)

        # Optional: Wait for a response from the CLIENT
        time.sleep(0.1)  # Small delay to allow CLIENT to respond

        # Read the expected number of bytes from the CLIENT
        if response_length > 0:
            data_received = i2c0.readfrom(0x13, response_length)
            if data_received:
                decode_response(command_char, data_received)
            else:
                print("No data received from CLIENT.")
        else:
            print("No data expected from CLIENT.")

    except Exception as e:
        print(f"Error sending data over I2C: {e}")

def decode_response(command_char, data):
    """
    Decode the response data based on the command sent.

    Args:
        command_char (str): The command character sent.
        data (bytes): The data received from the client.
    """
    if command_char == '3':
        # Magnetic sensor data (1 byte)
        magnetic_field_detected = bool(data[0])
        print(f"Magnetic Field Detected: {magnetic_field_detected} {data[0]}")
    elif command_char == '4':
        # Accelerometer data (12 bytes)
        if len(data) != 12:
            print("Error: Incorrect data length for accelerometer data.")
            return
        x = float_from_bytes(data[0:4])
        y = float_from_bytes(data[4:8])
        z = float_from_bytes(data[8:12])
        print(f"Accelerometer Data - X: {x:.2f}, Y: {y:.2f}, Z: {z:.2f}")
    elif command_char == '5':
        # Button states (1 byte)
        buttons = data[0]
        left_button = bool(buttons & 0x01)
        right_button = bool(buttons & 0x02)
        print(f"Left Button: {'Pressed' if left_button else 'Released'}, Right Button: {'Pressed' if right_button else 'Released'}")
    elif command_char == '6':
        # PDM Microphone data (4 bytes)
        if len(data) != 4:
            print("Error: Incorrect data length for microphone data.")
            return
        volume = float_from_bytes(data)
        print(f"Microphone Volume: {volume:.2f}")
    else:
        # Default response handling
        status = data[0]
        print(f"Received status from CLIENT: {chr(status)}")

def float_from_bytes(bytes_data):
    """
    Convert 4 bytes to a float. Placeholder function.

    Parameters:
        bytes_data (bytes): 4 bytes representing a float.

    Returns:
        float: Converted float value.
    """
    # Placeholder implementation. Replace with actual conversion as needed.
    import struct
    return struct.unpack('f', bytes_data)[0]

# =========================
# Event Display Functions
# =========================

def display_event(event):
    """
    Display event details with a countdown on the OLED.

    Parameters:
        event (Event): Event object containing event details.
    """
    try:
        # Clear the display
        display.fill(0)

        # Get the current time from the RTC
        time_data = read_time()
        if time_data:
            (year, month, date, day, hour, minute, second) = time_data

            # Adjust the day of the week to match Python's convention (Monday=0)
            # DS3231 RTC day starts from 1 (Sunday) to 7 (Saturday)
            weekday = (day + 5) % 7  # Converts 1-7 (Sun-Sat) to 0-6 (Mon-Sun)

            # Construct time tuple for mktime
            time_tuple = (year, month, date, hour, minute, second, weekday, -1)
            current_time = time.mktime(time_tuple)
        else:
            # If reading time failed, handle appropriately
            current_time = 0  # Or consider skipping the update
            print("Failed to read current time from RTC.")

        time_left = event.start_time - current_time

        # Determine what to display based on the countdown
        if time_left > 600:  # More than 10 minutes
            hours, remainder = divmod(time_left, 3600)
            minutes, seconds = divmod(remainder, 60)
            countdown_string = "Starts {:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds))
            display.text(countdown_string, 0, 0, 1)
        elif time_left > 595:
            countdown_string = "10 Minutes!"
            display.text(countdown_string, 0, 0, 1)
            #rainbow_cycle()
            theater_chase((128, 128, 0))
            #clear_pixels()
        elif time_left > 0:
            hours, remainder = divmod(time_left, 3600)
            minutes, seconds = divmod(remainder, 60)
            countdown_string = "Starts {:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds))
            display.text(countdown_string, 0, 0, 1)
        else:
            countdown_string = "Event started!"
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

def display_no_event():
    """Display a message indicating no event is scheduled."""
    try:
        display.fill(0)
        display.text("No Event Scheduled", 0, 0, 1)
        display.show()
    except OSError as e:
        print(f"OSError while displaying no event: {e}")

def display_main_menu(options, selection):
    """
    Display the main menu with given options and current selection.

    Parameters:
        options (list): List of menu options.
        selection (int): Current menu selection index.
    """
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

# =========================
# Menu and Mode Definitions
# =========================

# Define display modes
MODE_MAIN_MENU = 0
MODE_I2C_DETECT = 1
MODE_I2C_DETAIL = 2
MODE_EVENT_DISPLAY = 3
MODE_PONG_DISPLAY = 4

# =========================
# Pong Animation Function
# =========================

def pong():
    """
    Initialize I2C and start the pong animation with moving circles and rectangles.
    """
    print("Initializing I2C and starting the screensaver...")

    # Set MODE to LIVEDRIVE (1)
    payload_set_mode = bytes([0x05, 0x01, 0x01])
    send_payload(payload_set_mode, "Set MODE to LIVEDRIVE (1)")
    time.sleep(0.1)

    # Set Mouse Position to (0, 0)
    payload_set_mouse_position = bytes([0x05, 0x02, 0x00, 0x00])
    send_payload(payload_set_mouse_position, "Set Mouse Position to (0,0)")
    time.sleep(0.1)

    # Circle parameters
    x = SCREEN_WIDTH // 2  # Start at center x = 32
    y = SCREEN_HEIGHT // 2  # Start at center y = 24
    vx = 1  # Initial x velocity
    vy = 1  # Initial y velocity

    # Animation cycles
    for cycle in range(ANIMATION_CYCLES):
        print(f"Starting animation cycle {cycle + 1}/{ANIMATION_CYCLES}")
        # Reset circle to center for each cycle
        x = SCREEN_WIDTH // 2
        y = SCREEN_HEIGHT // 2
        vx = 1
        vy = 1
        bounce_count = 0

        # Rectangle movement variables
        y_left_input = 64  # Start at middle input value
        y_right_input = 64  # Start at middle input value
        y_left_direction = 1  # 1 for increasing, -1 for decreasing
        y_right_direction = -1  # Start moving in opposite direction
        step = 2  # Input step per frame

        while bounce_count < MAX_BOUNCES:
            # Update circle position
            x += vx
            y += vy

            # Bounce off the vertical walls
            if x + RADIUS >= SCREEN_WIDTH or x - RADIUS <= 0:
                vx = -vx
                bounce_count += 1
                print(f"Bounce count: {bounce_count} (Vertical)")

            # Bounce off the horizontal walls
            if y + RADIUS >= SCREEN_HEIGHT or y - RADIUS <= 0:
                vy = -vy
                bounce_count += 1
                print(f"Bounce count: {bounce_count} (Horizontal)")

            # Ensure the circle stays within bounds after bouncing
            x = max(RADIUS, min(x, SCREEN_WIDTH - RADIUS))
            y = max(RADIUS, min(y, SCREEN_HEIGHT - RADIUS))

            # Draw the circle at the new position
            screen_saver_circle(x, y, RADIUS)

            # Update left rectangle input and direction
            y_left_input += y_left_direction * step
            if y_left_input >= 128:
                y_left_input = 128
                y_left_direction = -1
            elif y_left_input <= 0:
                y_left_input = 0
                y_left_direction = 1

            # Update right rectangle input and direction
            y_right_input += y_right_direction * step
            if y_right_input >= 128:
                y_right_input = 128
                y_right_direction = -1
            elif y_right_input <= 0:
                y_right_input = 0
                y_right_direction = 1

            # Map input values to y-coordinates
            y_left = map_y(y_left_input, SCREEN_HEIGHT, 15)
            y_right = map_y(y_right_input, SCREEN_HEIGHT, 15)

            # Draw the rectangles with updated y positions
            screen_saver(y_left, y_right)

            # Delay between frames
            time.sleep(0.02)

# =========================
# Main Loop and User Interaction
# =========================

def main():
    """
    Main function to handle menu navigation and user interactions.
    """
    # Initialize variables for main menu
    current_mode = MODE_MAIN_MENU
    main_menu_options = ["I2C Detect", "Event Display", "Pong"]
    main_menu_selection = 0
    main_menu_length = len(main_menu_options)

    # Initialize variables for I2C navigation
    i2c_devices = scan_devices()
    i2c_selection = 0

    # Event object placeholder
    event = None

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
        elif current_mode == MODE_PONG_DISPLAY:
            pass  # Pong is handled within its own function

        # Read touchwheel input
        touchsignal = touchwheel_read(touchwheel_bus) if touchwheel_bus else 0

        if touchsignal > 128:
            send_i2c_command('1', bytes([255]))
            # theater_chase((0, 0, 128))

        # Update Etch SAO Sketch with touchwheel input
        if etch_sao_sketch:
            x = etch_sao_sketch.left
            y = etch_sao_sketch.right
            y = 128 - y  # Invert control

            print(x, y)
            etch_sao_sketch.draw_pixel(x, y, 1)
            etch_sao_sketch.draw_display()

            y_left_input = x
            y_right_input = y

        # Handle button presses with debounce
        if buttonA.value() == 0:  # Button A: Move selection down
            if current_mode == MODE_MAIN_MENU:
                main_menu_selection = (main_menu_selection + 1) % main_menu_length
            elif current_mode == MODE_I2C_DETECT:
                if i2c_devices:
                    i2c_selection = (i2c_selection + 1) % len(i2c_devices)
            time.sleep(0.2)  # Debounce delay

        elif buttonB.value() == 0:  # Button B: Select
            if current_mode == MODE_MAIN_MENU:
                selected_option = main_menu_options[main_menu_selection]
                if selected_option == "I2C Detect":
                    current_mode = MODE_I2C_DETECT
                    i2c_selection = 0  # Reset selection
                elif selected_option == "Event Display":
                    current_mode = MODE_EVENT_DISPLAY
                    reset_time_and_event()
                    # Load an event (for demonstration purposes, loading from address 0)
                    event = load_event_from_eeprom(0)  # Modify as needed
                elif selected_option == "Pong":
                    current_mode = MODE_PONG_DISPLAY
                    pong()
            elif current_mode == MODE_I2C_DETECT:
                if i2c_devices:
                    current_mode = MODE_I2C_DETAIL
            elif current_mode == MODE_I2C_DETAIL:
                pass  # Implement actions if needed
            elif current_mode == MODE_EVENT_DISPLAY:
                pass  # Implement actions if needed
            elif current_mode == MODE_PONG_DISPLAY:
                pass  # Implement actions if needed
            time.sleep(0.2)  # Debounce delay

        elif buttonC.value() == 0:  # Button C: Return to Main Menu or previous menu
            clear_pixels()
            if current_mode == MODE_I2C_DETAIL:
                current_mode = MODE_I2C_DETECT  # Return to I2C Detect device list
            elif current_mode in [MODE_I2C_DETECT, MODE_EVENT_DISPLAY]:
                current_mode = MODE_MAIN_MENU  # Return to Main Menu
            elif current_mode == MODE_MAIN_MENU:
                pass  # Optionally implement exit or do nothing
            time.sleep(0.2)  # Debounce delay

        # Add a small sleep to avoid excessive CPU usage
        time.sleep(0.05)

# =========================
# Utility Functions
# =========================

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

def reset_time_and_event():
    """
    Reset the RTC time and initialize an event.
    """
    # Wipe EEPROM without confirmation (Uncomment if needed)
    # wipe_eeprom()
    
    # Set time to November 3, 2024 at 4:49:30 PM
    year = 2024
    month = 11
    date = 3
    day = 7  # Sunday
    hour = 16  # 4 PM in 24-hour format
    minute = 49
    second = 30

    set_time(year, month, date, day, hour, minute, second)
    
    # Read back time and print
    time_data = read_time()
    if time_data:
        year, month, date, day, hour, minute, second = time_data
        print("Current time set to: {:04}-{:02}-{:02} {:02}:{:02}:{:02}".format(
            year, month, date, hour, minute, second))
    else:
        print("Failed to read time from RTC.")

    # Example: Create and save an event
    '''
    event_name = "Ceremony"
    start_time_tuple = (2024, 11, 3, 17, 0, 0, 0, 0)
    start_time = int(time.mktime(start_time_tuple))
    end_time_tuple = (2024, 11, 3, 18, 0, 0, 0, 0)
    end_time = int(time.mktime(end_time_tuple))
    speaker_name = "Elliot"
    description = "Badges!"
    event = Event(event_name, start_time, end_time, speaker_name, description)
    address = 0
    save_event_to_eeprom(event, address)
    event_loaded = load_event_from_eeprom(address)
    if event_loaded:
        print("\nEvent Details Loaded from EEPROM:")
        print("Event Name:", event_loaded.event_name)
        start_tuple = time.localtime(event_loaded.start_time)
        print("Start Time: {:04}-{:02}-{:02} {:02}:{:02}:{:02}".format(
            start_tuple[0], start_tuple[1], start_tuple[2], start_tuple[3], start_tuple[4], start_tuple[5]))
        end_tuple = time.localtime(event_loaded.end_time)
        print("End Time: {:04}-{:02}-{:02} {:02}:{:02}:{:02}".format(
            end_tuple[0], end_tuple[1], end_tuple[2], end_tuple[3], end_tuple[4], end_tuple[5]))
        print("Speaker Name:", event_loaded.speaker_name)
        print("Description:", event_loaded.description)
    else:
        print("Failed to load event from EEPROM.")
    '''

# =========================
# Run the Main Function
# =========================

if __name__ == "__main__":
    # Uncomment the following line to create a test event
    # create_test_event()
    main()
