"""
Supercon 8 Conference Badge Boot Script
---------------------------------------
Author: Elliot Williams and Contributors
Date: November 1-3, 2024
Location: Pasadena, CA
Event: Supercon 8, organized by Hackaday

Description:
This MicroPython boot script initializes the hardware components of the Raspberry Pi Pico Wireless badge used at Supercon 8.
It sets up I2C buses, configures GPIO pins for buttons and add-on ports, and initializes peripheral devices such as the petal controller and touch wheel.


Code Sections and Descriptions
Header and Metadata

Purpose: Provides an overview of the script, including authorship, date, event details, and a high-level description of the badge's boot process.
Content: Comments at the top of the script detailing the script's purpose and context.
Imports and Constants

Purpose: Imports necessary modules and defines constant values used throughout the script.
Content:
from machine import I2C, Pin: Imports classes for I2C communication and GPIO pin control.
import time: Imports time module for delays.
Defines I2C addresses (PETAL_ADDRESS, TOUCHWHEEL_ADDRESS).
GPIO Pin Definitions

Purpose: Configures the GPIO pins for buttons, LEDs, and add-on ports.
Content:
Boot LED: Indicates the initialization status.
Buttons: Configures three buttons (A, B, C) with internal pull-up resistors.
General Purpose I/O (GPIO): Sets up pairs of GPIO pins for each of the six add-on ports.
GPIOs List: Groups GPIO pairs into a list for easier management.
I2C Bus Initialization

Purpose: Sets up the two I2C buses used by the badge for different add-on ports.
Content:
Initializes i2c0 for ports 1-3 with specified SDA and SCL pins.
Initializes i2c1 for ports 4-6 with specified SDA and SCL pins.
Helper Functions

Purpose: Provides reusable functions to handle common tasks such as scanning I2C buses and interacting with peripherals.
Content:
which_bus_has_device_id: Scans both I2C buses to determine which bus(es) contain a device with a specific I2C address.
petal_init: Initializes the Petal controller by configuring its registers via I2C.
touchwheel_read: Reads the current value from the Touch Wheel device.
touchwheel_rgb: Sets the RGB color on the Touch Wheel's central display.
Peripheral Initialization

Purpose: Initializes and configures the Petal controller and Touch Wheel devices.
Content:
Petal Controller Initialization:
Attempts to initialize the Petal controller on i2c0.
If unsuccessful, attempts to initialize on i2c1.
Prints warnings if the Petal controller is not found.
Indicator Setup:
If the Petal controller is initialized, sets indicators (e.g., yellow light) to indicate waiting status.
Touch Wheel Initialization:
Continuously scans for the Touch Wheel device with a maximum number of retries to prevent infinite loops.
Sets touchwheel_bus if the Touch Wheel is found.
Prints warnings if the Touch Wheel is not found after retries.
Final Configuration

Purpose: Performs any final setup steps after peripheral initialization.
Content:
If both Petal and Touch Wheel are initialized, sets the Petal controller to indicate successful configuration (e.g., changes to green).
Turns off the Boot LED to signify the end of the boot sequence.
Prints a completion message to the console.
Additional Notes
Error Handling:

The script includes try-except blocks to gracefully handle errors during I2C communication and device initialization.
Warnings are printed if critical peripherals like the Petal controller or Touch Wheel are not found.
Debugging Aids:

The which_bus_has_device_id function can print the devices found on each I2C bus if debug is set to True.
Print statements throughout the script provide real-time feedback on the initialization process.
Timeout Mechanism:

The Touch Wheel initialization includes a retry mechanism with a maximum number of attempts (MAX_TOUCHWHEEL_RETRIES) to prevent the script from hanging indefinitely if the Touch Wheel is not detected.
GPIO Management:

GPIO pins are organized into a list (GPIOs) to facilitate easy access and potential future expansions, such as iterating over ports for configuration or status checks.
Extensibility:

The structured approach with helper functions and organized sections makes it straightforward to add new peripherals or modify existing configurations.
Additional features, such as more sophisticated LED patterns or interaction mechanisms, can be integrated without disrupting the existing initialization flow.
Customization:

Constants like PETAL_ADDRESS, GPIO pin numbers, and I2C configurations should be verified and adjusted according to the actual hardware setup and device specifications.
Performance Considerations:

Delays (time.sleep_ms) are used judiciously to ensure proper timing during initialization without causing significant slowdowns.


"""

