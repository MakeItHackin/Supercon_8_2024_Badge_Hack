# CalendarReset.py
# MIT License
# See github.com/MakeItHackin/Supercon_8_2024_Badge_Hack for more information.

'''
Supercon 8 Schedule SAO Firmware
Conference: Supercon 8, Pasadena, CA
Dates: November 1-3, 2024
Organized by: Hackaday
Authors: MakeItHackin, CodeAllNight, Danner

Overview
This firmware is designed for the Raspberry Pi Pico Wireless badge featured at Supercon 8. The badge includes six Simple Add-On (SAO) ports providing power, I2C communication, and GPIO capabilities. This particular code manages the Schedule SAO, enabling functionalities such as EEPROM management, real-time clock (RTC) synchronization, and event scheduling.

Project Link: The Schedule SAO by DaveDarko  https://hackaday.io/project/198229-the-schedule-sao

Detailed Explanation of Sections
Section 1: I2C Initialization and Configuration
Purpose: Sets up the I2C communication required to interact with the RTC and EEPROM modules.
Configuration: Adjust the scl and sda pins according to your hardware setup. The frequency is set to 400kHz for optimal performance.
Section 2: Utility Functions for BCD Conversion
Purpose: Provides helper functions to convert between decimal and Binary-Coded Decimal (BCD), which is necessary for communicating with the DS3231 RTC.
Section 3: DS3231 RTC Functions
Functions:
set_time: Configures the RTC with the specified date and time.
read_time: Retrieves the current time from the RTC.
Section 4: EEPROM Read/Write Functions
Functions:
write_bytes_to_eeprom: Handles writing raw bytes to the EEPROM, managing page boundaries and ensuring data integrity.
read_bytes_from_eeprom: Reads a specified number of bytes from the EEPROM.
write_string_to_eeprom & read_string_from_eeprom: Facilitate writing and reading strings by encoding and decoding UTF-8 data.
Section 5: Event Class Definition
Purpose: Defines the Event class to encapsulate event-related data, including name, timings, speaker, and description.
Section 6: Event Storage Functions
Functions:
save_event_to_eeprom: Serializes an Event object and saves it to the EEPROM.
load_event_from_eeprom: Deserializes data from the EEPROM back into an Event object.
Section 7: EEPROM Management Functions
Function:
wipe_eeprom: Clears all data in the EEPROM by writing 0xFF to every byte, effectively resetting the storage.
Section 8: Main Function
Workflow:
EEPROM Wipe: Clears existing data to ensure a fresh state.
RTC Configuration: Sets the RTC to a predefined date and time.
Event Creation: Constructs an Event object with specific details.
Event Storage: Saves the event to the EEPROM.
Verification: Loads the event from EEPROM and prints the details to confirm successful storage.
Section 9: Execution Entry Point
Purpose: Ensures that the main function is executed when the script runs.
Additional Notes
Error Handling: The code includes comprehensive error handling to catch and report issues during I2C communication, EEPROM access, and data serialization/deserialization.

Data Validation: Before writing or reading data, the code validates lengths and formats to prevent corruption or unexpected behavior.

Modularity: Functions are modularized for clarity and reusability, making it easier to maintain and extend the codebase.

Logging: Informative print statements provide real-time feedback on the operations being performed, aiding in debugging and monitoring.

Customization: Adjust EEPROM_I2C_ADDR, DS3231_I2C_ADDR, and pin configurations as needed based on your specific hardware setup.



'''


from machine import I2C, Pin
import time
import sys

# =============================================================================
# Section 1: I2C Initialization and Configuration
# =============================================================================

# Initialize I2C with specific pins.
# Adjust 'scl' and 'sda' based on your hardware setup.
# Example for ESP8266: scl=Pin(1), sda=Pin(0)
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)  # Adjust as per your board

# I2C Device Addresses
DS3231_I2C_ADDR = 0x68       # Address for DS3231 RTC module
EEPROM_I2C_ADDR = 0x57        # Address for EEPROM (adjust based on EEPROM's address pins)

