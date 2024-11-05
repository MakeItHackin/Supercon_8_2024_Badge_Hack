# BlinkyLoop_demo.py
# Demonstrated at Supercon 8, Pasadena, CA (Nov 1-3, 2024)
# MIT License
# Authors: MakeItHackin, CodeAllNight, Danner
# Project Link: https://github.com/MakeItHackin/Supercon_8_2024_Badge_Hack

"""
====================================================
Supercon 8 2024 Raspberry Pi Pico Wireless Badge
====================================================

This script is a demo for the BlinkyLoop Simple Add-On (SAO)
featured on the main badge for Supercon 8 conference organized
by Hackaday in Pasadena, CA.

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

**BlinkyLoop SAO Overview:**
The BlinkyLoop SAO includes a circle of WS2812 addressable LEDs (NeoPixels) and an accelerometer (LIS3DH) to sense orientation and movements. This demo focuses on testing the NeoPixels, while the accelerometer functionality can be explored through additional documentation or Flummer's project page.

**Project Description:**
This SAO is designed to be minimally invasive, ensuring compatibility with badges that have multiple connectors and varied mounting orientations. The accelerometer aids in maintaining upright animations, making it ideal for applications like clocks or pendulum effects. Potential project ideas include a digital level or motion-sensitive games.

**I2C Communication:**
- **I2C0:** Ports 1-3
- **I2C1:** Ports 4-6
- **Accelerometer (LIS3DH) Default Address:** `0x19`
- **Change Address to `0x18`:** By cutting a trace and bridging a small solder jumper to prevent address conflicts on the I2C bus.

Additional Information
BlinkyLoop SAO Project Overview
Description: The BlinkyLoop SAO is a simple add-on designed for electronic badges, featuring a circle of WS2812 addressable LEDs (NeoPixels) and an accelerometer (LIS3DH) to sense orientation and detect movements or gestures. Its minimalistic design ensures compatibility with badges that have multiple connectors and varied mounting orientations. The accelerometer helps maintain upright animations, making it ideal for displaying a simple clock or pendulum effects. Other potential projects include a digital level or motion-sensitive games.

Features:

LEDs: 12 WS2812 NeoPixels connected to GPIO1.
Accelerometer: LIS3DH connected via I2C with interrupt on GPIO2 for motion detection.
Temperature Sensor: Integrated within the accelerometer.
I2C Buses:
i2c0: Ports 1-3
i2c1: Ports 4-6
Address Configuration: LIS3DH default I2C address is 0x19. It can be changed to 0x18 by modifying the solder jumper to prevent address conflicts.
Project Link: BlinkyLoop SAO by Flummer

Demo Focus: This demo script primarily tests the NeoPixels' functionality. For accelerometer integration and more advanced features, refer to additional documentation or the BlinkyLoop project page.

====================================================
"""

import machine
import neopixel
import time
import sys

# ======================
# Configuration Section
# ======================
NUM_PIXELS = 12      # Number of NeoPixels in the BlinkyLoop
PIN_NUM = 3          # GPIO pin connected to NeoPixels

# Initialize NeoPixel object
np = neopixel.NeoPixel(machine.Pin(PIN_NUM), NUM_PIXELS)

# ======================
# Helper Functions
# ======================

def clear_pixels():
    """Turn off all NeoPixels."""
    for i in range(NUM_PIXELS):
        np[i] = (0, 0, 0)
    np.write()

def color_wipe(color, wait=50):
    """
    Wipe color across display a pixel at a time.
    
    Args:
        color (tuple): RGB color tuple.
        wait (int): Delay in milliseconds between each pixel.
    """
    for i in range(NUM_PIXELS):
        np[i] = color
        np.write()
        time.sleep_ms(wait)