from machine import I2C, Pin
import time

# -------------------------------------------------------------------
# Constants and Addresses
# -------------------------------------------------------------------

PETAL_ADDRESS = 0x00          # I2C address for the Petal controller (special address 0)
TOUCHWHEEL_ADDRESS = 0x54     # I2C address for the Touch Wheel device

# -------------------------------------------------------------------
# GPIO Pin Definitions
# -------------------------------------------------------------------

# Boot LED for indicating initialization status
bootLED = Pin("LED", Pin.OUT)
bootLED.on()  # Turn on boot LED to indicate the start of the boot process

# Button Pins with internal pull-up resistors
buttonA = Pin(8, Pin.IN, Pin.PULL_UP)
buttonB = Pin(9, Pin.IN, Pin.PULL_UP)
buttonC = Pin(28, Pin.IN, Pin.PULL_UP)

# General Purpose Input/Output (GPIO) Pins for Add-On Ports
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

# Group GPIOs into a list for easy access
GPIOs = [
    [gpio11, gpio12],
    [gpio21, gpio22],
    [gpio31, gpio32],
    [gpio41, gpio42],
    [gpio51, gpio52],
    [gpio61, gpio62]
]

# -------------------------------------------------------------------
# I2C Bus Initialization
# -------------------------------------------------------------------

# Initialize I2C bus 0 for ports 1-3 (SDA on Pin 0, SCL on Pin 1)
i2c0 = I2C(0, sda=Pin(0), scl=Pin(1), freq=400_000)

# Initialize I2C bus 1 for ports 4-6 (SDA on Pin 26, SCL on Pin 27)
i2c1 = I2C(1, sda=Pin(26), scl=Pin(27), freq=400_000)

# -------------------------------------------------------------------
# Helper Functions
# -------------------------------------------------------------------

def which_bus_has_device_id(i2c_id, debug=False):
    """
    Determines which I2C bus(es) contain a device with the specified I2C address.

    Args:
        i2c_id (int): The I2C address to search for.
        debug (bool): If True, prints the devices found on each bus.

    Returns:
        list: A list of I2C bus objects that have the device with the given address.
    """
    busses_found = []

    # Scan I2C bus 0
    i2c0_devices = i2c0.scan()
    if debug:
        print("Bus 0 Devices:")
        print([hex(addr) for addr in i2c0_devices])

    if i2c_id in i2c0_devices:
        busses_found.append(i2c0)

    # Scan I2C bus 1
    i2c1_devices = i2c1.scan()
    if debug:
        print("Bus 1 Devices:")
        print([hex(addr) for addr in i2c1_devices])

    if i2c_id in i2c1_devices:
        busses_found.append(i2c1)

    return busses_found

def petal_init(bus):
    """
    Configures the Petal controller with initial settings.

    Args:
        bus (I2C): The I2C bus connected to the Petal controller.
    """
    # Configure Petal controller registers
    bus.writeto_mem(PETAL_ADDRESS, 0x09, bytes([0x00]))  # Raw pixel mode (not 7-segment)
    bus.writeto_mem(PETAL_ADDRESS, 0x0A, bytes([0x09]))  # Intensity setting (out of 16)
    bus.writeto_mem(PETAL_ADDRESS, 0x0B, bytes([0x07]))  # Enable all segments
    bus.writeto_mem(PETAL_ADDRESS, 0x0C, bytes([0x81]))  # Undo shutdown bits
    bus.writeto_mem(PETAL_ADDRESS, 0x0D, bytes([0x00]))  # Reserved or specific configuration
    bus.writeto_mem(PETAL_ADDRESS, 0x0E, bytes([0x00]))  # Disable advanced features (default)
    bus.writeto_mem(PETAL_ADDRESS, 0x0F, bytes([0x00]))  # Turn off display test mode

