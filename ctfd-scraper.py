from requests import session, get, post
import json
import os
import re
from functools import partial
from workerpool import WorkerPool
from colored import fg, attr
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-i', help="CTF's url (CTFd framework)", required=True)
parser.add_argument('-u', help="Specify the registered username", required=True)
parser.add_argument('-p', help="Specify the password", required=True)
parser.add_argument('-d', help="Use this flag if you want to download the included files to your local machine.")
parser.add_argument('-t', help="If there are lots of challenges you can use threads to speed up the process", default=10, type=int)
args = parser.parse_args()

if args is None:
	print (parser.print_help())

def colo(txt, color):
	return (fg(color) + attr('bold') + txt + '\n')

url = args.i
title = url.strip('http://') if url.startswith('http') else url.strip('https://')
ses = session()

if not url.startswith('http') or not url.startswith('https'):
	url = 'https://' + url

try:
	res = ses.get(url).text
	nonce = re.findall("'csrfNonce': \"(.*)\",", res)
except:
	url = 'http://' + url.strip('https://')
	res = ses.get(url).text
	nonce = re.findall("'csrfNonce': \"(.*)\",", res)

login = {
	'name': args.u,
	'password': args.p,
	'nonce' : nonce
}

ses.post(url+'/login', data=login)
id_api = "/api/v1/challenges"

def get_id(api=id_api):
	res = ses.get(url+api).text
	return json.loads(res)

id_list = [str(i['id']) for i in get_id()['data']]
print ('There are {} total challenges!'.format(len(id_list)))

info = {}
def get_info(id, api):
	res = ses.get(url+ api + id).text
	jas = json.loads(res)
	jas = jas['data']
	hint = jas['hints']
	name = jas['name']
	desc = jas['description']
	category = jas['category']
	files = jas['files']
	info[name] = {'chall_id': str(id), 'category': category, 'description': desc, 'hints': hint , 'files': files }

pool = WorkerPool(args.t)
pool.map(partial(get_info, api=id_api+'/'), id_list)
pool.shutdown()
pool.wait()

for i in info:
	o = info[i]
	name = i
	category = o['category']
	desc = o['description']
	hint = o['hints']
	files = o['files']

	print(colo('Challenge Name : ' + name , 'red'))
	print(colo('Challenge Category : ' + category, 'yellow'))

	if desc:
		print(colo('Challenge description : ' + desc , 'green'))
	
	if hint:
		print(colo('Hints : ' + ",".join([h['content'] for h in hint]) , 'violet'))
	
	if files:
		files = [url+i for i in files]
		print(colo('Files included : ' + ', '.join(files) , 'white'))
		
		if args.d :
			# print ("argsssss: "+ args.d) # debug
			
			if not os.path.isdir(args.d):
				os.mkdir(args.d)

			current_dir = args.d	
			path = current_dir

			overall = open(path + "/" + 'totaldump', 'a+')
			overall.write('Name: ' + name + '\n' + 'Category: '+category + '\n' + 'Description: ' + desc + '\n' + 'Hints:' + ",".join([h['content'] for h in hint]) + '\n' +'Files: ' + ', '.join(f for f in files) + '\n--------------------------------------------\n')
			overall.close()

			chall_dir = path + "/" + category + "/" + name + "/"
			os.makedirs(chall_dir)

			for c in files:
				print (c)
				chall_namee= re.findall("(/.*?){6}(.*?)\?token", c)[0][1]
				print (chall_namee)
				f = open(chall_dir + chall_namee, 'wb')
				r = ses.get(c).content
				f.write(r)
				f.close
				rme = open(chall_dir+'/'+'README', 'wb')
				rme.write(bytes(desc + "\nHint: "+",".join([h['content'] for h in hint]) , encoding='utf8'))
				rme.close()

	print (colo('\n-----------------------------------------------------------------\n', 'white'))
