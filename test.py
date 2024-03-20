import requests
import time
vidsrc_url ='https://vidsrc.to/vapi/movie/new/'
def vidsrc_ids ():
        page = 1
        while True :
            items = requests.get(vidsrc_url + str(page)).json()['result']['items']
            page = page+1
            if len(items)!= 0 :
                for obj in items:
                    print(obj['tmdb_id'])
                    # with open('vids.txt','a') as file :
                    #     file.write(obj['tmdb_id']+'_'+obj['imdb_id']+'\n')

            else:
                break

vidsrc_ids()