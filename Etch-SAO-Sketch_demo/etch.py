# =============================================================================
# etch_init.py
# =============================================================================
# Description:
# This module defines the Etch class responsible for initializing and 
# interfacing with the Etch SAO Sketch hardware. It handles I2C communication 
# with the OLED display and the LIS3DH 3-axis accelerometer, reads analog 
# inputs from potentiometers, and provides methods to manipulate the display.
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
import ssd1327

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------

__version__ = '0.1.4'  # Version of the Etch module

I2C_ADDRESS = 0x19  # I2C address for the LIS3DH accelerometer

# GPIO pins for analog inputs (potentiometers)
gpio61 = Pin(18, Pin.IN)
gpio62 = Pin(17, Pin.IN)

# -----------------------------------------------------------------------------
# Etch Class Definition
# -----------------------------------------------------------------------------

class Etch:
    """
    Etch Class to interface with the Etch SAO Sketch hardware.
    Handles I2C communication, sensor initialization, and display manipulation.
    """

    def __init__(self, i2c1):
        """
        Initialize the Etch object with the provided I2C interface.

        Parameters:
        - i2c1: An initialized I2C object for communication.
        """
        print("Initializing Etch SAO Sketch...")
        self._i2c = i2c1
        print("Initializing OLED display...")
        self._display = ssd1327.SSD1327(self._i2c)
        print("Initializing accelerometer (LIS3DH)...")
        self._init_lis3dh()

    def _read_register(self, addr, reg, nbytes=1):
        """
        Read data from a specific register of an I2C device.

        Parameters:
        - addr: I2C address of the device.
        - reg: Register address to read from.
        - nbytes: Number of bytes to read.

        Returns:
        - Bytearray containing the read data.
        """
        return self._i2c.readfrom_mem(addr, reg, nbytes)

    def _init_lis3dh(self):
        """
        Initialize the LIS3DH 3-axis accelerometer with the required settings.
        Configures control registers for proper operation.
        """
        # Configure CTRL_REG1 (0x20) to enable axes and set data rate
        self._i2c.writeto_mem(I2C_ADDRESS, 0x20, bytearray([0x07]))
        print("CTRL_REG1:", self._read_register(I2C_ADDRESS, 0x20))

        # Further configuration of CTRL_REG1 for specific settings
        self._i2c.writeto_mem(I2C_ADDRESS, 0x20, bytearray([0x77]))
        # Configure CTRL_REG4 (0x23) for high-resolution mode and block data update
        self._i2c.writeto_mem(I2C_ADDRESS, 0x23, bytearray([0x88]))
        print("CTRL_REG4:", self._read_register(I2C_ADDRESS, 0x22))

        # Additional configurations as needed
        self._i2c.writeto_mem(I2C_ADDRESS, 0x22, bytearray([0x10]))
        self._i2c.writeto_mem(I2C_ADDRESS, 0x1F, bytearray([0x80]))
        print("CTRL_REG4 after update:", self._read_register(I2C_ADDRESS, 0x23))

        # Ensure configurations are applied
        self._i2c.writeto_mem(I2C_ADDRESS, 0x23, bytearray([0x88]))
        print("Final CTRL_REG4:", self._read_register(I2C_ADDRESS, 0x23))

        # Short delay to allow settings to take effect
        time.sleep_ms(100)

    def _read_adc(self):
        """
        Read analog values from the potentiometers connected to the GPIO pins.

        Returns:
        - List containing ADC values for each potentiometer.
        """
        adc_registers = [0x88, 0x8A]  # Register addresses for ADC readings
        adc_values = []
        for reg in adc_registers:
            data = self._i2c.readfrom_mem(I2C_ADDRESS, reg, 2)
            value = (data[0] | (data[1] << 8))
            adc_values.append(value)
        return adc_values

    def _read_left(self):
        """
        Read and process the left potentiometer value.

        Returns:
        - Mapped integer value between 0 and 128 representing the X-axis position.
        """
        dataL = self._read_register(I2C_ADDRESS, 0x88, 2)
        left = (dataL[1] << 8) | dataL[0]
        if left > 32512:
            left -= 65536
        left += 32512  # Normalize to 0..65535
        return left // 508  # Scale to 0..128

    def _read_right(self):
        """
        Read and process the right potentiometer value.

        Returns:
        - Mapped integer value between 0 and 128 representing the Y-axis position.
        """
        dataR = self._read_register(I2C_ADDRESS, 0x8A, 2)
        right = (dataR[1] << 8) | dataR[0]
        if right > 32512:
            right -= 65535
        right += 32512  # Normalize to 0..65535
        return right // 508  # Scale to 0..128

    @property
    def left(self):
        """
        Property to get the current X-axis position from the left potentiometer.

        Returns:
        - Integer value between 0 and 128.
        """
        return self._read_left()

    @property
    def right(self):
        """
        Property to get the current Y-axis position from the right potentiometer.

        Returns:
        - Integer value between 0 and 128.
        """
        return self._read_right()

    def shake(self):
        """
        Clear the OLED display by clearing the display buffer.
        """
        self._display.clear()

    def draw_pixel(self, x, y, color):
        """
        Draw a single pixel on the OLED display at the specified coordinates.

        Parameters:
        - x: X-coordinate (0-127).
        - y: Y-coordinate (0-127).
        - color: Pixel color (1 for on, 0 for off).
        """
        # Clamp x and y to display boundaries
        if y > 127:
            y = 127
        if y < 0:
            y = 0
        if x > 127:
            x = 127
        if x < 0:
            x = 0

        # Adjust Y-coordinate based on screen orientation
        if y > 64:
            y -= 64
        else:
            y += 64

        # Draw the pixel on the display buffer
        self._display.draw_pixel(x, y, color)

    def draw_display(self):
        """
        Update the OLED display with the current buffer content.
        """
        self._display.show()

# -----------------------------------------------------------------------------
# Uncomment the following lines if you wish to run initialization independently
# -----------------------------------------------------------------------------
# print("Starting initialization...")
# time.sleep(1)
# init_lis3dh()
# print("Initialization complete.")
