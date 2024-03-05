import asyncio
import aiohttp
import aiofile
import hashlib
import pathlib
from datetime import datetime
import io
import os

class HashStore:
	def __init__(self, filepath):
		self.hash_store = set()
		self.filepath = filepath
		
		try:
			with open(filepath, 'r') as file:
				for line in file:
					self.hash_store.update((line,))
		except FileNotFoundError:
			with open(filepath, 'w+') as file:
				...

	def update(self, digest):
		self.hash_store.update((digest,))
		with open(self.filepath, 'a+') as file:
			file.write(f'\n{digest}')

	def __contains__(self, item):
		return item in self.hash_store


class Archival:

	def __init__(self, *, url, save_dir, interval, prefix, suffix = '', hash_store_path):
		self.url 		= url
		self.dir 		= pathlib.Path(save_dir)
		self.interval 	= interval
		self.prefix     = prefix
		self.suffix     = suffix
		self.hash_store	= HashStore(hash_store_path)

	async def poll_site(self):
		while True:
			try:
				sha2 = hashlib.sha256()
				async with aiohttp.ClientSession() as session:
					async with session.get(url = self.url) as response:
						temp = io.BytesIO()
						async for _ in response.content:
							sha2.update(_)
							temp.write(_)
						digest = sha2.hexdigest()
						print(digest in self.hash_store)
						if digest not in self.hash_store:
							with open(f"{self.prefix}_{datetime.utcnow().strftime('%d-%b-%Y %H%MUTC')}{self.suffix}", 'wb') as file:
								file.write(temp.getvalue())
							self.hash_store.update(digest)
			except aiohttp.client_exceptions.ClientConnectorError as e:
				await asyncio.sleep(900)

			await asyncio.sleep(self.interval)



x = Archival(url = 'https://mausam.imd.gov.in/Radar/caz_agt.gif', save_dir = '.', interval = 30, prefix = 'agartala radar',
			suffix = '.gif',
			hash_store_path = 'hashstore.txt')
# print(x.poll_site())
asyncio.run(x.poll_site())