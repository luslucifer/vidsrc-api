import requests
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool 
from tqdm import tqdm
import os

# Assuming 'dwn.txt' doesn't exist initially, create an empty file
tuple_saved = 'dwn.txt'
open(tuple_saved, 'a').close()


# url = 'http://0.0.0.0:8090/vidsrc/'
url = 'https://vidsrc-api-1.onrender.com/vidsrc/'
vidsrc_url = 'https://vidsrc.to/vapi/movie/new/'
idsFile = 'vids.txt'

class Subs:
    def geting_subs_arr(self, obj: dict):
        subs = obj[0]['data']['sub']
        return subs

    def vidsrc_ids(self):
        page = 1
        while True:
            items = requests.get(vidsrc_url + str(page)).json()['result']['items']
            page = page + 1
            if len(items) != 0:
                for obj in items:
                    print(obj)
                    try:
                        with open(idsFile, 'a') as file:
                            file.write(obj['tmdb_id'] + '_' + obj['imdb_id'] + '\n')
                    except Exception as err:
                        print(err)
            else:
                break

    def id_list(self):
        with open(idsFile, 'r') as file:
            data = file.read()

        lines = data.split('\n')

        tmdb_ids = []
        imdb_ids = []
        with open(idsFile, 'r') as file:
            data = file.read()
            lines = data.split('\n')

            # Extract TMDB IDs from each line
            for line in lines:
                try:
                    tmdb_id = line.split('_')[0]
                    imdb_id = line.split('_')[1]

                    imdb_ids.append(imdb_id)
                    tmdb_ids.append(tmdb_id)
                except IndexError:
                    print(f"Error parsing line: {line}. Skipping...")

        return tmdb_ids, imdb_ids

    def download_subs(self, lang, file_url, id, id2):
        try:
            get = requests.get(file_url).content
            with open(f'subs/{lang}_{id}_{id2}.vtt', 'wb') as file:
                file.write(get)

        except Exception as err:
            print(err)

    def main(self, id: str, id2: str):
        with open(tuple_saved , 'a') as file :
            file.write(str((id,id2))+'\n')

        res = requests.get(url + id).json()
        arr = self.geting_subs_arr(res)
        
        with ThreadPoolExecutor(max_workers=len(arr) + 1) as executor:
            progress_bar = tqdm(total=len(arr), desc=f"Processing {id}_{id2}", position=0)
            
            def update_progress(_):
                progress_bar.update(1)
                
            for obj in arr:
                lang:str = obj['lang']
                lang = lang.replace('/','-')
                file_url = obj['file']
                executor.submit(self.download_subs, lang, file_url, id, id2).add_done_callback(update_progress)

if __name__ == '__main__':
    s = Subs()
    tmdb, imdb = s.id_list()
    tuple_list = [(tmdb[x], imdb[x]) for x in range(0, len(tmdb))]
    with open(tuple_saved,'r') as file : 
        splited = file.read().splitlines()
    tuple_list = list(set(tuple_list) - set(splited))

    with Pool(10) as p:
        for _ in tqdm(p.starmap(s.main, tuple_list), total=len(tuple_list), desc="Overall Progress"):
            pass
