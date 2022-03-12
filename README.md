# disaster_radio_micropython
A Disaster.radio implementation in MicroPython for esp32, including an sx1278 esp32 micropython low-level library. 
building something like Armachat, but UNDERSTANDABLE. Base protocol is Disaster.radio.
LoraLevel3 protocol is under development, will be documented later.
The goal is to implement an off-grid text messgaing with encryption, optional geo sharing, and payment information delivery (something like VERY simplified SWIFT, idk.)
It can finction as a mesh of "blind" Lora nodes, intercating with via web interface. Also planning to build a standalone qwerty pager like Armachat. Hardware will be open source as well. 
Planning to support "One node - one user" paradigm, as well as "mesh of (fixed & mobile) nodes <-> multiple clients via WiFi", kind of alternative cell network.


All you need to build a node is: 
* an ESP32
* an sx1276/78 module
* a handful of wires
Building guide will be available later, but experienced DIYers can easily figure out from the code how to connect sx1278 to esp32.
It can finction as a mesh of "blind" Lora nodes, intercating with via web interface. 
