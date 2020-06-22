from serial import Serial

class BluetoothSerialPortController:
	ser = Serial('/dev/tty.HC-05-SerialPort')

	@classmethod
	def fast(cls):
		cls.ser.write(b'\x03')


	@classmethod
	def slow(cls):
		cls.ser.write(b'\x00')
