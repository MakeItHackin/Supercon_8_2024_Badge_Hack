"""
Supercon 8 Conference Badge Firmware
------------------------------------
Author: Elliot Williams and Contributors
Date: November 1-3, 2024
Location: Pasadena, CA
Event: Supercon 8, organized by Hackaday

Description:
This MicroPython script is designed for the Raspberry Pi Pico Wireless featured on the main badge for Supercon 8. 
The badge includes six Simple Add-On ports providing power, I2C communication, and two GPIO pins each. 
Ports 1-3 are connected to I2C bus 0 (i2c0), and ports 4-6 are connected to I2C bus 1 (i2c1).

Features:
- Controls RGB LEDs based on button inputs.
- Reads and displays touch wheel interactions.
- Initializes and manages communication with add-on modules via I2C.


Error Handling: The touchwheel_read function includes a try-except block to handle potential I2C communication errors gracefully.

Debugging Statements: Print statements are included throughout the code to aid in debugging by providing real-time feedback on button presses and touch wheel interactions.

Customization: Constants such as PETAL_ADDRESS, GPIO pin numbers, and I2C configurations should be adjusted based on the actual hardware setup and address assignments.

Extensibility: The script is structured to allow easy addition of new features or modifications to existing functionalities, such as adding more buttons, sensors, or handling additional I2C devices.


"""

from machine import I2C, Pin
import time

# Constants
PETAL_ADDRESS = 0x20  # I2C address for the petal controller (example address)
BUTTON_A_PIN = 10     # GPIO pin number for Button A
BUTTON_B_PIN = 11     # GPIO pin number for Button B
BUTTON_C_PIN = 12     # GPIO pin number for Button C
BOOT_LED_PIN = 25     # GPIO pin for the boot LED

# Initialize I2C buses
i2c0 = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)  # I2C bus 0 for ports 1-3
i2c1 = I2C(1, scl=Pin(3), sda=Pin(2), freq=400000)  # I2C bus 1 for ports 4-6

# Initialize GPIO pins for buttons
buttonA = Pin(BUTTON_A_PIN, Pin.IN, Pin.PULL_UP)
buttonB = Pin(BUTTON_B_PIN, Pin.IN, Pin.PULL_UP)
buttonC = Pin(BUTTON_C_PIN, Pin.IN, Pin.PULL_UP)

# Initialize Boot LED
bootLED = Pin(BOOT_LED_PIN, Pin.OUT)
bootLED.on()  # Turn on boot LED to indicate initialization

# Initialize variables
counter = 0

# Select which I2C bus to use for the petal controller
# Assuming petal_bus is connected to i2c0; adjust as necessary
petal_bus = i2c0
touchwheel_bus = i2c1  # Assuming touch wheel is connected to i2c1

def touchwheel_read(bus):
    """
    Reads the touch wheel value from the touch wheel I2C device.
    
    Args:
        bus (I2C): The I2C bus connected to the touch wheel.
    
    Returns:
        int: The touch wheel position value.
    """
    try:
        # Example read operation; actual implementation may vary
        data = bus.readfrom_mem(PETAL_ADDRESS, 0x00, 1)
        return data[0]
    except Exception as e:
        print("Touchwheel Read Error:", e)
        return 0

# -------------------------------------------------------------------
# Initialization Sequence
# -------------------------------------------------------------------

## Perform a quick spiral LED test to verify LED functionality
if petal_bus:
    for j in range(8):
        which_leds = (1 << (j + 1)) - 1  # Create a bitmask for LEDs
        for i in range(1, 9):
            print(f"Setting LEDs with bitmask: {which_leds:#04x}")
            petal_bus.writeto_mem(PETAL_ADDRESS, i, bytes([which_leds]))
            time.sleep_ms(30)
            # Optionally toggle LEDs off if needed
            petal_bus.writeto_mem(PETAL_ADDRESS, i, bytes([which_leds]))
            time.sleep_ms(30)

# -------------------------------------------------------------------
# Main Loop
# -------------------------------------------------------------------
while True:
    ## Display button status on RGB LEDs
    if petal_bus:
        # Check Button A status
        if not buttonA.value():
            petal_bus.writeto_mem(PETAL_ADDRESS, 2, bytes([0x80]))  # Turn on RGB for Button A
            print("Button A Pressed")
        else:
            petal_bus.writeto_mem(PETAL_ADDRESS, 2, bytes([0x00]))  # Turn off RGB for Button A

        # Check Button B status
        if not buttonB.value():
            petal_bus.writeto_mem(PETAL_ADDRESS, 3, bytes([0x80]))  # Turn on RGB for Button B
            print("Button B Pressed")
        else:
            petal_bus.writeto_mem(PETAL_ADDRESS, 3, bytes([0x00]))  # Turn off RGB for Button B

        # Check Button C status
        if not buttonC.value():
            petal_bus.writeto_mem(PETAL_ADDRESS, 4, bytes([0x80]))  # Turn on RGB for Button C
            print("Button C Pressed")
        else:
            petal_bus.writeto_mem(PETAL_ADDRESS, 4, bytes([0x00]))  # Turn off RGB for Button C

    ## Read touch wheel status
    if touchwheel_bus:
        tw = touchwheel_read(touchwheel_bus)
        print(f"Touchwheel Value: {tw}")

    ## Display touch wheel interaction on petal LEDs
    if petal_bus and touchwheel_bus:
        if tw > 0:
            tw_adjusted = (128 - tw) % 256
            petal = int(tw_adjusted / 32) + 1  # Determine which LED to light
            print(f"Touchwheel adjusted value: {tw_adjusted}, Petal LED: {petal}")
        else:
            petal = 999  # Invalid or no touch detected
            print("No touch detected on touch wheel")

        # Update petal LEDs based on touch wheel input
        for i in range(1, 9):
            if i == petal:
                petal_bus.writeto_mem(0, i, bytes([0x7F]))  # Light up the corresponding petal LED
                print(f"Lighting up Petal LED {i}")
            else:
                petal_bus.writeto_mem(0, i, bytes([0x00]))  # Turn off other petal LEDs

    # Short delay to prevent excessive CPU usage
    time.sleep_ms(20)

    # Turn off Boot LED after initialization
    bootLED.off()
