import spidev
import RPi.GPIO as GPIO
import time


ADXL345_MG2G_MULTIPLIER= 0.004 # < 4mg per lsb
SENSORS_GRAVITY_STANDARD = 9.80665

# Setup SPI
spi = spidev.SpiDev()
spi.open(0, 0)  # Using SPI bus 0, device 0 (device is ignored but necessary for opening)
spi.max_speed_hz = 5000000  # 5 MHz
spi.mode = 3  # ADXL345 operates in mode 3
spi.bits_per_word = 8  # 8 bits per word
spi.no_cs = True  # We will use our own CS pins


# Setup GPIO for CS pins
cs_pins = [17]  # GPIO pins for CS of each ADXL345
GPIO.setmode(GPIO.BCM)
for pin in cs_pins:
    GPIO.setup(pin, GPIO.OUT, initial=GPIO.HIGH)

# ADXL345 Registers
REG_DATA_FORMAT = 0x31
REG_BW_RATE = 0x2C
REG_POWER_CTL = 0x2D
REG_DATA_START = 0x32

# Write to register
def write_register(cs_pin, reg_address, data):
    GPIO.output(cs_pin, GPIO.LOW)
    spi.xfer2([reg_address, data])
    GPIO.output(cs_pin, GPIO.HIGH)

# Read from register
# We read 6 bytes of data from the register
def read_register(cs_pin, reg_address, length = 6):
    # Set the cs_pin to low to allow communication with the device
    GPIO.output(cs_pin, GPIO.LOW)
    spi.xfer2([reg_address | 0x80])  # Read operation, MSB = 1
    data = spi.xfer2([0x00] * length)  # Dummy write to read data
    # Set the cs_pin to high to disable communication with the device
    GPIO.output(cs_pin, GPIO.HIGH)
    return data

# Initialize ADXL345
def init_adxl345(cs_pin):
    # *****
    # The DATA_FORMAT register controls the presentation of data to
    # Register 0x32 through Register 0x37. All data, except that for the
    # ±16 g range, must be clipped to avoid rollover.

    # SELF_TEST bit is set to 0, so no self-test
    # SPI bit is set to 0, so 4-wire SPI mode
    # INT_INVERT bit is set to 0, so interrupts are active high
    # Justification bit is set to 0, so right-justified with sign extension
    # D1 = 0 and D0 = 1, so range is +/- 4g
    write_register(cs_pin, REG_DATA_FORMAT, 0x09)  # +/- 4g; 0.004g/LSB
    # *****
    # The BW_RATE register is used to set Data rate and power mode control

    # LOW_POWER bit is set to 0, so normal operation
    # RATE bits are set to 0x06, so 6.25 Hz
    write_register(cs_pin, REG_BW_RATE, 0x0A)
    # *****
    # POWER_CTL Power-saving features control
    # Link Bit is set to 0 the inactivity and activity functions are concurrent.
    # AUTO_SLEEP bit is set to 0, so auto-sleep is disabled.
    # Measure bit is set to 1, so measurement mode is enabled.
    # Sleep bit is set to 0, so device is in normal mode.
    # WAKEUP bits are set to 0, so 8 Hz
    write_register(cs_pin, REG_POWER_CTL, 0x08)  # Measurement mode

# Read acceleration data from ADXL345
# These six bytes (Register 0x32 to Register 0x37) are eight bits
# each and hold the output data for each axis. Register 0x32 and
# Register 0x33 hold the output data for the x-axis, Register 0x34 and
# Register 0x35 hold the output data for the y-axis, and Register 0x36
# and Register 0x37 hold the output data for the z-axis. The output
# data is twos complement, with DATAx0 as the least significant byte
# and DATAx1 as the most significant byte, where x represent X,
# Y, or Z. The DATA_FORMAT register (Address 0x31) controls the
# format of the data. It is recommended that a multiple-byte read of all
# registers be performed to prevent a change in data between reads
# of sequential registers.
# Function to read acceleration data
def read_acceleration(cs_pin):
    # Initiate burst read from DATAX0 (0x32). Add 0x80 to indicate read operation,
    # and 0x40 to enable multi-byte read
    reg_address = 0x32 | 0x80 | 0x40
    GPIO.output(cs_pin, GPIO.LOW)
    # Send the address and read 6 bytes of data (X, Y, Z each two bytes)
    data = spi.xfer2([reg_address] + [0x00]*6)
    GPIO.output(cs_pin, GPIO.HIGH)

    # Combine the bytes for each axis
    x = (data[1] << 8) | data[2]
    y = (data[3] << 8) | data[4]
    z = (data[5] << 8) | data[6]

    # Adjust for 10-bit resolution and sign extend if necessary
    if x & (1 << 9): x -= (1 << 10)
    if y & (1 << 9): y -= (1 << 10)
    if z & (1 << 9): z -= (1 << 10)

    # Convert to g values based on the range you configured the ADXL345 for
    # Assuming the range is +/- 4g (0x01 in the DATA_FORMAT register)
    scale_factor = 4.0 / 1024
    x_g = x * scale_factor
    y_g = y * scale_factor
    z_g = z * scale_factor

    return x_g, y_g, z_g

# Convert to 2's complement
def twos_complement(raw_val):
    if raw_val & (1 << 9):  # If the 10th bit is set, it's negative
        raw_val -= (1 << 10)  # Subtract 2^10 to extend the sign
    return raw_val
# Initialize all ADXL345s
for pin in cs_pins:
    init_adxl345(pin)
    time.sleep(0.1)  # Short delay after initialization
    # verify communication by reading the device ID
    device_id = read_register(pin, 0x00, 1)
    print(f"ADXL345 on CS pin {pin} has device ID: {device_id[0]}", flush=True)
    if device_id[0] != 0xE5:
        print(f"ADXL345 on CS pin {pin} is not communicating properly", flush=True)
        exit(1)

try:
    while True:
        for i, pin in enumerate(cs_pins):
            x, y, z = read_acceleration(pin)
            # x = x * ADXL345_MG2G_MULTIPLIER * SENSORS_GRAVITY_STANDARD
            # y = y * ADXL345_MG2G_MULTIPLIER * SENSORS_GRAVITY_STANDARD
            # z = z * ADXL345_MG2G_MULTIPLIER * SENSORS_GRAVITY_STANDARD
            # Converting to g-Forces
            # To convert the 10-bit value to g-forces, 
            # you need to know the scale factor, which depends on the selected g-range. 
            # For a ±4g range, each bit represents 4g / 2^10 (about 0.0039g per bit):
            print(f"ADXL345 #{i+1}: x={x}, y={y}, z={z}", flush=True)
        #time.sleep(0.2)
except KeyboardInterrupt:
    print("Program stopped")
finally:
    GPIO.cleanup()  # Clean up GPIO on CTRL+C exit