def rainbow_cycle(wait=20):
    """
    Draw rainbow that uniformly distributes itself across all pixels.
    
    Args:
        wait (int): Delay in milliseconds between each cycle step.
    """
    for j in range(256):
        for i in range(NUM_PIXELS):
            idx = (i * 256 // NUM_PIXELS) + j
            np[i] = wheel(idx & 255)
        np.write()
        time.sleep_ms(wait)

def theater_chase(color, wait=50, iterations=10):
    """
    Movie theater light style chaser animation.
    
    Args:
        color (tuple): RGB color tuple.
        wait (int): Delay in milliseconds between each step.
        iterations (int): Number of chase iterations.
    """
    for _ in range(iterations):
        for q in range(3):
            for i in range(NUM_PIXELS):
                if (i + q) % 3 == 0:
                    np[i] = color
                else:
                    np[i] = (0, 0, 0)
            np.write()
            time.sleep_ms(wait)
    clear_pixels()

def blink(color, wait=500, times=5):
    """
    Blink all pixels on and off.
    
    Args:
        color (tuple): RGB color tuple.
        wait (int): Delay in milliseconds between on/off states.
        times (int): Number of blink cycles.
    """
    for _ in range(times):
        color_pixels(color)
        time.sleep_ms(wait)
        clear_pixels()
        time.sleep_ms(wait)

def sparkle(color, wait=100, times=20):
    """
    Sparkle random pixels.
    
    Args:
        color (tuple): RGB color tuple.
        wait (int): Delay in milliseconds between sparkles.
        times (int): Number of sparkles.
    """
    import urandom
    for _ in range(times):
        idx = urandom.getrandbits(4) % NUM_PIXELS
        np[idx] = color
        np.write()
        time.sleep_ms(wait)
        np[idx] = (0, 0, 0)

def fade(color, wait=20, steps=50):
    """
    Fade all pixels in and out.
    
    Args:
        color (tuple): RGB color tuple.
        wait (int): Delay in milliseconds between fade steps.
        steps (int): Number of fade steps.
    """
    r, g, b = color
    for fade_val in range(steps):
        scaled_color = (r * fade_val // steps, g * fade_val // steps, b * fade_val // steps)
        color_pixels(scaled_color)
        time.sleep_ms(wait)
    for fade_val in range(steps, -1, -1):
        scaled_color = (r * fade_val // steps, g * fade_val // steps, b * fade_val // steps)
        color_pixels(scaled_color)
        time.sleep_ms(wait)

def twinkle(color, wait=100, times=20):
    """
    Twinkle random pixels multiple times.
    
    Args:
        color (tuple): RGB color tuple.
        wait (int): Delay in milliseconds between twinkles.
        times (int): Number of twinkles.
    """
    import urandom
    for _ in range(times):
        idx = urandom.getrandbits(4) % NUM_PIXELS
        np[idx] = color
        np.write()
        time.sleep_ms(wait)
        np[idx] = (0, 0, 0)

def running_lights(color, wait=100, iterations=5):
    """
    Lights running from one end to the other.
    
    Args:
        color (tuple): RGB color tuple.
        wait (int): Delay in milliseconds between light movements.
        iterations (int): Number of complete runs.
    """
    for _ in range(iterations):
        for i in range(NUM_PIXELS):
            np[i] = color
            if i > 0:
                np[i-1] = (0, 0, 0)
            np.write()
            time.sleep_ms(wait)
    clear_pixels()

def fire_effect(wait=50, iterations=50):
    """
    Simple fire-like flickering effect.
    
    Args:
        wait (int): Delay in milliseconds between flickers.
        iterations (int): Number of flicker cycles.
    """
    import urandom
    for _ in range(iterations):
        for i in range(NUM_PIXELS):
            brightness = urandom.getrandbits(8) // 4
            np[i] = (brightness, brightness // 2, 0)
        np.write()
        time.sleep_ms(wait)

def custom_pattern(wait=100):
    """
    Display a custom color pattern.
    
    Args:
        wait (int): Delay in milliseconds before clearing the pattern.
    """
    pattern = [
        (255, 0, 0),    # Red
        (0, 255, 0),    # Green
        (0, 0, 255),    # Blue
        (255, 255, 0),  # Yellow
        (0, 255, 255),  # Cyan
        (255, 0, 255),  # Magenta
        (192, 192, 192),# Silver
        (128, 0, 0),    # Maroon
        (128, 128, 0),  # Olive
        (0, 128, 0),    # Dark Green
        (128, 0, 128),  # Purple
        (0, 128, 128)   # Teal
    ]
    for i in range(NUM_PIXELS):
        np[i] = pattern[i % len(pattern)]
    np.write()
    time.sleep_ms(wait)
    clear_pixels()

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
    Set all pixels to the specified color.
    
    Args:
        color (tuple): RGB color tuple.
    """
    for i in range(NUM_PIXELS):
        np[i] = color
    np.write()

# ======================
# Animation Mapping
# ======================
animations = {
    '1': ('Color Wipe (Red)', lambda: color_wipe((255, 0, 0))),
    '2': ('Rainbow Cycle', rainbow_cycle),
    '3': ('Theater Chase (Blue)', lambda: theater_chase((0, 0, 255))),
    '4': ('Blink (Green)', lambda: blink((0, 255, 0))),
    '5': ('Sparkle (White)', lambda: sparkle((255, 255, 255))),
    '6': ('Fade (Purple)', lambda: fade((128, 0, 128))),
    '7': ('Twinkle (Yellow)', lambda: twinkle((255, 255, 0))),
    '8': ('Running Lights (Orange)', lambda: running_lights((255, 165, 0))),
    '9': ('Fire Effect', fire_effect),
    '10': ('Custom Pattern', custom_pattern),
    'h': ('Help Menu', None)
}

# ======================
# User Interface
# ======================

def print_help():
    """Display the help menu with available animations."""
    print("\n=== NeoPixel Animation Help Menu ===")
    # Sort keys: numeric keys first (sorted numerically), then 'h'
    sorted_keys = sorted(
        animations.keys(),
        key=lambda x: (0, int(x)) if x.isdigit() else (1, x)
    )
    for key in sorted_keys:
        if key != 'h':
            print(f"{key}: {animations[key][0]}")
    print("h: Show Help Menu")
    print("Enter the number corresponding to the animation you want to run.")

def handle_input(cmd):
    """Process user input and trigger corresponding animations."""
    cmd = cmd.strip()
    if cmd in animations:
        if cmd == 'h':
            print_help()
        else:
            print(f"\nTriggering Animation: {animations[cmd][0]}")
            animations[cmd][1]()  # Execute the animation function
            print(f"Animation '{animations[cmd][0]}' completed.\n")
    else:
        print("Invalid command. Type 'h' for help.")

# ======================
# Main Execution
# ======================

def main():
    """Main loop to handle user input and control NeoPixels."""
    print("Initializing NeoPixel Animations...")
    print_help()
    
    while True:
        try:
            cmd = input("Enter command: ")
            handle_input(cmd)
        except KeyboardInterrupt:
            print("\nExiting program.")
            clear_pixels()
            sys.exit()
        except Exception as e:
            print(f"An error occurred: {e}")
            clear_pixels()

if __name__ == "__main__":
    main()
