#!/usr/bin/env python

import base64, ctparser, ctprivate, hashlib, json, random, socket, ssl, time, sys


blksize = hashlib.sha1().block_size

trans_5c = "".join(chr(x ^ 0x5c) for x in xrange(256))
trans_36 = "".join(chr(x ^ 0x36) for x in xrange(256))

rest_host = "api.twitter.com"
url_get_mentions = "/1.1/statuses/mentions_timeline.json"
url_post_update = "/1.1/statuses/update.json"

stream_host = "userstream.twitter.com"
url_stream_user = "/1.1/user.json"


def hmac_sha1(key, msg):
	if len(key) > blksize:
		key = hashlib.sha1(key).digest()
	key += chr(0) * (blksize - len(key))
	opad = key.translate(trans_5c)
	ipad = key.translate(trans_36)
	return hashlib.sha1(opad + hashlib.sha1(ipad + msg).digest())


def percent_encode(src):
	dst = ""
	for c in src:
		if c.isalnum() or c in "-._~":
			dst += c
		else:
			dst += "%" + hex(ord(c))[2:].upper()
	return dst


def collect_params(params):
	tmp = { }
	for key in sorted(params):
		tmp[percent_encode(key)] = percent_encode(params[key])
	out = "&".join(key + "=" + tmp[key] for key in sorted(tmp))
	return out


def sig_base_string(method, url, pstr):
	return method.upper() + "&" + percent_encode(url) + "&" + percent_encode(pstr)


def signing_key():
	return percent_encode(ctprivate.consumer_secret) + "&" + percent_encode(ctprivate.access_secret)


def sign(method, url, params):
	key = signing_key()
	msg = sig_base_string(method, url, collect_params(params))
	res = hmac_sha1(key, msg).digest()
	return base64.b64encode(res)


def gen_nonce(n):
	return "".join(random.choice("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz") for i in xrange(0, n))


def open_oauth_stream(host, method, url, api_params):
	oauth_params = { }
	oauth_params["oauth_consumer_key"] = ctprivate.consumer_key
	oauth_params["oauth_nonce"] = gen_nonce(32)
	oauth_params["oauth_signature_method"] = "HMAC-SHA1"
	oauth_params["oauth_timestamp"] = str(int(time.time()))
	oauth_params["oauth_token"] = ctprivate.access_token
	oauth_params["oauth_version"] = "1.0"
	oauth_params["oauth_signature"] = sign(method, "https://" + host + url, dict(api_params.items() + oauth_params.items()))
	params = dict(api_params.items() + oauth_params.items())
	if len(api_params) != 0:
		full_url = url + "?" + "&".join(percent_encode(key) + "=" + percent_encode(api_params[key]) for key in api_params)
	else:
		full_url = url
	header = method + " " + full_url + " HTTP/1.1\r\n"
	header += "Accept: */*\r\n"
	header += "Connection: close\r\n"
	header += "User-Agent: TwitCalc/1.0\r\n"
	header += "Authorization: OAuth "
	header += ", ".join(percent_encode(key) + '="' + percent_encode(oauth_params[key]) + '"' for key in oauth_params) + "\r\n"
	header += "Host: " + host + "\r\n"
	header += "\r\n"

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	ssl_sock = ssl.wrap_socket(s, ca_certs = "/etc/ssl/certs/ca-certificates.crt", cert_reqs = ssl.CERT_REQUIRED)
	ssl_sock.connect((rest_host, 443))
	ssl_sock.write(header)

	return ssl_sock


def call_twitter_api(method, url, api_params):
	ssl_sock = open_oauth_stream(rest_host, method, url, api_params)
	
	data = ""
	while True:
		tmp = ssl_sock.read()
		if tmp == "":
			break
		data += tmp
	
	ssl_sock.close()

	# parse out response header
	return data[data.index("\r\n\r\n") + 4:]


def stream_twitter_api(method, url, api_params):
	ssl_sock = open_oauth_stream(stream_host, method, url, api_params)
	
	chunk_buf = ""
	got_hdr = False
	chunk_size = 0
	stream = ""
	while True:
		tmp = ssl_sock.read()
		chunk_buf += tmp
		if not got_hdr and "\r\n\r\n" in chunk_buf:
			got_hdr = True
			# just ignore the header (TODO: parse out response?)
			chunk_buf = chunk_buf[chunk_buf.find("\r\n\r\n") + 4:]
		# rebuild the stream from the chunks
		if chunk_size == 0:
			# grab chunk size
			n = chunk_buf.find("\r\n")
			if n < 0:
				continue
			# check for empty lines
			if n == 0:
				chunk_buf = chunk_buf[2:]
				continue
			chunk_size = int(chunk_buf[:n], 16)
			chunk_buf = chunk_buf[n + 2:]
		if chunk_size != 0 and len(chunk_buf) >= chunk_size:
			chunk = chunk_buf[:chunk_size]
			chunk_buf = chunk_buf[chunk_size:]
			chunk_size = 0
			stream += chunk
			while True:
				n = stream.find("\r\n")
				if n < 0:
					break
				ln = stream[:n]
				stream = stream[n + 2:]
				if ln != "":
					yield json.loads(ln)


def process_tweet(tweet):
	try:
		text = tweet[u"text"]
		if len(text) <= 8 or text[:8] != "@calctw ":
			return
		text = text[8:]

		# TODO: process text
		print text
	except:
		# catch any and all errors and ignore them (don't post reply)
		print "Invalid tweet: " + tweet
		return


#for tweet in stream_twitter_api("GET", url_stream_user, { "with" : "user", "replies" : "all" }):
#	process_tweet(tweet)

# test
tree = ctparser.parse("1/(2^2+3*4)")
print tree.value({ })
