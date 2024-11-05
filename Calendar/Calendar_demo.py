# Calendar_demo.py
# ======================================
# Supercon 8 Conference Badge - Schedule SAO
# ======================================
# 
# This script is written in MicroPython for the Raspberry Pi Pico Wireless badge
# featured at the Supercon 8 conference in Pasadena, CA (Nov 1-3, 2024).
# 
# **Authors:**
# - MakeItHackin
# - CodeAllNight
# - Danner
# 
# **Purpose:**
# - Integrates with the DS3231 Real-Time Clock (RTC) and a 4KB EEPROM via I2C.
# - Demonstrates functionalities such as setting and reading time, managing calendar events,
#   reading temperature, and wiping EEPROM data.
# - Provides an interactive menu for user interaction.
#
# **License:** MIT License
# **Repository:** [github.com/MakeItHackin/Supercon_8_2024_Badge_Hack](https://github.com/MakeItHackin/Supercon_8_2024_Badge_Hack)

'''
Detailed Code Explanation
1. Header and Metadata
At the very beginning of the script, there's a comprehensive header that provides essential information about the script:

Filename: Calendar_demo.py
Purpose: Manages calendar events by interfacing with the DS3231 RTC and EEPROM.
Authors: MakeItHackin, CodeAllNight, Danner
Conference Details: Supercon 8, Pasadena, CA, organized by Hackaday.
License: MIT License
Repository: Link to the GitHub repository for more information.
2. Imports
python
Copy code
from machine import I2C, Pin
import time
import sys
machine: Provides access to hardware-related functions, specifically I2C and Pin control.
time: For handling time-related functions like delays and timestamp conversions.
sys: Allows for system-level operations like exiting the program.
3. Initialization
I2C Interface Setup
python
Copy code
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)  # Adjust as per your board
Initializes the I2C bus with specified SCL and SDA pins and sets the frequency to 400kHz.
Note: The pins and frequency might need adjustment based on the specific hardware setup.
Device Addresses and EEPROM Specifications
python
Copy code
DS3231_I2C_ADDR = 0x68
EEPROM_I2C_ADDR = 0x57  # Adjust based on your EEPROM's address pins

EEPROM_SIZE = 4096  # 4KB EEPROM
PAGE_SIZE = 32       # EEPROM page size (common sizes: 16, 32, 64 bytes)
DS3231_I2C_ADDR: I2C address for the DS3231 RTC.
EEPROM_I2C_ADDR: I2C address for the EEPROM, which can vary based on hardware configuration.
EEPROM_SIZE: Total size of the EEPROM in bytes.
PAGE_SIZE: The size of each EEPROM page, important for write operations.
4. Helper Functions
BCD Conversion
python
Copy code
def dec_to_bcd(val):
    return (val // 10 << 4) + (val % 10)

def bcd_to_dec(val):
    return ((val >> 4) * 10) + (val & 0x0F)
dec_to_bcd: Converts a decimal number to Binary-Coded Decimal (BCD) format.
bcd_to_dec: Converts a BCD number back to decimal format.
Purpose: The DS3231 RTC uses BCD for time representation, so these functions facilitate conversions.
5. DS3231 RTC Functions
Setting the Time
python
Copy code
def set_time(year, month, date, day, hour, minute, second):
    ...
Parameters: Full date and time components.
Process: Converts each component to BCD and writes them to the DS3231 registers.
Error Handling: Catches and reports any I/O errors during the write operation.
Reading the Time
python
Copy code
def read_time():
    ...
Process: Reads 7 bytes from the DS3231 starting at register 0x00, converts them from BCD to decimal.
Returns: A tuple containing the current time or None if reading fails.
Error Handling: Catches and reports any I/O errors during the read operation.
Reading the Temperature
python
Copy code
def read_temperature():
    ...
Process: Reads temperature registers (0x11 and 0x12) from the DS3231.
Calculation: Combines MSB and LSB to get the temperature in Celsius.
Returns: Temperature value or None if reading fails.
Error Handling: Catches and reports any I/O errors during the read operation.
6. EEPROM Read/Write Functions
Writing Bytes to EEPROM
python
Copy code
def write_bytes_to_eeprom(address, data):
    ...
Parameters: Starting address and data to write.
Process: Writes data in chunks defined by PAGE_SIZE to handle EEPROM page boundaries.
Delay: Introduces a 10ms delay after each write to ensure the EEPROM completes its write cycle.
Error Handling: Catches and reports any I/O errors during the write operation.
Reading Bytes from EEPROM
python
Copy code
def read_bytes_from_eeprom(address, length):
    ...
Parameters: Starting address and number of bytes to read.
Returns: The data read or None if reading fails.
Error Handling: Catches and reports any I/O errors during the read operation.
Writing and Reading Strings
python
Copy code
def write_string_to_eeprom(address, string):
    ...
    
def read_string_from_eeprom(address, length):
    ...
Purpose: Facilitate writing and reading UTF-8 encoded strings to and from EEPROM.
Encoding/Decoding: Converts strings to bytes before writing and decodes bytes back to strings after reading.
Error Handling: Reports any issues during encoding, decoding, or I/O operations.
7. Event Management
Event Class
python
Copy code
class Event:
    ...
Attributes:
event_name: Name of the event.
start_time: Event start time in Epoch format.
end_time: Event end time in Epoch format.
speaker_name: Name of the speaker.
description: Description of the event.
Purpose: Encapsulates all relevant information about a calendar event.
Saving an Event to EEPROM
python
Copy code
def save_event_to_eeprom(event, address):
    ...
Process:
Serializes the Event object into a bytearray with specific length constraints.
Writes the serialized data to EEPROM at the specified address.
Optionally verifies the write operation by reading back the data and comparing.
Error Handling: Checks for data size limits and handles I/O errors.
Loading an Event from EEPROM
python
Copy code
def load_event_from_eeprom(address):
    ...
Process:
Deserializes data from EEPROM starting at the specified address.
Reconstructs an Event object if valid data is found.
Error Handling: Validates lengths and content at each step, reporting issues as they arise.
Listing All Events
python
Copy code
def list_all_events(start_address=0, max_events=10, event_size=250):
    ...
Parameters:
start_address: EEPROM address to begin listing events.
max_events: Maximum number of events to list.
event_size: Allocated size per event in EEPROM.
Process: Iterates through EEPROM slots, attempting to load and display each event.
Output: Prints details of each valid event or indicates if no data is found.
8. I2C Bus Functions
python
Copy code
def scan_i2c_bus():
    ...
Purpose: Scans the I2C bus for connected devices and lists their addresses.
Output: Prints a list of found I2C devices or indicates if none are found.
9. EEPROM Management Functions
Wiping the EEPROM
python
Copy code
def wipe_eeprom():
    ...
Process:
Prompts the user for confirmation before proceeding.
Writes 0xFF to every byte in EEPROM in chunks defined by PAGE_SIZE.
Verifies the wipe by checking specific addresses.
Safety: Ensures the user is aware that this operation will erase all data.
Error Handling: Reports any failures during the wipe or verification process.
10. Interactive Menu Functions
Displaying the Menu
python
Copy code
def print_menu():
    ...
Purpose: Shows available options to the user for interacting with the badge's functionalities.
Main Interactive Loop
python
Copy code
def main():
    ...
Process:
Continuously displays the menu and prompts the user for input.
Executes functions based on user selection.
Handles invalid inputs and exceptions gracefully.
Provides options to set/read time, manage events, scan I2C, wipe EEPROM, and exit.
User Interaction: Ensures a user-friendly interface for managing the badge's features.
11. Entry Point
python
Copy code
if __name__ == "__main__":
    main()
Purpose: Ensures that the main function runs only when the script is executed directly, not when imported as a module.
Additional Notes
Event Storage Strategy: Each event is allocated 250 bytes in EEPROM, allowing for up to 16 events in a 4KB EEPROM.
Data Validation: The script performs thorough validation of input data, ensuring that strings do not exceed their maximum allowed lengths and that numerical inputs are within valid ranges.
Error Handling: Throughout the script, exceptions are caught and informative messages are printed to aid in debugging and user guidance.
Extensibility: The modular design allows for easy addition of new features or integration with other SAOs.

'''

