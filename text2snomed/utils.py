import json
import requests
import logging
from tqdm import tqdm
import stanza

logging_path = 'linking_data/original/original_ade_full.log'

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', 
                    level=logging.WARNING,
                    filename=logging_path,
                    filemode='w')

nlp = stanza.Pipeline('en')
base_uri = 'https://uts-ws.nlm.nih.gov'
browser_query_uri = 'https://browser.ihtsdotools.org/?perspective=full&conceptId1={}&edition={}&release=&languages=en'
version = 'current'
sabs = 'SNOMEDCT_US'
apikey = '85f3d10c-8df0-4146-8a4c-e9f6a988f988'
edition = 'MAIN/2024-01-01'
limit = 1 # number of results to return per page, the most exact match is the first one
early_stop = 1 # number of pages to search
do_retry = True # if True, retry with chunked phrase if no results found

def chunker(input_phrase):
    doc = nlp(input_phrase)
    # doc.sentences[0].print_dependencies()
    for dep in doc.sentences[0].dependencies:
        chunked_phrase = ''
        if dep[1] == 'root':
            root_id = dep[2].id
            input_phrase = input_phrase.split()

            if root_id == len(input_phrase): # root is the last word
                chunked_phrase = ' '.join(input_phrase[1:])
            elif root_id == 1: # root is the first word
                if "of" in input_phrase:
                    of_id = input_phrase.index("of")
                    chunked_phrase = ' '.join(input_phrase[of_id+1:])
                else:
                    chunked_phrase = ''
            else:
                chunked_phrase = ''
            # print('chunked_phrase: ', chunked_phrase)
            break

    return chunked_phrase.strip()


def query_snomed(cui, page):
    path = '/search/'+version
    query = {'apiKey':apikey, 'string':cui, 'sabs':sabs, 'returnIdType':'code', 'pageNumber':page}

    while True:
        try:
            output = requests.get(base_uri+path, params=query)
            output.encoding = 'utf-8'
            #print(output.url)
            outputJson = output.json()
            break
        except:
            logging.warning('ERROR: ' + cui)
            continue
   
    results = (([outputJson['result']])[0])['results']
    # print('results found: ', len(results))

    return results


def further_get_snomed_codes(cui):
    logging.info('SEARCH CUI: ' + cui)
    snomed_result_single_cui = {}
    page = 0

    while True:
        page += 1
        results = query_snomed(cui, page)
        if len(results) == 0 or page > early_stop:
            if page == 1 and do_retry: # no results found
                # print('No results found for ' + cui)
                chunked_phrase = chunker(cui)
                if len(chunked_phrase) > 0:
                    # print('chunked_phrase: ', chunked_phrase)
                    logging.warning('No results for [{}], Retry [{}]'.format(cui, chunked_phrase))
                    snomed_result_single_cui = further_get_snomed_codes(chunked_phrase)
                break
            else: # got result, no need more pages
                break
                
        for item in results[:limit]:
            snomed_result_single_cui = {
                    'name': item['name'],
                    'ui': item['ui'],
                    'api_uri': item['uri'],
                    'browser_uri': browser_query_uri.format(item['ui'], edition)
                }
    
    return snomed_result_single_cui


def get_snomed_codes(cui_list):
    snomed_results = {}
    
    for cui in cui_list: # cui = query text for entity
        snomed_result_single_cui = further_get_snomed_codes(cui)
        if len(snomed_result_single_cui) > 0: # if snoemd_result_single_cui is not empty
            snomed_results[cui] = snomed_result_single_cui 
        # print('len of snomed_results: {}'.format(len(snomed_results)) + '\n' + '=' * 50)

    return snomed_results

