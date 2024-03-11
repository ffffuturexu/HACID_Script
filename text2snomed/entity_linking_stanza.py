from utils import *


def do_nlp(input_file, output_file):
    # stanza.download('en', package='mimic', processors={'ner': 'i2b2'})    
    bionlp = stanza.Pipeline('en', package='mimic', processors={'ner': 'i2b2'}) 
    with open(input_file, 'r') as f_input:
        sentences = f_input.readlines()

    output_results = []

    for sentence in tqdm(sentences):
        sentence_result = {}
        sentence_result['sentence'] = sentence
        doc = bionlp(sentence)

        sentence_result['entities'] = []
        for ent in doc.entities:
            entity = {}
            entity['text'] = ent.text
            entity['type'] = ent.type
            # print(f'{ent.text}\t{ent.type}')
            sentence_result['entities'].append(entity)
        
        output_results.append(sentence_result)

    # print('bionlp done with the length of ', len(output_results))
    with open(output_file, 'w') as f_output:
        json.dump(output_results, f_output, indent=4)


def add_snomed(input_file, output_file):
    with open(input_file, 'r') as f_input:
        json_data = json.load(f_input)
    
    for sentence in tqdm(json_data):
        # print(sentence['sentence'])
        entity_list = []
        for entity in sentence['entities']:
            entity_list.append(entity['text'])

        # print(entity_list)
        snomed_results = get_snomed_codes(entity_list)
        # print('snomed_results: ', snomed_results)

        for entity in sentence['entities']:
            cui = entity['text']
            if cui in snomed_results:
                entity['snomed_name'] = snomed_results[cui]['name']
                entity['snomed_ui'] = snomed_results[cui]['ui']
                entity['snomed_api_uri'] = snomed_results[cui]['api_uri']
                entity['snomed_browser_uri'] = snomed_results[cui]['browser_uri']

    with open(output_file, 'w') as f_output:
        json.dump(json_data[:2], f_output, indent=4)
        logging.warning('Done with the length of ' + str(len(json_data)))


if __name__ == '__main__':
    # do_nlp('linking_data/stanza/ade_example.txt', 'linking_data/stanza/stanza_ade_example.json') # if the ner is done, comment this line
    add_snomed(input_file='linking_data/stanza/stanza_ade_example.json', 
               output_file='linking_data/stanza/stanza_ade_full_snomed.json')