def touchwheel_read(bus):
    """
    Reads the current value from the Touch Wheel device.

    Args:
        bus (I2C): The I2C bus connected to the Touch Wheel.

    Returns:
        int: The touch position value (0 for no touch, 1-255 for positions around the wheel).
    """
    try:
        data = bus.readfrom_mem(TOUCHWHEEL_ADDRESS, 0x00, 1)
        return data[0]
    except Exception as e:
        print("Error reading Touch Wheel:", e)
        return 0

def touchwheel_rgb(bus, r, g, b):
    """
    Sets the RGB color on the central display of the Touch Wheel.

    Args:
        bus (I2C): The I2C bus connected to the Touch Wheel.
        r (int): Red component (0-255).
        g (int): Green component (0-255).
        b (int): Blue component (0-255).
    """
    try:
        bus.writeto_mem(TOUCHWHEEL_ADDRESS, 15, bytes([r]))
        bus.writeto_mem(TOUCHWHEEL_ADDRESS, 16, bytes([g]))
        bus.writeto_mem(TOUCHWHEEL_ADDRESS, 17, bytes([b]))
    except Exception as e:
        print("Error setting Touch Wheel RGB:", e)

# -------------------------------------------------------------------
# Peripheral Initialization
# -------------------------------------------------------------------

# Initialize Petal Controller
petal_bus = None
try:
    petal_init(i2c0)
    petal_bus = i2c0
    print("Petal controller initialized on I2C bus 0.")
except Exception as e:
    print("Failed to initialize Petal on I2C bus 0:", e)

if not petal_bus:
    try:
        petal_init(i2c1)
        petal_bus = i2c1
        print("Petal controller initialized on I2C bus 1.")
    except Exception as e:
        print("Failed to initialize Petal on I2C bus 1:", e)

if not petal_bus:
    print("Warning: Petal controller not found on any I2C bus.")

# Indicate waiting for Touch Wheel with yellow light (example command)
if petal_bus:
    try:
        petal_bus.writeto_mem(PETAL_ADDRESS, 3, bytes([0x80]))  # Example command for yellow light
        petal_bus.writeto_mem(PETAL_ADDRESS, 2, bytes([0x80]))
    except Exception as e:
        print("Error setting Petal indicators:", e)

# Initialize Touch Wheel
touchwheel_bus = None
touchwheel_counter = 0
MAX_TOUCHWHEEL_RETRIES = 50  # Timeout after 50 attempts (approx 5 seconds)

while not touchwheel_bus and touchwheel_counter < MAX_TOUCHWHEEL_RETRIES:
    try:
        available_busses = which_bus_has_device_id(TOUCHWHEEL_ADDRESS)
        if available_busses:
            touchwheel_bus = available_busses[0]
            print(f"Touch Wheel found on I2C bus {available_busses.index(touchwheel_bus)}.")
            break
    except Exception as e:
        print("Error scanning for Touch Wheel:", e)
    time.sleep_ms(100)
    touchwheel_counter += 1

if not touchwheel_bus:
    print("Warning: Touch Wheel not found after multiple attempts.")

# -------------------------------------------------------------------
# Final Configuration
# -------------------------------------------------------------------

# If both Petal and Touch Wheel are initialized, set initial states
if touchwheel_bus and petal_bus:
    try:
        # Example: Set Petal to green to indicate Touch Wheel is configured
        petal_bus.writeto_mem(PETAL_ADDRESS, 3, bytes([0x00]))  # Turn off previous indicator
        petal_bus.writeto_mem(PETAL_ADDRESS, 2, bytes([0x80]))  # Set desired state
        time.sleep_ms(200)
        petal_bus.writeto_mem(PETAL_ADDRESS, 2, bytes([0x00]))  # Reset indicator
    except Exception as e:
        print("Error during final Petal configuration:", e)

# Turn off Boot LED after initialization
bootLED.off()
print("Boot sequence completed.")
