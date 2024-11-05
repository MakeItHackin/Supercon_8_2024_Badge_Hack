# =============================================================================
# etch_demo.py
# =============================================================================
# Description:
# This script serves as a demonstration for the Etch SAO Sketch on the 
# Raspberry Pi Pico Wireless badge. It initializes the I2C communication, 
# connects to the Etch SAO, clears the display, and continuously reads input 
# from the potentiometers to draw pixels on the OLED screen.
#
# Project:
# Supercon 8 Conference Badge by Hackaday
#
# Authors:
# - MakeItHackin
# - CodeAllNight
# - Danner
#
# see github.com/MakeItHackin/Supercon_8_2024_Badge_Hack for more information.
#
# Additional Information:
# - Etch-SAO-Sketch Project: https://hackaday.io/project/197581-etch-sao-sketch
# - Refer to the GitHub repository for more details.
#
# Date:
# November 1-3, 2024
# =============================================================================

import etch
import time
from machine import I2C, Pin

# -----------------------------------------------------------------------------
# Initialization Section
# -----------------------------------------------------------------------------

# Initialize I2C communication on I2C bus 1 with specified SDA and SCL pins
i2c = I2C(1, sda=Pin(26), scl=Pin(27), freq=400_000)

# Scan and print all I2C devices connected to the bus
print("I2C Devices Found:", i2c.scan())

# Initialize the Etch SAO Sketch connected to SPOT 6 on the badge
etch_sao_sketch = etch.Etch(i2c)

# Clear the OLED display by performing a "shake" action
etch_sao_sketch.shake()

# -----------------------------------------------------------------------------
# Main Loop
# -----------------------------------------------------------------------------
# Continuously read potentiometer values, map them to screen coordinates,
# and draw pixels on the OLED display.

while True:
    # Read the current values from the left and right potentiometers
    x = etch_sao_sketch.left
    y = etch_sao_sketch.right

    # Invert the Y-axis control for proper display orientation
    y = 128 - y

    # Print the current (x, y) coordinates for debugging
    print(f"Coordinates: x={x}, y={y}")

    # Draw a single pixel at the mapped (x, y) position with color '1' (on)
    etch_sao_sketch.draw_pixel(x, y, 1)

    # Update the OLED display to reflect the drawn pixel
    etch_sao_sketch.draw_display()

    # Wait for 100 milliseconds before the next iteration
    time.sleep_ms(100)
