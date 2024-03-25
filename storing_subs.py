import requests
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool 
from tqdm import tqdm
import os
import threading

# Assuming 'dwn.txt' doesn't exist initially, create an empty file
tuple_saved = 'dwn.txt'
idsFile = 'vids.txt'
open(tuple_saved, 'a').close()
open(idsFile,'w').close()

url = 'https://vidsrc-to-eight.vercel.app/vidsrc/'
# url = 'https://vidsrc-api-1.onrender.com/vidsrc/'
vidsrc_url = 'https://vidsrc.to/vapi/episode/latest/'

lock = threading.Lock()  # Create a lock instance

class Subs:
    def geting_subs_arr(self, obj: dict):
        subs = obj[0]['data']['sub']
        return subs

    def vidsrc_ids(self):
        
        try:
            page = 0
            with open(idsFile , 'r') as file :
                splited_no = len(file.read().splitlines())
            if not splited_no >=15 :
                page = round(splited_no/15)
            
            while True:
                page = page + 1
                try :
                    items = requests.get(vidsrc_url + str(page)).json()['result']['items']
                    if len(items) != 0:
                        for obj in items:
                            print(obj)
                            try:
                                with lock:  # Acquire lock before writing to file
                                    with open(idsFile, 'a') as file:
                                        file.write(obj['tmdb_id'] + '_' + obj['imdb_id']+ '_'+str(obj['season'])+ '_'+str(obj['number']) + '\n')
                            except Exception as err:
                                print(err)
                    else:
                        break
                except Exception as err : 
                    print(f'err in vidsrc while loop : {err}')
        except Exception as err : 
            print (f'err at vidsrc_src: {err}')

    def id_list(self):
        with open(idsFile, 'r') as file:
            data = file.read()
        # if len(data)==0 :
        #     self.vidsrc_ids()

        lines = data.split('\n')

        tuple_list = []
        with open(idsFile, 'r') as file:
            data = file.read()
            lines = data.split('\n')

            # Extract TMDB IDs from each line
            for line in lines:
                try:
                    tmdb_id = line.split('_')[0]
                    imdb_id = line.split('_')[1]
                    ss = line.split('_')[2]
                    ep = line.split('_')[3]
                    tuple = (tmdb_id,ss,ep,imdb_id)
                    tuple_list.append(tuple)

                except IndexError:
                    print(f"Error parsing line: {line}. Skipping...")

        return tuple_list

    def download_subs(self, lang, file_url, id, id2,ss,ep):
        try:
            get = requests.get(file_url).content
            with open(f'subs/{lang}_{id}_{id2}_{ss}_{ep}.vtt', 'wb') as file:
                file.write(get)

        except Exception as err:
            print(err)

    def main(self, id : str =None, ss:str = '1' , ep:str = '1',id2:str = None ):
        try:
            with open(tuple_saved , 'a') as file :
                file.write(str((id,ss,ep,id2))+'\n')

            params = {'s':ss,'e':ep}
            res = requests.get(url + id ,params=params).json()
            arr = self.geting_subs_arr(res)
            
            with ThreadPoolExecutor(max_workers=len(arr) + 1) as executor:
                progress_bar = tqdm(total=len(arr), desc=f"Processing {id}_{id2}", position=0)
                
                def update_progress(_):
                    progress_bar.update(1)
                    
                for obj in arr:
                    lang:str = obj['lang']
                    lang = lang.replace('/','-')
                    file_url = obj['file']
                    executor.submit(self.download_subs, lang, file_url, id, id2,ss,ep).add_done_callback(update_progress)
        except Exception as err: 
            print (f' err in main : {err}')

    def file_check(self):
        subs = 'subs'
        if not os.path.exists(subs):
            os.mkdir(subs)
        
        if not os.path.exists(idsFile):
            print('fuck')
            self.vidsrc_ids()
        

if __name__ == '__main__':
    s = Subs()
    s.file_check()
    tuple_list = s.id_list()
    with open(tuple_saved,'r') as file : 
        splited = file.read().splitlines()
    tuple_list = list(set(tuple_list) - set(splited))
    for i in tuple_list:
        print(i)

    with Pool(10) as p:
        for _ in tqdm(p.starmap(s.main, tuple_list), total=len(tuple_list), desc="Overall Progress"):
            pass
