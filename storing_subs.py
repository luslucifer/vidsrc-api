import requests
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool 

url = 'http://127.0.0.1:8000/vidsrc/'
vidsrc_url = 'https://vidsrc.to/vapi/movie/new/'
with open('mvids.txt', 'r') as file:
    id_arr = file.read().splitlines()

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

    def download_subs(self, lang, file_url, id,id2):
        try:
            get = requests.get(file_url).content
            with open(f'subs/{lang}_{id}_{id2}.vtt', 'wb') as file:
                file.write(get)

        except Exception as err:
            print(err)

    def main(self, id: str ,id2:str):
        res = requests.get(url + id).json()
        arr = self.geting_subs_arr(res)
        with ThreadPoolExecutor(max_workers=len(arr)+1) as executor:  # Adjust max_workers as needed
            for obj in arr:
                lang = obj['lang']
                file_url = obj['file']
                executor.submit(self.download_subs, lang, file_url, id,id2)


if __name__ == '__main__':
    s = Subs()
    tmdb , imdb = s.id_list()
    # s.main(id=str(123))
    tuple_list = []
    for x in range(0,len(tmdb)):
        t = (tmdb[x],imdb[x])
        tuple_list.append(t)

    with Pool(10) as p :
        p.starmap(s.main,tuple_list)

