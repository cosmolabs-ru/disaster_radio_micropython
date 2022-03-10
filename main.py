from sx1278 import SX1278
from utime import sleep

print("I'm alive!")
sleep(0.5)
lora = SX1278(5, 2, 14)

lora_id = hex(lora.read_reg(lora.regmap.regVersion)[1])
print("LoRa chip ID: ", lora_id)

while 1:
    lora.write_reg(lora.regmap.regOpMode, 0x80)
    print("OpMode: ", lora.read_reg(lora.regmap.regOpMode))
    sleep(1)
    lora.write_reg(lora.regmap.regOpMode, 0x81)
    print("OpMode: ", lora.read_reg(lora.regmap.regOpMode))
    sleep(1)
