#!/usr/bin/python

import requests
import randcrack


def toUnsignedInt(num_bits):
	return f"{num_bits & 0xffff_ffff:032b}"
	

if __name__ == "__main__":
	headers = {'User-Agent': 'Mozilla/5.0'}
	payload = {'offering':'niceusername','bribe':'123456'}

	session = requests.Session()

	rc = randcrack.RandCrack()
	negative = False
	for i in range(624):
		print("Iteration " + str(i))
		result = session.post('http://150.136.137.215/report',headers=headers,data=payload,verify=False)
		#result = session.post('http://127.0.0.1:5000/report',headers=headers,data=payload,verify=False)

		cont = str(result.content)
		number = cont[cont.find("was")+len("was")+1:len(cont)-1].strip()
		print(number)
		if (int(number) < 0):
			negative = True
		else:
			negative = False
		unsigned = int(number) + (1<<32)
		print("unsigned -> " + str(unsigned))
		rc.submit(unsigned)
		#print(unsigned)
		#backToDec = int(unsigned, 2)
		#print(backToDec) # 32bit integer NOW ungsigned decimal form
		#rc.submit(backToDec)
		#if (number.find("-") != -1):
			#print("submitting " + (str(number)))
		#	rc.submit(int(str(number)) * -1)
		#else:
		#	rc.submit(int(str(number)))
	prediction = rc.predict_randrange(0, 4294967295)
	convertedBack = prediction - (1 << 32)
	print("Prediction: ", convertedBack)
	payload['bribe'] = str(convertedBack)
	print(payload['bribe'])
	result = session.post('http://150.136.137.215/report',headers=headers,data=payload,verify=False)
	print(result.content)
