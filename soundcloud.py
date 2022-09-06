from requests import get
from bs4 import BeautifulSoup as soup

def clean(string, garbage):
	for i in garbage:
		string = string.replace(i,'')
	return string

def get_client_id():
	script_url = soup( get('https://soundcloud.com/').text, 'html.parser'  ).findAll('script')[-1]['src'] # The 2nd from the last script src
	script = get(script_url).text
	# Get Client Id From script
	client_id = script.split(',client_id:')[1].split('"')[1]
	return client_id

def get_song_info(share_link):
	res = get(share_link)
	res_soup = soup(res.content, 'html.parser')

	song_name = ' '.join(res_soup.find('title').text.split(' ')[1:]).replace('Listen online for free on SoundCloud', '')
	song_id = res_soup.find('meta',{'property':'twitter:app:url:iphone'})['content'].split(':')[-1]

	return {'name': song_name, 'id':song_id}

def download_parts_and_assemble_parts(file_name, parts):
	# Cleaning File Name
	file_name = clean(file_name, ['|','/','\\','*','>','<',':'])
	file_name = file_name.strip()

	file = open(file_name+'.mp3', 'ab')
	for part in parts:
		part_content = get(str(part), headers={}).content
		file.write(part_content)
	file.close()


class Soundcloud:
	def __init__(self):
		self.client_id = get_client_id()
		self.headers = {'Accept-Language': 'en-GB,en;q=0.9,en-US;q=0.8', 'Cache-Control': 'max-age=0', 'Connection': 'keep-alive', 'Host': 'api-v2.soundcloud.com', 'sec-ch-ua': '"Microsoft Edge";v="105", " Not;A Brand";v="99", "Chromium";v="105"', 'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Windows"', 'Sec-Fetch-Dest': 'document', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Site': 'none', 'Sec-Fetch-User': '?1', 'Upgrade-Insecure-Requests': '1', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.27'}

	def get_song_parts(self, track_id):
		# Getting Song Json
		url = f"https://api-v2.soundcloud.com/tracks?ids={track_id}&client_id={self.client_id}"
		res = get(url, headers=self.headers).json()

		stream_url = res[0]['media']['transcodings'][0]['url']
		stream_url+= '?client_id=' + self.client_id

		m3u8_url = get(stream_url, headers=self.headers).json()['url']
		m3u8_file = get(m3u8_url).content.decode('utf-8')

		parts = [ part for part in m3u8_file.splitlines() if '#' not in part ]

		return parts


def main():
	sc = Soundcloud()
	
	url = input('URL: ')
	song_info = get_song_info(url)
	parts = Soundcloud().get_song_parts(song_info['id'])

	print(f'Downloading \nName: {song_info["name"]}\nId: {song_info["id"]}')
	download_parts_and_assemble_parts(song_info['name'], parts)
	print('Downloaded')

main()
input('Press Enter To Exit')