# EEPROM Specifications
EEPROM_SIZE = 4096             # Total EEPROM size in bytes (4KB)
PAGE_SIZE = 32                 # EEPROM page size (common sizes: 16, 32, 64 bytes)

# =============================================================================
# Section 2: Utility Functions for BCD Conversion
# =============================================================================

def dec_to_bcd(val):
    """Convert a decimal number to Binary-Coded Decimal (BCD)."""
    return (val // 10 << 4) + (val % 10)

def bcd_to_dec(val):
    """Convert a Binary-Coded Decimal (BCD) number to decimal."""
    return ((val >> 4) * 10) + (val & 0x0F)

# =============================================================================
# Section 3: DS3231 RTC Functions
# =============================================================================

def set_time(year, month, date, day, hour, minute, second):
    """
    Set the DS3231 RTC time.
    
    Parameters:
    - year: Full year (e.g., 2024)
    - month: Month (1-12)
    - date: Day of the month (1-31)
    - day: Day of the week (Monday=1, Sunday=7)
    - hour: Hour in 24-hour format (0-23)
    - minute: Minute (0-59)
    - second: Second (0-59)
    """
    year = year % 100  # Ensure two-digit year for DS3231
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
    Read the current time from the DS3231 RTC.
    
    Returns:
    A tuple containing (year, month, date, day, hour, minute, second)
    or None if reading fails.
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
        # Uncomment the next line to print the read time
        # print(f"Read Time: {year}-{month:02}-{date:02} {hour:02}:{minute:02}:{second:02}")
        return (year, month, date, day, hour, minute, second)
    except OSError as e:
        print("Failed to read time:", e)
        return None

# =============================================================================
# Section 4: EEPROM Read/Write Functions
# =============================================================================

def write_bytes_to_eeprom(address, data):
    """
    Write bytes to EEPROM starting at the specified address.
    
    Parameters:
    - address: Starting EEPROM address (integer)
    - data: Bytearray of data to write
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
    # Uncomment the next line to confirm successful write
    # print("Bytes written to EEPROM successfully.")

def read_bytes_from_eeprom(address, length):
    """
    Read a specified number of bytes from EEPROM starting at the given address.
    
    Parameters:
    - address: Starting EEPROM address (integer)
    - length: Number of bytes to read (integer)
    
    Returns:
    Bytearray of read data or None if reading fails.
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
    - address: Starting EEPROM address (integer)
    - string: String to write
    """
    data = string.encode('utf-8')
    write_bytes_to_eeprom(address, data)
    # Uncomment the next line to confirm successful write
    # print("String written to EEPROM successfully.")

def read_string_from_eeprom(address, length):
    """
    Read a string of a specified length from EEPROM starting at the given address.
    
    Parameters:
    - address: Starting EEPROM address (integer)
    - length: Number of bytes to read (integer)
    
    Returns:
    Decoded string or None if reading/decoding fails.
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

# =============================================================================
# Section 5: Event Class Definition
# =============================================================================

class Event:
    """Class representing a scheduled event."""
    def __init__(self, event_name, start_time, end_time, speaker_name, description):
        self.event_name = event_name
        self.start_time = start_time  # Epoch time (integer)
        self.end_time = end_time      # Epoch time (integer)
        self.speaker_name = speaker_name
        self.description = description

# =============================================================================
# Section 6: Event Storage Functions
# =============================================================================

def save_event_to_eeprom(event, address):
    """
    Serialize and save an event to EEPROM at the specified address.
    
    Parameters:
    - event: Event object to save
    - address: Starting EEPROM address (integer)
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

def load_event_from_eeprom(address):
    """
    Load and deserialize an event from EEPROM starting at the specified address.
    
    Parameters:
    - address: Starting EEPROM address (integer)
    
    Returns:
    Event object if successful, otherwise None.
    """
    # Read Event Name Length
    event_name_length_bytes = read_bytes_from_eeprom(address, 1)
    if event_name_length_bytes is None:
        print("Failed to read event name length.")
        return None
    event_name_length = event_name_length_bytes[0]
    
    # Check if the entire event slot is empty (all bytes set to 0xFF)
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
    
    # Create Event Object
    event = Event(event_name, start_time, end_time, speaker_name, description)
    print("Event loaded successfully.")
    return event

# =============================================================================
# Section 7: EEPROM Management Functions
# =============================================================================

def wipe_eeprom():
    """
    Erase all data in the EEPROM without user confirmation.
    Fills the EEPROM with 0xFF bytes.
    """
    print("Wiping EEPROM...")
    # Iterate through the entire EEPROM in PAGE_SIZE chunks
    for addr in range(0, EEPROM_SIZE, PAGE_SIZE):
        remaining = EEPROM_SIZE - addr
        chunk_size = PAGE_SIZE if remaining >= PAGE_SIZE else remaining
        # Create a chunk filled with 0xFF
        chunk = bytearray([0xFF] * chunk_size)
        try:
            write_bytes_to_eeprom(addr, chunk)
        except Exception as e:
            print(f"Failed to wipe EEPROM at address {addr}: {e}")
            return
    print("EEPROM wiped successfully.")

# =============================================================================
# Section 8: Main Function
# =============================================================================

def main():
    """
    Main function to execute automated tasks:
    1. Wipe EEPROM.
    2. Set RTC time.
    3. Save an event to EEPROM.
    4. Load and verify the saved event.
    """
    # Step 1: Wipe EEPROM without confirmation
    wipe_eeprom()
    
    # Step 2: Set time to November 3, 2024 at 4:45 PM
    year = 2024
    month = 11
    date = 3
    # Calculate day of the week (Monday=1, Sunday=7)
    # November 3, 2024, is a Sunday
    day = 7  # Sunday
    hour = 16  # 4 PM in 24-hour format
    minute = 48
    second = 30

    set_time(year, month, date, day, hour, minute, second)
    
    # Step 3: Read back time and print
    time_data = read_time()
    if time_data:
        year, month, date, day, hour, minute, second = time_data
        print("Current time set to: {:04}-{:02}-{:02} {:02}:{:02}:{:02}".format(
            year, month, date, hour, minute, second))
    else:
        print("Failed to read time from RTC.")

    # Step 4: Create an event with specified information
    event_name = "Ceremony"
    # Event start time: November 3, 2024, at 5:00 PM
    start_time_tuple = (2024, 11, 3, 17, 0, 0, 0, 0)
    start_time = int(time.mktime(start_time_tuple))
    
    # Event end time: November 3, 2024, at 6:00 PM
    end_time_tuple = (2024, 11, 3, 18, 0, 0, 0, 0)
    end_time = int(time.mktime(end_time_tuple))
    
    speaker_name = "Elliot"
    description = "Badges!"
    
    event = Event(event_name, start_time, end_time, speaker_name, description)
    
    # Step 5: Save event to EEPROM at address 0
    address = 0
    save_event_to_eeprom(event, address)
    
    # Step 6: Read back event at address 0 to confirm verification
    event_loaded = load_event_from_eeprom(address)
    if event_loaded:
        print("\nEvent Details Loaded from EEPROM:")
        print("Event Name:", event_loaded.event_name)
        
        # Convert epoch time to local time tuple for display
        start_tuple = time.localtime(event_loaded.start_time)
        print("Start Time: {:04}-{:02}-{:02} {:02}:{:02}:{:02}".format(
            start_tuple[0], start_tuple[1], start_tuple[2],
            start_tuple[3], start_tuple[4], start_tuple[5]))
        
        end_tuple = time.localtime(event_loaded.end_time)
        print("End Time: {:04}-{:02}-{:02} {:02}:{:02}:{:02}".format(
            end_tuple[0], end_tuple[1], end_tuple[2],
            end_tuple[3], end_tuple[4], end_tuple[5]))
        
        print("Speaker Name:", event_loaded.speaker_name)
        print("Description:", event_loaded.description)
    else:
        print("Failed to load event from EEPROM.")

# =============================================================================
# Section 9: Execution Entry Point
# =============================================================================

if __name__ == "__main__":
    main()
