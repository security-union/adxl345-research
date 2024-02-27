
## Serial and I2C

Seems like adding a 3rd accelerometer using SPI is not possible, so we will use I2C.

1. Connect the serial to raspberry pi following this diagram:

```
[Raspberry Pi]    SPI Interface    [ADXL345 #1 (SPI)]    [ADXL345 #2 (SPI)]    [ADXL345 (I2C)]
+-------------+                    +----------------+    +----------------+    +--------------+
|             |                    |                |    |                |    |              |
|          GPIO 10 (MOSI)----------|SDI-------------|----|SDI             |    |              |
|             |                    |                |    |                |    |              |
|          GPIO 9 (MISO)-----------|SDO-------------|----|SDO             |    |              |
|             |                    |                |    |                |    |              |
|          GPIO 11 (SCLK)----------|SCLK------------|----|SCLK            |    |              |
|             |                    |                |    |                |    |              |
|          GPIO 17 (CS)------------|CS              |    |                |    |              |
|             |                    |                |    |                |    |              |
|          GPIO 22 (CS)----------------------------------|CS              |    |              |
|             |                    |                |    |                |    |              |
|          GPIO 2 (SDA)--------------------------------------------------------|SDA           |
|             |                    |                |    |                |    |              |
|          GPIO 3 (SCL)--------------------------------------------------------|SCL           |
|             |                    |                |    |                |    |              |
|          3.3V--------------------|VCC-------------|----|VCC-------------|----|VCC           |
|             |                    |                |    |                |    |              |
|          GND---------------------|GND-------------|----|GND-------------|----|GND           |
+-------------+                    +----------------+    +----------------+    +--------------+
```

2. Rename the .env.template to .env and set your RPI IP address and username.

3. Run the following command to install the serial tools and start:
```
cd rpi
deploy_and_run.sh --program serial.py  --install 
```

It will ask for the password of the RPI a couple of times, this is expected.
