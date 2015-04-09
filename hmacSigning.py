from flask import Flask
from flask import request
from flask import Response
from urlparse import urlparse
import time
import hmac,hashlib
import urllib
global secretKey

secretKey	= 'dirtyLittleSecret'
app			= Flask(__name__)

@app.route("/checksum", methods=['GET'])
def checksum():	
	requestParamURL = request.args.get('url')

	urlParsed = urlparse(requestParamURL)

	# Set the checksum to expire 60 seconds from now.
	expireTime = str(int(time.time()) + 60)

	# Make the expireTime part of the hmac signed data so we can enforce the expiration of the signature
	hmacData = requestParamURL+"-"+expireTime
	checksum = hmac.new(secretKey, hmacData, hashlib.sha256).hexdigest()+"-"+expireTime

	responseData = urllib.quote_plus(requestParamURL)+"&checksum="+checksum
	
	return Response(responseData, status=200, mimetype='text/plain')

@app.route("/checkchecksum", methods=['GET'])
def checkchecksum():
	requestParamURL			= request.args.get('url')
	requestChecksum			= request.args.get('checksum')
	requestChecksumPieces	= requestChecksum.split("-", 1)
	requestChecksumTime		= requestChecksumPieces[1]
	requestChecksum			= requestChecksumPieces[0]
	currentTime				= int(time.time())

	hmacData = requestParamURL+"-"+requestChecksumTime
	checksum = hmac.new(secretKey, hmacData, hashlib.sha256).hexdigest()

	if currentTime <= int(requestChecksumTime) and requestChecksum == checksum:
		responseData	= "verified"
		status			= 200
	else:
		responseData    = "not verified"
		status			= 400

	return Response(responseData, status, mimetype='text/plain')

if __name__ == "__main__":
    app.run()

