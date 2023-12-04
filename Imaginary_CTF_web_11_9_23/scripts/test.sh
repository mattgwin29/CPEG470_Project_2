import random, time
from randcrack import RandCrack

def toUnsignedInt(num_bits):
	return f"{num_bits & 0xffff_ffff:032b}"

if __name__ == "__main__":


	random.seed(23)

	rc = RandCrack()

	for i in range(624):
		rInt = random.getrandbits(32)
		if (i%2) == 0:
			rInt = -1*rInt +(1 << 32)

		#bits = toUnsignedInt(rInt)
		bits = rInt
		print(bits)
		base2Unsigned = int(toUnsignedInt(rInt), 2)

		rc.submit(base2Unsigned)

	print("Random result: {}\nCracker result: {}"
		.format(random.randrange(0, 4294967295), rc.predict_randrange(0, 4294967295)))	