# Import Necessary Libraries
from machine import I2C, Pin
import time
import sys

# ======================================
# Initialization
# ======================================

# Initialize I2C Interface
# Adjust scl and sda pins based on your hardware setup
# Example for ESP8266: scl=Pin(1), sda=Pin(0)
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)  # Adjust as per your board

# Define I2C Addresses for Devices
DS3231_I2C_ADDR = 0x68    # DS3231 RTC I2C address
EEPROM_I2C_ADDR = 0x57     # EEPROM I2C address (adjust based on EEPROM's address pins)

# EEPROM Specifications
EEPROM_SIZE = 4096          # Total EEPROM size in bytes (4KB)
PAGE_SIZE = 32              # EEPROM page size (common sizes: 16, 32, 64 bytes)

# ======================================
# Helper Functions
# ======================================

# BCD (Binary-Coded Decimal) Conversion Functions
def dec_to_bcd(val):
    """Convert a decimal number to BCD."""
    return (val // 10 << 4) + (val % 10)

def bcd_to_dec(val):
    """Convert a BCD number to decimal."""
    return ((val >> 4) * 10) + (val & 0x0F)

# ======================================
# DS3231 Real-Time Clock (RTC) Functions
# ======================================

def set_time(year, month, date, day, hour, minute, second):
    """
    Set the DS3231 RTC time.

    Parameters:
    - year (int): Full year (e.g., 2024)
    - month (int): Month (1-12)
    - date (int): Date (1-31)
    - day (int): Day of the week (1-7, Mon=1)
    - hour (int): Hour (0-23)
    - minute (int): Minute (0-59)
    - second (int): Second (0-59)
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
        i2c.writeto_mem(DS3231_I2C_ADDR, 0x00, data)
        print("Time set successfully.")
    except OSError as e:
        print("Failed to set time:", e)

def read_time():
    """
    Read the current time from DS3231 RTC.

    Returns:
    - tuple: (year, month, date, day, hour, minute, second) if successful
    - None: if reading fails
    """
    try:
        data = i2c.readfrom_mem(DS3231_I2C_ADDR, 0x00, 7)
        second = bcd_to_dec(data[0])
        minute = bcd_to_dec(data[1])
        hour = bcd_to_dec(data[2])
        day = bcd_to_dec(data[3])
        date = bcd_to_dec(data[4])
        month = bcd_to_dec(data[5] & 0x1F)
        year = bcd_to_dec(data[6]) + 2000
        print(f"Read Time: {year}-{month:02}-{date:02} {hour:02}:{minute:02}:{second:02}")
        return (year, month, date, day, hour, minute, second)
    except OSError as e:
        print("Failed to read time:", e)
        return None

def read_temperature():
    """
    Read the temperature from DS3231 RTC.

    Returns:
    - float: Temperature in Celsius if successful
    - None: if reading fails
    """
    try:
        temp_msb = i2c.readfrom_mem(DS3231_I2C_ADDR, 0x11, 1)[0]
        temp_lsb = i2c.readfrom_mem(DS3231_I2C_ADDR, 0x12, 1)[0]
        temp = temp_msb + ((temp_lsb >> 6) * 0.25)
        print(f"Read Temperature: {temp:.2f}°C")
        return temp
    except OSError as e:
        print("Failed to read temperature:", e)
        return None

# ======================================
# EEPROM Read/Write Functions
# ======================================

def write_bytes_to_eeprom(address, data):
    """
    Write bytes to EEPROM starting at the specified address.

    Parameters:
    - address (int): EEPROM address to start writing
    - data (bytes or bytearray): Data to write
    """
    while data:
        chunk = data[:PAGE_SIZE]
        data = data[PAGE_SIZE:]
        try:
            # Use writeto_mem with two-byte address for EEPROMs larger than 256 bytes
            i2c.writeto_mem(EEPROM_I2C_ADDR, address, chunk, addrsize=16)
            time.sleep_ms(10)  # Delay to ensure EEPROM write cycle completes
            address += len(chunk)
        except OSError as e:
            print("Failed to write to EEPROM:", e)
            break
    print("Bytes written to EEPROM successfully.")

def read_bytes_from_eeprom(address, length):
    """
    Read a specified number of bytes from EEPROM starting at the given address.

    Parameters:
    - address (int): EEPROM address to start reading
    - length (int): Number of bytes to read

    Returns:
    - bytes: Data read from EEPROM
    - None: if reading fails
    """
    try:
        # Use readfrom_mem with two-byte address for EEPROMs larger than 256 bytes
        data = i2c.readfrom_mem(EEPROM_I2C_ADDR, address, length, addrsize=16)
        return data
    except OSError as e:
        print("Failed to read from EEPROM:", e)
        return None

def write_string_to_eeprom(address, string):
    """
    Write a string to EEPROM at the specified address.

    Parameters:
    - address (int): EEPROM address to start writing
    - string (str): String to write
    """
    data = string.encode('utf-8')
    write_bytes_to_eeprom(address, data)
    print("String written to EEPROM successfully.")

def read_string_from_eeprom(address, length):
    """
    Read a string of a specified length from EEPROM starting at the given address.

    Parameters:
    - address (int): EEPROM address to start reading
    - length (int): Number of bytes to read

    Returns:
    - str: Decoded string
    - None: if reading or decoding fails
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

# ======================================
# Event Management
# ======================================

class Event:
    """
    Represents a calendar event.

    Attributes:
    - event_name (str): Name of the event
    - start_time (int): Event start time (Epoch time)
    - end_time (int): Event end time (Epoch time)
    - speaker_name (str): Name of the speaker
    - description (str): Description of the event
    """
    def __init__(self, event_name, start_time, end_time, speaker_name, description):
        self.event_name = event_name
        self.start_time = start_time  # Epoch time
        self.end_time = end_time      # Epoch time
        self.speaker_name = speaker_name
        self.description = description

def save_event_to_eeprom(event, address):
    """
    Serialize and save an event to EEPROM at the specified address.

    Parameters:
    - event (Event): Event object to save
    - address (int): EEPROM address to start writing
    """
    data = bytearray()
    
    # Serialize Event Name
    event_name_bytes = event.event_name.encode('utf-8')
    if len(event_name_bytes) > 50:
        print("Event name too long! Maximum 50 bytes allowed.")
        return
    data.append(len(event_name_bytes))
    data.extend(event_name_bytes)
    
    # Serialize Start Time (4 bytes)
    data.extend(event.start_time.to_bytes(4, 'big'))
    
    # Serialize End Time (4 bytes)
    data.extend(event.end_time.to_bytes(4, 'big'))
    
    # Serialize Speaker Name
    speaker_name_bytes = event.speaker_name.encode('utf-8')
    if len(speaker_name_bytes) > 50:
        print("Speaker name too long! Maximum 50 bytes allowed.")
        return
    data.append(len(speaker_name_bytes))
    data.extend(speaker_name_bytes)
    
    # Serialize Description
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
    
    # Write serialized data to EEPROM
    write_bytes_to_eeprom(address, data)
    print("Event saved successfully.")
    
    # Optional Verification: Read back the written data to confirm
    verification_data = read_bytes_from_eeprom(address, len(data))
    if verification_data == data:
        print("Verification Successful: Data written correctly.")
    else:
        print("Verification Failed: Data mismatch.")

def load_event_from_eeprom(address):
    """
    Load and deserialize an event from EEPROM starting at the specified address.

    Parameters:
    - address (int): EEPROM address to start reading

    Returns:
    - Event: Deserialized Event object
    - None: if loading fails or no valid event found
    """
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
    
    # Create Event Object
    event = Event(event_name, start_time, end_time, speaker_name, description)
    print("Event loaded successfully.")
    return event

def list_all_events(start_address=0, max_events=10, event_size=250):
    """
    List all stored events in the EEPROM.

    Parameters:
    - start_address (int): EEPROM address to start listing from
    - max_events (int): Maximum number of events to list
    - event_size (int): Size allocated for each event in EEPROM
    """
    print("\nListing All Events:")
    for i in range(max_events):
        addr = start_address + i * event_size
        print(f"\nChecking Event {i + 1} at EEPROM address {addr}:")
        event = load_event_from_eeprom(addr)
        if event:
            print(f"  Event {i + 1}:")
            print(f"    Name: {event.event_name}")
            start_tuple = time.localtime(event.start_time)
            print(f"    Start Time: {start_tuple[0]}-{start_tuple[1]:02}-{start_tuple[2]:02} "
                  f"{start_tuple[3]:02}:{start_tuple[4]:02}:{start_tuple[5]:02}")
            end_tuple = time.localtime(event.end_time)
            print(f"    End Time: {end_tuple[0]}-{end_tuple[1]:02}-{end_tuple[2]:02} "
                  f"{end_tuple[3]:02}:{end_tuple[4]:02}:{end_tuple[5]:02}")
            print(f"    Speaker: {event.speaker_name}")
            print(f"    Description: {event.description}")
        else:
            print(f"  Event {i + 1}: No valid data found.")

# ======================================
# I2C Bus Functions
# ======================================

def scan_i2c_bus():
    """
    Scan the I2C bus and list all connected devices.
    """
    devices = i2c.scan()
    if devices:
        print("I2C devices found:")
        for device in devices:
            print(f" - 0x{device:02X}")
    else:
        print("No I2C devices found.")

# ======================================
# EEPROM Management Functions
# ======================================

def wipe_eeprom():
    """
    Erase all data in the EEPROM with user confirmation and verification.
    """
    print("\n*** WARNING: This will erase all data in the EEPROM! ***")
    confirmation = input("Are you sure you want to wipe the EEPROM? (yes/no): ").strip().lower()
    if confirmation not in ['yes', 'y']:
        print("EEPROM wipe canceled.")
        return
    
    print("Wiping EEPROM...")
    # Iterate through the entire EEPROM in PAGE_SIZE chunks
    for addr in range(0, EEPROM_SIZE, PAGE_SIZE):
        remaining = EEPROM_SIZE - addr
        chunk_size = PAGE_SIZE if remaining >= PAGE_SIZE else remaining
        # Create a chunk filled with 0xFF (common erased state)
        chunk = bytearray([0xFF] * chunk_size)
        try:
            write_bytes_to_eeprom(addr, chunk)
            print(f"  Wiped {addr} to {addr + chunk_size - 1}")
        except Exception as e:
            print(f"Failed to wipe EEPROM at address {addr}: {e}")
            return
    
    print("EEPROM wiped successfully.")
    
    # Verification Step: Read back the first few bytes to confirm
    verification_addresses = [0, 250, 500, 750, 1000, 1250, 1500, 1750, 2000, 2250, 2500, 2750, 3000, 3250, 3500, 3750, 4000]
    all_wiped = True
    for v_addr in verification_addresses:
        data = read_bytes_from_eeprom(v_addr, 1)
        if data != b'\xFF':
            print(f"Verification Failed: Address {v_addr} contains {data.hex()} instead of FF.")
            all_wiped = False
    if all_wiped:
        print("Verification Successful: All checked addresses are wiped.")
    else:
        print("Verification Failed: Some addresses were not wiped correctly.")

# ======================================
# Interactive Menu Functions
# ======================================

def print_menu():
    """
    Display the interactive menu to the user.
    """
    print("\nMenu:")
    print("1. Set Time")
    print("2. Read Time")
    print("3. Read Temperature")
    print("4. Write Event to EEPROM")
    print("5. Read Event from EEPROM")
    print("6. Scan I2C Bus")
    print("7. List All Events")
    print("8. Wipe EEPROM")
    print("9. Exit")

def main():
    """
    Main loop to interact with the user through the interactive menu.
    """
    while True:
        print_menu()
        try:
            choice = input("Enter your choice: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting...")
            sys.exit()

        if choice == '1':
            # Set Time
            try:
                year = int(input("Enter year (YYYY): "))
                month = int(input("Enter month (1-12): "))
                date = int(input("Enter date (1-31): "))
                day = int(input("Enter day of week (1-7, Mon=1): "))
                hour = int(input("Enter hour (0-23): "))
                minute = int(input("Enter minute (0-59): "))
                second = int(input("Enter second (0-59): "))
                set_time(year, month, date, day, hour, minute, second)
            except ValueError:
                print("Invalid input. Please enter numerical values.")
        
        elif choice == '2':
            # Read Time
            try:
                time_data = read_time()
                if time_data:
                    year, month, date, day, hour, minute, second = time_data
                    print("Current time: {:04}-{:02}-{:02} {:02}:{:02}:{:02}".format(
                        year, month, date, hour, minute, second))
            except Exception as e:
                print("Error:", e)
        
        elif choice == '3':
            # Read Temperature
            try:
                temp = read_temperature()
                if temp is not None:
                    print("Temperature: {:.2f}°C".format(temp))
            except Exception as e:
                print("Error:", e)
        
        elif choice == '4':
            # Write Event to EEPROM
            try:
                event_name = input("Enter event name (Max 50 characters): ")
                if len(event_name.encode('utf-8')) > 50:
                    print("Event name too long! Maximum 50 bytes allowed.")
                    continue

                print("Enter event start time:")
                start_year = int(input("  Year (YYYY): "))
                start_month = int(input("  Month (1-12): "))
                start_date = int(input("  Date (1-31): "))
                start_hour = int(input("  Hour (0-23): "))
                start_minute = int(input("  Minute (0-59): "))
                start_second = int(input("  Second (0-59): "))
                start_tuple = (start_year, start_month, start_date, start_hour, start_minute, start_second, 0, 0)
                start_time = int(time.mktime(start_tuple))
                
                print("Enter event end time:")
                end_year = int(input("  Year (YYYY): "))
                end_month = int(input("  Month (1-12): "))
                end_date = int(input("  Date (1-31): "))
                end_hour = int(input("  Hour (0-23): "))
                end_minute = int(input("  Minute (0-59): "))
                end_second = int(input("  Second (0-59): "))
                end_tuple = (end_year, end_month, end_date, end_hour, end_minute, end_second, 0, 0)
                end_time = int(time.mktime(end_tuple))
                
                speaker_name = input("Enter speaker name (Max 50 characters): ")
                if len(speaker_name.encode('utf-8')) > 50:
                    print("Speaker name too long! Maximum 50 bytes allowed.")
                    continue

                description = input("Enter event description (Max 138 characters): ")
                if len(description.encode('utf-8')) > 138:
                    print("Description too long! Maximum 138 bytes allowed.")
                    continue

                event = Event(event_name, start_time, end_time, speaker_name, description)
                
                address = int(input("Enter EEPROM address to save the event (0-4095): "))
                if address < 0 or address > 4095:
                    print("Invalid EEPROM address. Must be between 0 and 4095.")
                    continue
                
                # Check if address is aligned with event_size (250 bytes)
                if address % 250 != 0:
                    print("Please enter an address that is a multiple of 250 (e.g., 0, 250, 500, ...).")
                    continue

                save_event_to_eeprom(event, address)
            except ValueError:
                print("Invalid input. Please enter numerical values where required.")
            except Exception as e:
                print("Error:", e)
        
        elif choice == '5':
            # Read Event from EEPROM
            try:
                address = int(input("Enter EEPROM address to read the event from (0-4095): "))
                if address < 0 or address > 4095:
                    print("Invalid EEPROM address. Must be between 0 and 4095.")
                    continue
                
                # Check if address is aligned with event_size (250 bytes)
                if address % 250 != 0:
                    print("Please enter an address that is a multiple of 250 (e.g., 0, 250, 500, ...).")
                    continue

                event = load_event_from_eeprom(address)
                if event:
                    print("\nEvent Details:")
                    print("Event Name:", event.event_name)
                    start_tuple = time.localtime(event.start_time)
                    print("Start Time: {:04}-{:02}-{:02} {:02}:{:02}:{:02}".format(
                        start_tuple[0], start_tuple[1], start_tuple[2], start_tuple[3], start_tuple[4], start_tuple[5]))
                    end_tuple = time.localtime(event.end_time)
                    print("End Time: {:04}-{:02}-{:02} {:02}:{:02}:{:02}".format(
                        end_tuple[0], end_tuple[1], end_tuple[2], end_tuple[3], end_tuple[4], end_tuple[5]))
                    print("Speaker Name:", event.speaker_name)
                    print("Description:", event.description)
                else:
                    print(f"No valid event found at EEPROM address {address}.")
            except ValueError:
                print("Invalid input. Please enter numerical values.")
            except Exception as e:
                print("Error:", e)
        
        elif choice == '6':
            # Scan I2C Bus
            scan_i2c_bus()
        
        elif choice == '7':
            # List All Events
            list_all_events()
        
        elif choice == '8':
            # Wipe EEPROM
            wipe_eeprom()
        
        elif choice == '9':
            # Exit
            print("Exiting...")
            break
        
        else:
            print("Invalid choice. Please try again.")

# ======================================
# Entry Point
# ======================================

# Run the interactive menu when the script is executed
if __name__ == "__main__":
    main()
