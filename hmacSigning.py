from flask import Flask
from flask import request
from flask import Response
import time
import hmac,hashlib
import urllib
import json
import bleach

global secretKey

secretKey	= 'dirtyLittleSecret'
app			= Flask(__name__)

@app.route("/checksum", methods=['GET'])
def checksum():	
	
	#Get the "url" input parameter and sanitize it, removing ability to use XSS
	requestParamURL = bleach.clean(request.args.get('url'), strip=True)

	# Set the checksum to expire 60 seconds from now.
	expireTime = str(int(time.time()) + 60)

	# Make the expireTime part of the hmac signed data so we can enforce the expiration of the signature
	hmacData = requestParamURL+"-"+expireTime
	checksum = hmac.new(secretKey, hmacData, hashlib.sha256).hexdigest()+"-"+expireTime

	# This is a convenience so you can quickly paste in the parameters when running the "checkchecksum" operation.
	verifyChecksumParams = "url="+urllib.quote_plus(requestParamURL)+"&checksum="+checksum

	# JSON encode the data
	responseData = json.dumps({"url": requestParamURL, "checksum": checksum, "verify_checksum_url":verifyChecksumParams}, sort_keys=True)
	
	return Response(responseData, status=200, mimetype='application/json')

@app.route("/checkchecksum", methods=['GET'])
def checkchecksum():
	#Get the "url" input parameter and sanitize it, removing ability to use XSS
	requestParamURL = bleach.clean(request.args.get('url'), strip=True)
	
	#Get the "checksum" input parameter
	requestChecksum	= request.args.get('checksum')
	
	# Verify that the checksum parameter is specified.
	try:
		requestChecksumPieces = requestChecksum.split("-", 1)
	except AttributeError:
		return Response(json.dumps({"msg":"Missing checksum"}), 400, mimetype='application/json')

	# Verify that the checksum consists of <checksum>-<expirationTime>
	try:
		requestChecksumTime	= requestChecksumPieces[1]
	except IndexError:
		return Response(json.dumps({"msg":"Invalid checksum"}), 400, mimetype='application/json')

	# Verify that the expirationTime is an integer
	try:
		int(requestChecksumTime)
	except ValueError:
		return Response(json.dumps({"msg":"Invalid format for checksum time suffix (must be an integer)"}), 400, mimetype='application/json')

	requestChecksum			= requestChecksumPieces[0]
	currentTime				= int(time.time())
	
	# Rebuild the checksum based off the input parameters
	hmacData = requestParamURL+"-"+requestChecksumTime
	checksum = hmac.new(secretKey, hmacData, hashlib.sha256).hexdigest()

	# Verify that the checksum matches AND that the current time has not exceeded the request expiration time
	if currentTime <= int(requestChecksumTime) and requestChecksum == checksum:
		verified	= True
		status		= 200
	else:
		verified    = False
		status		= 400

	responseData = json.dumps({"verified":verified});
	
	return Response(responseData, status, mimetype='application/json')

if __name__ == "__main__":
    app.run()

