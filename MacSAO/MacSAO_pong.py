# MacSAO_pong.py
# MIT License
# see github.com/MakeItHackin/Supercon_8_2024_Badge_Hack for more information.


'''
Overview
This Micropython script is designed for the MacSAO (Macintosh Simple Add-On) featured on the main badge of the Supercon 8 Conference in Pasadena, CA, held from November 1-3, 2024, organized by Hackaday. The badge utilizes a Raspberry Pi Pico Wireless and supports six Simple Add-On (SAO) ports for additional functionalities. This particular script simulates a game of Pong on the MacSAO's OLED display by communicating via the I2C interface.

Authors: MakeItHackin, CodeAllNight, Danner
Repository: github.com/MakeItHackin/Supercon_8_2024_Badge_Hack
Project Info: Macintosh SAO by SirCastor
Documentation: aeiche.com/macsao

Detailed Explanation
Imports
machine.I2C & machine.Pin: Used for I2C communication and pin control.
time: Provides time-related functions like delays.
sys: Enables system-specific parameters and functions, used here for exiting the program in case of errors.
Configuration
I2C Pins: Defines the GPIO pins used for SDA and SCL lines.
MACSAO_ADDRESS: The I2C address of the MacSAO device.
Payloads: Predefined byte sequences to send specific commands to the MacSAO.
I2C Initialization
Initializes the I2C bus with the specified SDA and SCL pins.
Sets the frequency to 100kHz.
Includes error handling to ensure the program exits gracefully if initialization fails.
I2C Device Scan
Scans the I2C bus for connected devices.
Prints out the addresses of any found devices.
Exits the program if the scan fails.
Utility Functions
send_payload(payload, description):

Sends a byte payload to the MacSAO.
Includes optional debug print statements for tracking sent commands.
create_rectangle_payload(x, y, width, height, color):

Constructs a byte payload to draw a filled rectangle on the display.
Parameters define the position, size, and color of the rectangle.
map_y(input_val, screen_height, rect_height):

Maps an input value (0-128) to a Y-coordinate within the screen's height, ensuring the rectangle remains within bounds.
screen_saver(y_left, y_right):

Draws two rectangles (paddles) at specified Y-coordinates.
Resets the mouse position after drawing each rectangle.
screen_saver_circle(x, y, radius):

Draws a circle (representing the Pong ball) at the specified position.
Resets the mouse position after drawing the circle.
Main Function
Initialization:

Sets the MacSAO to LiveDrive mode.
Resets the mouse position to (0, 0).
Screen and Game Parameters:

Defines screen dimensions, rectangle (paddle) sizes, and initial positions and velocities for the Pong ball.
Sets the number of animation cycles and maximum bounces per cycle.
Animation Loop:

For each cycle:
Resets the Pong ball to the center.
Runs the animation until the maximum number of bounces is reached.
Updates the ball's position based on its velocity.
Detects and handles collisions with the screen boundaries by reversing velocity and incrementing the bounce count.
Ensures the ball stays within screen bounds.
Draws the ball and updates the paddles' positions.
Includes a short delay to control animation speed.
Optional Cleanup:

Provides commented-out code to clear the screen after all animation cycles are complete.
Script Entry Point
Ensures that the main() function runs when the script is executed directly.
Additional Information
Documentation & Usage:

Comprehensive instructions and documentation are available at aeiche.com/macsao.
For more projects and detailed information, visit the Hackaday project page for MacSAO.
Contributing:

Contributions and enhancements are welcome. Please refer to the GitHub repository for more details.
Dependencies:

Ensure that the Raspberry Pi Pico Wireless is properly configured with Micropython.
The MacSAO should be connected correctly via the I2C interface as per the pin configuration.
Customization:

You can modify the animation_cycles, max_bounces, and step variables to adjust the animation's behavior.
The create_rectangle_payload and screen_saver_circle functions can be adapted to change the appearance of the paddles and ball.

'''



# ================================
#          IMPORTS
# ================================
from machine import I2C, Pin
import time
import sys

# ================================
#       CONFIGURATION
# ================================

# Define I2C Pins based on your hardware configuration
SDA_PIN = 26  # SDA is connected to Pin 26
SCL_PIN = 27  # SCL is connected to Pin 27

# MacSAO I2C address (7-bit address)
MACSAO_ADDRESS = 0x0A

# Define Control Payloads
payload_set_mouse_position = bytes([0x05, 0x02, 0x00, 0x00])  # Set Mouse Position to (0, 0)

# ================================
#       I2C INITIALIZATION
# ================================

# Initialize I2C bus with the correct pins
try:
    i2c = I2C(1, scl=Pin(SCL_PIN), sda=Pin(SDA_PIN), freq=100000)
    print("I2C initialized on bus 1 with SCL on pin 27 and SDA on pin 26.")
except Exception as e:
    print("Failed to initialize I2C:", e)
    sys.exit(1)

# ================================
#        I2C DEVICE SCAN
# ================================

# Scan for I2C devices
try:
    devices = i2c.scan()
    if devices:
        print("I2C devices found:", [hex(device) for device in devices])
    else:
        print("No I2C devices found.")
except Exception as e:
    print("Failed to scan I2C bus:", e)
    sys.exit(1)

# ================================
#         UTILITY FUNCTIONS
# ================================

def send_payload(payload, description):
    """
    Sends a payload to the MacSAO via I2C.

    Parameters:
    - payload (bytes): The data to send.
    - description (str): Description of the payload for debugging.
    """
    try:
        i2c.writeto(MACSAO_ADDRESS, payload)
        # Uncomment the line below to enable debug messages
        # print(f"Sent: {description}")
    except Exception as e:
        print(f"Failed to send {description}: {e}")

