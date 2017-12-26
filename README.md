# BenVLedControl

This plugin allows my WS281x based LED strips to do something fancy based on what my printer is doing.
Uses the rpi_ws281x library for driving the actual LED strip.

LED strips are directly connected to the RPi3 on GPIO18, but powered through my printer's power supply.

## Setup

Install via the bundled [Plugin Manager](https://github.com/foosel/OctoPrint/wiki/Plugin:-Plugin-Manager)
or manually using this URL:

    https://github.com/benv666/BenVLedControl/archive/master.zip

**TODO:** Describe how to install your plugin, if more needs to be done than just installing it via pip or through
the plugin manager.

## Configuration

LED Count: amount of LEDs (well, control chips) in the strip.
  In my case there are 4 strips of equal length, all have 8 chips with each 3 LEDs making for a total of 96 LEDs (meaning 32 controllable LEDs in total).
  This means that LED 1, 9, 17 and 25 are considered "corner" LEDs.
