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
ses = session()

if not url.startswith('http') or not url.startswith('https'):
	url = 'https://' + url

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
		print(colo('Hints : ' + ','.join(i for i in desc) , 'violet'))
	
	if files:
		files = [url+i for i in files]
		print(colo('Files included : ' + ', '.join(files) , 'white'))
		if args.d :
			if args.i not in os.listdir(args.d):
				os.makedirs(args.d+ '/' + args.i)

			if not args.d.endswith('/'):
				args.d = args.d + '/'

			current_dir = args.d + args.i + '/'
			
			overall = open(current_dir + 'totaldump', 'a+')
			overall.write('Name: ' + name + '\n' + 'Category: '+category + '\n' + 'Description: ' + desc + '\n' + 'Hints:' + ', '.join(h for h in hint) + '\n' +'Files: ' + ', '.join(f for f in files) + '\n--------------------------------------------\n')
			overall.close()

			path = current_dir + args.d + '/' if not args.d.startswith('/') else args.d+args.i+'/'

			if category not in os.listdir(path):
				path +=  category
				os.makedirs(path)
			else:
				path += category

			if name not in os.listdir(path):
				path += '/' + name
				os.makedirs(path)
			else:
				path += '/' + name

			for c in range(len(files)):
				f = open(path+'/'+name+str(c), 'wb')
				r = ses.get(files[c]).text
				f.write(bytes(r, encoding='utf8'))
				f.close
				rme = open(path+'/'+'README', 'wb')
				rme.write(bytes(desc, encoding='utf8'))
				rme.close()

	print (colo('\n-----------------------------------------------------------------\n', 'white'))