def create_rectangle_payload(x, y, width, height, color):
    """
    Create a payload to draw a filled rectangle.

    Parameters:
    - x (int): Top-left x-coordinate
    - y (int): Top-left y-coordinate
    - width (int): Width of the rectangle
    - height (int): Height of the rectangle
    - color (int): 0 for black, 1 for white

    Returns:
    - bytes: The payload to send via I2C
    """
    return bytes([0x01, 0x02, 0x0C, x, y, width, height, color, 0xFE])

def map_y(input_val, screen_height=48, rect_height=15):
    """
    Map an input value between 0 and 128 to a Y-coordinate within screen bounds.

    Parameters:
    - input_val (int): Input value between 0 and 128
    - screen_height (int): Height of the screen in pixels
    - rect_height (int): Height of the rectangle in pixels

    Returns:
    - int: Mapped Y-coordinate, clamped to ensure the rectangle stays on screen
    """
    y = int((input_val / 128) * screen_height)
    y = max(0, min(y, screen_height - rect_height))
    return y

def screen_saver(y_left, y_right):
    """
    Draw the current frame of the screensaver with two rectangles.

    Parameters:
    - y_left (int): Y-coordinate for the left rectangle (0 to 33)
    - y_right (int): Y-coordinate for the right rectangle (0 to 33)
    """
    # Set Variable: Set MODE to LIVEDRIVE (1)
    payload_set_mode = bytes([0x05, 0x01, 0x01])

    # Set Variable: Reset Mouse Position to (0, 0)
    payload_set_mouse_position = bytes([0x05, 0x02, 0x00, 0x00])

    # Define Rectangle Payloads with updated y positions
    payload_draw_left_rect = create_rectangle_payload(
        x=0, y=y_left, width=5, height=15, color=0x00  # Black color
    )
    payload_draw_right_rect = create_rectangle_payload(
        x=59, y=y_right, width=5, height=15, color=0x00  # Black color
    )

    # Draw the left rectangle
    send_payload(payload_draw_left_rect, f"Draw Left Rectangle at (0,{y_left})")
    send_payload(payload_set_mouse_position, "Reset Mouse Position to (0,0)")
    time.sleep(0.02)  # Short delay

    # Draw the right rectangle
    send_payload(payload_draw_right_rect, f"Draw Right Rectangle at (59,{y_right})")
    send_payload(payload_set_mouse_position, "Reset Mouse Position to (0,0)")
    time.sleep(0.02)  # Short delay

def screen_saver_circle(x, y, radius):
    """
    Draw the circle (pong ball) at the specified position.

    Parameters:
    - x (int): X-coordinate of the circle's center
    - y (int): Y-coordinate of the circle's center
    - radius (int): Radius of the circle
    """
    # Draw the circle at new position with white color
    payload_draw_circle = bytes([0x01, 0x02, 0x0F, x, y, radius, 0x01, 0xFE])
    send_payload(payload_draw_circle, f"Draw Circle at ({x},{y})")
    send_payload(payload_set_mouse_position, "Reset Mouse Position to (0,0)")
    time.sleep(0.02)  # Short delay

# ================================
#           MAIN FUNCTION
# ================================

def main():
    """
    Main function to initialize the MacSAO and run the Pong animation.
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

    # Screen dimensions
    screen_width = 64
    screen_height = 48

    # Rectangle dimensions
    rect_width = 5
    rect_height = 15

    # Circle (Pong ball) parameters
    radius = 5
    x = screen_width // 2  # Start at center x = 32
    y = screen_height // 2  # Start at center y = 24
    vx = 1  # Initial x velocity
    vy = 1  # Initial y velocity

    # Animation settings
    animation_cycles = 10        # Number of animation cycles
    max_bounces = 20             # Maximum bounces per cycle

    # Initialize rectangle movement variables
    y_left_input = 64             # Start at middle input value
    y_right_input = 64            # Start at middle input value
    y_left_direction = 1          # 1 for increasing, -1 for decreasing
    y_right_direction = -1        # Start moving in opposite direction
    step = 2                      # Input step per frame

    for cycle in range(animation_cycles):
        print(f"Starting animation cycle {cycle + 1}/{animation_cycles}")
        
        # Reset circle to center for each cycle
        x = screen_width // 2
        y = screen_height // 2
        vx = 1
        vy = 1
        bounce_count = 0

        while bounce_count < max_bounces:
            # Update circle position
            x += vx
            y += vy

            # Bounce off the vertical walls
            if x + radius >= screen_width or x - radius <= 0:
                vx = -vx
                bounce_count += 1
                print(f"Bounce count: {bounce_count} (Vertical)")

            # Bounce off the horizontal walls
            if y + radius >= screen_height or y - radius <= 0:
                vy = -vy
                bounce_count += 1
                print(f"Bounce count: {bounce_count} (Horizontal)")

            # Ensure the circle stays within bounds after bouncing
            x = max(radius, min(x, screen_width - radius))
            y = max(radius, min(y, screen_height - radius))

            # Draw the circle at the new position
            screen_saver_circle(x, y, radius)

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
            y_left = map_y(y_left_input, screen_height, rect_height)
            y_right = map_y(y_right_input, screen_height, rect_height)

            # Draw the rectangles with updated y positions
            screen_saver(y_left, y_right)

            # Delay between frames to control animation speed
            time.sleep(0.02)

    # Optionally, clear the screen at the end of all cycles
    # payload_clear_screen = bytes([0x01, 0x02, 0x00, 0xFE])
    # send_payload(payload_clear_screen, "Clear Screen")

    print("Screensaver completed.")

# ================================
#        SCRIPT ENTRY POINT
# ================================

# Run the main function when the script is executed
if __name__ == "__main__":
    main()
