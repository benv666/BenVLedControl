# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
import octoprint.events
import requests
from neopixel import *
from rpi_ws281x import *

'''
	BenV's octoprint Led control

	Since I'm running this anyway I migth as well use it for snooping gcode commands.

	Concepts:
	- "looplicht" based on printer movement direction
	- print progress indicated by certain led color (or maybe flashyness, duty cycle based on percentage orso for certain leds. Maybe only the corner leds.)

'''

class BenVLedPlugin(octoprint.plugin.StartupPlugin,
				octoprint.plugin.ProgressPlugin,
				octoprint.plugin.EventHandlerPlugin,
				octoprint.plugin.SettingsPlugin,
				octoprint.plugin.AssetPlugin,
				octoprint.plugin.TemplatePlugin):

	def initialize(self):
		self._initialized = False

		# LED strip configuration:
		LED_COUNT      = self._settings.get(["ledcontrol", "led_count"])
		LED_PIN        = self._settings.get(["ledcontrol", "led_gpio"])
		LED_FREQ_HZ    = self._settings.get(["ledcontrol", "led_freq"])
		LED_DMA        = self._settings.get(["ledcontrol", "led_dma"])
		LED_BRIGHTNESS = self._settings.get(["ledcontrol", "led_brightness"])
		LED_CHANNEL    = self._settings.get(["ledcontrol", "led_channel"])
		LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
		LED_STRIP      = rpi_ws281x.ws.WS2811_STRIP_GRB   # Strip type and colour ordering

		# (self, num, pin, freq_hz=800000, dma=5, invert=False, brightness=128, channel=0, gamma=None):
		# self._strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
		self._strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, None)
		# Intialize the library (must be called once before other functions).
		self._strip.begin()
		self._initialized = True

		# Light every other LED
		color = Color(255, 128, 128)
		for i in range(strip.numPixels()):
			strip.setPixelColor(i, color)
		strip.show()

	def get_settings_defaults(self):
		return dict(
			enabled=True,
			ledcontrol=dict(
				startup=False,
				printstart=False,
				printfailed=True,
				printdone=True,
				printcancel=False,
				printpause=False,
				printresume=False,
				timelapsestart=False,
				timelapsefinish=True,
				timelapsefailed=True,
				printerconnected=False,
				printerdisconnected=False,
				printererror=True,
				interval=0,
				led_freq=800000,# LED signal frequency in hertz (usually 800khz)
				led_gpio=18,# GPIO pin connected to the pixels (18 uses PWM).
				led_dma=10,# DMA channel to use for generating signal (try 10)
				led_count=32, # Number of addressable LEDs/(chips).
				led_brightness=255,# Set to 0 for darkest and 255 for brightest
				led_channel=0# set to '1' for GPIOs 13, 19, 41, 45 or 53
			)
		)

	def get_template_configs(self):
		return [
			dict(type="settings", custom_bindings=False)
		]

	def on_print_progress(self, storage, path, progress):
		global timerProgress
		timerProgress = progress

	def on_after_startup(self):
		self._logger.info("BenV Led Plugin Starting up...")
		if not self._settings.get(['enabled']):
			return

		try:
			self.initialize()
		except Exception as e:
			self._initialized = False
			self._logger.warning("Error initializing! %s" % str(e))
		 	return

	def on_event(self, event, payload):
		# Return if not enabled
		if not self._settings.get(['enabled']):
			self._logger.info("Not enabled.")
			return

		# Handle events
		if event == 'Connected':
			if self._settings.get(['ledcontrol','printerconnected']):
				return
		if event == 'Disconnected':
			if self._settings.get(['ledcontrol','printerdisconnected']):
				return
		if event == 'Error':
			if self._settings.get(['ledcontrol','printererror']):
				return
		if event == 'PrintStarted':
			if self._settings.get(['ledcontrol','printstart']):
				return
		if event == 'PrintFailed':
			if self._settings.get(['ledcontrol','printfailed']):
				return
		if event == 'PrintDone':
			if self._settings.get(['ledcontrol','printdone']):
				return
		if event == 'PrintCancelled':
			if self._settings.get(['ledcontrol','printcancel']):
				return
		if event == 'PrintPaused':
			if self._settings.get(['ledcontrol','printpause']):
				return
		if event == 'PrintResumed':
			if self._settings.get(['ledcontrol','printresume']):
				return
		if event == 'MovieRendering':
			if self._settings.get(['ledcontrol','timelapsestart']):
				return
		if event == 'MovieDone':
			if self._settings.get(['ledcontrol','timelapsefinish']):
				return
		if event == 'MovieFailed':
			if self._settings.get(['ledcontrol','timelapsefailed']):
				return

	def hook_gcode(self, comm_instance, phase, cmd, cmd_type, gcode, *args, **kwargs):
		# Return if not enabled
		if not self._settings.get(['enabled']):
			self._logger.info("Not enabled, will not send.")
			return

		# Handle pause/resume gcodes
		if gcode and gcode == "M24":
			if self._settings.get(['ledcontrol','printresume']):
				return
		if gcode and gcode == "M25":
			if self._settings.get(['ledcontrol','printpause']):
				return
		if gcode and gcode == "M226":
			if self._settings.get(['ledcontrol','printpause']):
				return
		if gcode and gcode == "M600":
			if self._settings.get(['ledcontrol','printpause']):
				return

# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "BenV's WS281x Led Control for OctoPrint"

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = BenVLedPlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.comm.protocol.gcode.sent": __plugin_implementation__.hook_gcode
	}

