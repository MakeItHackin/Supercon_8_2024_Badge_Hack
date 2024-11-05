# =============================================================================
# ssd1327.py
# =============================================================================
# Description:
# This module defines the SSD1327 class, which handles communication with the 
# SSD1327 OLED display over I2C. It provides methods to initialize the 
# display, send commands and data, manipulate individual pixels, draw shapes, 
# and refresh the display with the current buffer content.
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

from machine import I2C, Pin
import time

# -----------------------------------------------------------------------------
# SSD1327 OLED Display Class
# -----------------------------------------------------------------------------

class SSD1327:
    """
    SSD1327 Class to interface with a 128x128 grayscale OLED display.
    Handles initialization, command/data transmission, and pixel manipulation.
    """

    WIDTH = 128          # Display width in pixels
    HEIGHT = 128         # Display height in pixels
    I2C_ADDRESS = 0x3C   # I2C address for the SSD1327 OLED display

    def __init__(self, i2c: I2C):
        """
        Initialize the SSD1327 OLED display.

        Parameters:
        - i2c: An initialized I2C object for communication.
        """
        self.i2c = i2c
        # Initialize the display buffer (1 bit per pixel for monochrome)
        self.buffer = bytearray(self.WIDTH * self.HEIGHT // 8)
        self.reset()
        self.init_display()

    def reset(self):
        """
        Reset the OLED display.
        Note: Implement hardware reset if a reset pin is connected.
        """
        # Placeholder for reset functionality
        pass

    def command(self, cmd):
        """
        Send a single command byte to the OLED display.

        Parameters:
        - cmd: Command byte to send.
        """
        self.i2c.writeto(self.I2C_ADDRESS, bytearray([0x00, cmd]))

    def command2(self, cmd, cmd2):
        """
        Send two command bytes to the OLED display.

        Parameters:
        - cmd: First command byte.
        - cmd2: Second command byte.
        """
        self.i2c.writeto(self.I2C_ADDRESS, bytearray([0x00, cmd, cmd2]))

    def split_into_segments(self, ydata, segment_length=1024):
        """
        Split data into smaller segments for transmission.

        Parameters:
        - ydata: Bytearray data to split.
        - segment_length: Maximum length of each segment.

        Returns:
        - List of bytearrays, each representing a data segment.
        """
        return [ydata[i:i + segment_length] for i in range(0, len(ydata), segment_length)]

    def data(self, xdata):
        """
        Send data bytes to the OLED display.

        Parameters:
        - xdata: Bytearray containing data to send.
        """
        segments = self.split_into_segments(xdata)
        for i, segment in enumerate(segments):
            # Send each data segment with control byte 0x40
            self.i2c.writeto_mem(self.I2C_ADDRESS, 0x40, segment)

    def init_display(self):
        """
        Initialize the SSD1327 OLED display with the required command sequence.
        Sets up display parameters like remapping, display offset, clock division,
        multiplex ratio, and others.
        """
        # Power off the display
        self.command(0xAE)  # SSD1327_DISPLAYOFF

        # Set contrast control
        self.command2(0x81, 0x80)

        # Set remap & color depth
        self.command2(0xA0, 0x5F)

        # Set display start line to 0
        self.command2(0xA1, 0x40)

        # Set display offset to 0
        self.command2(0xA2, 0x00)

        # Set display mode to normal (not inverted)
        self.command(0xA6)

        # Set phase length (clocking)
        self.command2(0xB1, 0x11)

        # Additional configuration for display
        self.command2(0xB3, 0x00)  # 100Hz
        self.command2(0xAB, 0x01)
        self.command2(0xB6, 0x04)
        self.command2(0xBE, 0x0F)
        self.command2(0xBC, 0x08)
        self.command2(0xD5, 0x62)
        self.command2(0xFD, 0x12)

        # Set display to normal mode
        self.command(0xA4)  # SSD1327_NORMALDISPLAY

        # Power on the display
        self.command(0xAF)  # SSD1327_DISPLAYON

    def clear(self):
        """
        Clear the display buffer and update the OLED display.
        """
        # Reset the buffer to all zeros (cleared)
        self.buffer = bytearray(self.WIDTH * self.HEIGHT // 8)
        self.show()

    def show(self):
        """
        Refresh the OLED display with the current buffer content.
        """
        # Set column address range
        self.command(0x21)            # Set column address
        self.command(0x00)            # Start column
        self.command(self.WIDTH - 1)  # End column

        # Set page address range
        self.command(0x22)            # Set page address
        self.command(0x00)            # Start page
        self.command((self.HEIGHT // 8) - 1)  # End page

        # Send the buffer data to the display
        self.data(self.buffer)

    def draw_pixel(self, y, x, color):
        """
        Draw a single pixel at the specified (x, y) coordinates.

        Parameters:
        - y: Y-coordinate (0-127).
        - x: X-coordinate (0-127).
        - color: Pixel color (1 for on, 0 for off).
        """
        # Ensure coordinates are within display boundaries
        if 0 <= x < self.WIDTH and 0 <= y < self.HEIGHT:
            # Calculate buffer index
            index = x + (y // 8) * self.WIDTH
            # Set or clear the bit corresponding to the pixel
            if color:
                self.buffer[index] |= (1 << (y % 8))  # Set pixel
            else:
                self.buffer[index] &= ~(1 << (y % 8))  # Clear pixel

    def fill_rect(self, x, y, width, height, color):
        """
        Draw a filled rectangle on the display.

        Parameters:
        - x: X-coordinate of the top-left corner.
        - y: Y-coordinate of the top-left corner.
        - width: Width of the rectangle.
        - height: Height of the rectangle.
        - color: Rectangle color (1 for on, 0 for off).
        """
        for i in range(width):
            for j in range(height):
                self.draw_pixel(x + i, y + j, color)

# -----------------------------------------------------------------------------
# Example Usage
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    # Initialize I2C communication on I2C bus 1 with specified SDA and SCL pins
    i2c = I2C(1, sda=Pin(26), scl=Pin(27), freq=400_000)

    # Create an instance of the SSD1327 OLED display
    oled = SSD1327(i2c)

    # Clear the display to start with a blank screen
    oled.clear()

    # Example: Draw a horizontal line across the display
    for x in range(128):
        y = 15  # Fixed Y-coordinate
        if y >= 64:
            x = x - 8
        oled.draw_pixel(x, y, 1)  # Draw pixel with color '1' (on)
        oled.show()                # Update the display
        time.sleep_ms(10)          # Short delay for visibility

    # Optionally, clear the display after drawing
    # oled.clear()
