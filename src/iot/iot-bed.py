import os
import json
import logging
import subprocess
import time
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient

logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

class sertaBLEController:
	def __init__(self, addr, pretend=False):
		self.pretend = pretend
		self.addr = addr
		self.handle = "0x0020"
		self.commands = {
			"Flat Preset": "e5fe1600000008fe",
			"ZeroG Preset": "e5fe1600100000f6",
			"TV/PC Preset": "e5fe1600400000c6",
			"Head Up Preset": "e5fe160080000086",
			"Lounge Preset": "e5fe1600200000e6",
			"Massage Head Add": "e5fe1600080000fe",
			"Massage Head Min": "e5fe160000800086",
			"Massage Foot Add": "e5fe160004000002",
			"Massage Foot Min": "e5fe160000000105",
			"Head and Foot Massage On": "e5fe160001000005",
			"Massage Timer": "e5fe160002000004",
			"Lift Head": "e5fe160100000005",
			"Lower Head": "e5fe160200000004",
			"Lift Foot": "e5fe160400000002",
			"Lower Foot": "e5fe1608000000fe"
		}

	def sendCommand(self, name):
		cmd = self.commands.get(name, None)
		if cmd is None:
			raise Exception("Command not found: " + name)

		for retry in range(3):
			print("sending command: %s" % cmd)
			cmd_args = [
				"/usr/bin/gatttool",
				"-b", self.addr,
				"--char-write",
				"--handle", self.handle,
				"--value", cmd
			]
			if self.pretend:
				print(' '.join(cmd_args))
				res = 0
			else:
				res = subprocess.call(cmd_args)
			print("command sent")
			if res == 0:
				break
			else:
				print("Command error, retrying in 2 seconds")
				time.sleep(2)
		return res == 0

class shadowCallbackContainer:
	def __init__(self, deviceShadowInstance, bleController):
		self.deviceShadowInstance = deviceShadowInstance
		self.bleController = bleController

	# Custom Shadow callback
	def customShadowCallback_Delta(self, payload, responseStatus, token):
		# payload is a JSON string ready to be parsed using json.loads(...)
		# in both Py2.x and Py3.x
		print("Received a delta message:")
		payloadDict = json.loads(payload)
		deltaMessage = json.dumps(payloadDict["state"])
		print(deltaMessage)

		newPayload = {
			"state": {
				"reported": {
				}
			}
		}

		if "preset" in payloadDict["state"]:
			preset = payloadDict["state"]["preset"]
			if preset == "zero-g":
				res = self.bleController.sendCommand("ZeroG Preset")
				if not res:
					print("Error sending command for preset: " + preset)
				else:
					newPayload["state"]["reported"]["preset"] = preset
			elif preset == "flat":
				res = self.bleController.sendCommand("Flat Preset")
				if not res:
					print("Error sending command for preset: " + preset)
				else:
					newPayload["state"]["reported"]["preset"] = preset
			elif preset == "tv":
				res = self.bleController.sendCommand("TV/PC Preset")
				if not res:
					print("Error sending command for preset: " + preset)
				else:
					newPayload["state"]["reported"]["preset"] = preset
			else:
				print("Unknown preset:" + preset)

		elif "massage" in payloadDict["state"]:
			massagePercent = payloadDict["state"]["massage"]

			if massagePercent < 0:
				num_cmds = int((100 - abs(massagePercent)) / 25)
				print("Turning OFF massage with %d commands." % num_cmds)
				if num_cmds != 4:
					for i in range(num_cmds):
						self.bleController.sendCommand("Head and Foot Massage On")
						time.sleep(2.5)
				newPayload["state"]["reported"]["massage"] = 0
				newPayload["state"]["desired"] = {"massage": 0}
			else:
				res = self.bleController.sendCommand("Head and Foot Massage On")
				if not res:
					print("Error sending command for massage")
				else:
					newPayload["state"]["reported"]["massage"] = massagePercent
		else:
			print("WARNING: unhandled action, payload: " + deltaMessage)

		print("Request to update the reported state...")
		self.deviceShadowInstance.shadowUpdate(json.dumps(newPayload), None, 5)
		print("Sent.")

def main():

	endpoint = os.environ.get("IOT_ENDPOINT", None)
	thing_name = os.environ.get("THING_NAME", None)
	ble_address = os.environ.get("BLE_ADDRESS", None)
	pretend = os.environ.get("BLE_PRETEND", "false").lower() == "true"

	if endpoint is None:
		raise Exception("IOT_ENDPOINT env not set")
	if thing_name is None:
		raise Exception("THING_NAME env not set")
	if ble_address is None:
		raise Exception("BLE_ADDRESS env not set")

	ble = sertaBLEController(ble_address, pretend)

	client = AWSIoTMQTTShadowClient(thing_name)
	client.configureEndpoint(endpoint, 8883)
	client.configureCredentials("root-CA.crt", "device-key.pem", "device.pem")

	client.configureAutoReconnectBackoffTime(1, 32, 20)
	client.configureConnectDisconnectTimeout(10)  # 10 sec
	client.configureMQTTOperationTimeout(5)  # 5 sec

	client.connect()

	shadow = client.createShadowHandlerWithName(thing_name, True)
	shadowCallbackContainer_IoTBed = shadowCallbackContainer(shadow, ble)
	shadow.shadowRegisterDeltaCallback(shadowCallbackContainer_IoTBed.customShadowCallback_Delta)

    # Loop forever
	while True:
		time.sleep(0.1)

if __name__ == "__main__":
    main()
