from sympy.ntheory import factorint
from Crypto.Util.number import long_to_bytes
import libnum
import sys
from pwn import *
import gmpy2

context.log_level='DEBUG'

def fermat_factor(n):
    assert n % 2 != 0

    a = gmpy2.isqrt(n)
    b2 = gmpy2.square(a) - n

    while not gmpy2.is_square(b2):
        a += 1
        b2 = gmpy2.square(a) - n

    p = a + gmpy2.isqrt(b2)
    q = a - gmpy2.isqrt(b2)

    return int(p), int(q)


r = remote('167.172.9.174', 4243)
r.sendline()
r.recvuntil('>>>')
r.sendline('bmh5')
r.recvuntil('>>>')
r.sendline('YiBl')
r.recvuntil('>>>')
r.sendline('cTog')
r.recvuntil('>>>')
r.sendline('WFlR')
r.recvuntil('>>>')
r.sendline('U0tK')
r.recvuntil('>>>')
r.sendline('e0wz')
r.recvuntil('>>>')
r.sendline('cDRf')
r.recvuntil('>>>')
r.sendline('RzNy')
r.recvuntil('>>>')
r.sendline('UjRo')
r.recvuntil('>>>')
r.sendline('M19T')
r.recvuntil('>>>')
r.sendline('ZFRJ')
r.recvuntil('>>>')
r.sendline('aTRf')
r.recvuntil('>>>')
r.sendline('NHJk')
r.recvuntil('>>>')
r.sendline('MVBU')
r.recvuntil('>>>')
r.sendline('ckQx')
r.recvuntil('>>>')
r.sendline('SGg0')
r.recvuntil('>>>')
r.sendline('P30=')

for i in range(100):

	re = r.recvuntil('>>>').split(b'\n')
	print (re)
	n = int(re[2].split(b'=')[1])
	c = int(re[3].split(b'=')[1])


	print (n,c)

	(p,q) = fermat_factor(n)

	print (p, q)

	PHI=(p-1)*(q-1)

	e = 65537
	d=(gmpy2.invert(e, PHI))
	# d=(libnum.invmod(e, PHI))
	res=pow(c,d, n)
	res = p64(res).replace(b'\x00', b'')[::-1].strip()
	print (res)

	r.sendline (res)

