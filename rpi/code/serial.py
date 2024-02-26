import spidev
import RPi.GPIO as GPIO
import time
from struct import unpack


ADXL345_MG2G_MULTIPLIER = 0.004  # < 4mg per lsb
SENSORS_GRAVITY_STANDARD = 9.80665
ACC_CONVERSION = 2 * 16.0 / 8192.0

# Setup SPI
spi = spidev.SpiDev()
spi.open(
    0, 0
)  # Using SPI bus 0, device 0 (device is ignored but necessary for opening)
spi.max_speed_hz = 2000000  # 5 MHz
spi.mode = 3  # ADXL345 operates in mode 3
spi.bits_per_word = 8  # 8 bits per word


# Setup GPIO for CS pins
cs_pins = [8]  # GPIO pins for CS of each ADXL345
GPIO.setmode(GPIO.BCM)
for pin in cs_pins:
    GPIO.setup(pin, GPIO.OUT, initial=GPIO.HIGH)

# ADXL345 Registers
REG_DATA_FORMAT = 0x31
REG_BW_RATE = 0x2C
REG_POWER_CTL = 0x2D
REG_DATA_START = 0x32
REG_READ = 0x80
REG_MULTI_BYTE = 0x40


# Write to register
def write_register(cs_pin, reg_address, data):
    GPIO.output(cs_pin, GPIO.LOW)
    spi.xfer2([reg_address, data])
    GPIO.output(cs_pin, GPIO.HIGH)


# Read from register
# We read 6 bytes of data from the register
def read_register(cs_pin, reg_address, length=6):
    # Set the cs_pin to low to allow communication with the device
    GPIO.output(cs_pin, GPIO.LOW)
    data = spi.xfer2(
        [reg_address | REG_READ | (REG_MULTI_BYTE if length > 1 else 0)] + [0] * length
    )[1:]
    # Set the cs_pin to high to disable communication with the device
    GPIO.output(cs_pin, GPIO.HIGH)
    return data


# Initialize ADXL345
def init_adxl345(cs_pin):
    # *****
    write_register(cs_pin, REG_BW_RATE, 0x0F)  # 100 Hz

    # *****
    # The DATA_FORMAT register controls the presentation of data to
    # Register 0x32 through Register 0x37. All data, except that for the
    # ±16 g range, must be clipped to avoid rollover.
    # SELF_TEST bit is set to 0, so no self-test
    # SPI bit is set to 0, so 4-wire SPI mode
    # INT_INVERT bit is set to 0, so interrupts are active high
    # Justification bit is set to 0, so right-justified with sign extension

    write_register(cs_pin, REG_DATA_FORMAT, 0x0B)  # +/- 4g; 0.004g/LSB
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
    data = read_register(cs_pin, REG_DATA_START, 6)
    # Interpret the data as signed 16-bit values
    x = (data[1] << 8) | data[0]
    if x & (1 << 15):  # Check if x is negative
        x -= 1 << 16
    y = (data[3] << 8) | data[2]
    if y & (1 << 15):  # Check if y is negative
        y -= 1 << 16
    z = (data[5] << 8) | data[4]
    if z & (1 << 15):  # Check if y is negative
        z -= 1 << 16
    x = x * ACC_CONVERSION
    y = y * ACC_CONVERSION
    z = z * ACC_CONVERSION
    return x, y, z


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
    # print the acceleration data every second
    last_time = time.time()
    while True:
        for i, pin in enumerate(cs_pins):
            x, y, z = read_acceleration(pin)
            if time.time() - last_time > 1:
                print(f"ADXL345 #{i+1}: x={x}, y={y}, z={z}", flush=True)
                last_time = time.time()
            # time.sleep(0.2)
except KeyboardInterrupt:
    print("Program stopped")
finally:
    GPIO.cleanup()  # Clean up GPIO on CTRL+C exit
