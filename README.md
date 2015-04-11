# hmacSign

DESCRIPTION:

Sign an API request using HMAC and an expiration time.

Includes: 

  1) XSS protection 

  2) Basic error reporting when the checkchecksum API route is requested and the "checksum" input parameter is missing or an 
     invalid format. 


DEPLOYMENT:

1) Requirement: make sure that your environment has python 2.7.9 installed

   a) If you have a different version of python installed and don't want to disrupt what is natively installed on your 
      server:

      i)   install virtualenvwrapper (pip install virtualenvwrapper)
      
      ii)  follow directions at this URL: http://simononsoftware.com/virtualenv-tutorial-part-2/
      
      iii) To change to version 2.7.9, refer to the URL above, and go to the "Using Different Python Versions"
           NOTE: you will have to figure out how to install Python 2.7.* on your *nix server if it is not already installed  

2) Choose a directory where you want to clone this repo.

3) git clone https://github.com/jamesfgreene/hmacSign.git

4) pip install -r requirements.txt 

5) Start the service:
     
   python hmacSigning.py

USAGE:

Example: 

1) First, generate the checksum, given the url:

Request:

  curl -i -XGET "http://localhost:5000/checksum?url=http://www.foo.com%3Ffoo%3Dx%26bar%3Dy%3Cscript%3D"                                                                   

Response:
  HTTP/1.0 200 OK
  Content-Type: application/json
  Content-Length: 346
  Server: Werkzeug/0.10.4 Python/2.7.9
  Date: Sat, 11 Apr 2015 03:40:56 GMT

  {
	"checksum": "d37359dfa798c68b894bbf4f4309bc1f71d03f2d026ebfd3a91d5c603013aaf8-1428723716",
	"url": "http://www.foo.com?foo=x&bar=y", 
	"verify_checksum": "curl -i -XGET 'http://localhost:5000/checkchecksum?url=http%3A%2F%2Fwww.foo.com%3Ffoo%3Dx%26amp%3Bbar%3Dy&checksum=d37359dfa798c68b894bbf4f4309bc1f71d03f2d026ebfd3a91d5c603013aaf8-1428723716'"
  }

2) Verify the checksum by executing the "checkchecksum" endpoint with the url and checksum

NOTE: you will need to properly urlencode the "url" input parameter.

Or you can simply copy and paste the "verify_checksum" JSON attribute from the response above and whack enter):

Request: 

  curl -i -XGET 'http://localhost:5000/checkchecksum?url=http%3A%2F%2Fwww.foo.com%3Ffoo%3Dx%26amp%3Bbar%3Dy&checksum=d37359dfa798c68b894bbf4f4309bc1f71d03f2d026ebfd3a91d5c603013aaf8-1428723716'

Response: 

  HTTP/1.0 200 OK
  Content-Type: application/json
  Content-Length: 18
  Server: Werkzeug/0.10.4 Python/2.7.9
  Date: Sat, 11 Apr 2015 03:41:27 GMT

  {"verified": true}



3) If time has expired (60 seconds has passed since the checksum was created for the URL) or the checksum and/or URL are modified:

Request: 

  curl -i -XGET 'http://localhost:5000/checkchecksum?url=http%3A%2F%2Fwww.foo.com%3Ffoo%3Dx%26amp%3Bbar%3Dy&checksum=d37359dfa798c68b894bbf4f4309bc1f71d03f2d026ebfd3a91d5c603013aaf8-1428723716'

Response:

  HTTP/1.0 400 BAD REQUEST
  Content-Type: application/json
  Content-Length: 19
  Server: Werkzeug/0.10.4 Python/2.7.9
  Date: Sat, 11 Apr 2015 03:46:11 GMT

  {"verified": false}
