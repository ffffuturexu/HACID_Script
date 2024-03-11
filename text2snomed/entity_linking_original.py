from utils import *


def gather_entity_from_ade_original(input_file, output_file):
    with open(input_file, 'r') as f_input:
        json_data = json.load(f_input)

    output_results = []
    for sample in tqdm(json_data):
        sample_result = {}
        sentence = ' '.join(sample['tokens'])
        # print(sentence)
        sample_result['sentence'] = sentence

        sample_result['entities'] = []
        entity_list = []
        for entity in sample['entities']:
            entity_text = ' '.join(sample['tokens'][entity['start']:entity['end']])
            entity_list.append(entity_text)
            sample_result['entities'].append({
                'text': entity_text,
                'type': entity['type']
            })
        # print(str(entity_list) + '\n' + '=' * 50)

        snomed_results = get_snomed_codes(entity_list)
        # print('snomed_results: ', snomed_results)

        for entity in sample_result['entities']:
            cui = entity['text']
            if cui in snomed_results:
                entity['snomed_name'] = snomed_results[cui]['name']
                entity['snomed_ui'] = snomed_results[cui]['ui']
                entity['snomed_api_uri'] = snomed_results[cui]['api_uri']
                entity['snomed_browser_uri'] = snomed_results[cui]['browser_uri']

        output_results.append(sample_result)
        # print('=' * 50)

    with open(output_file, 'w') as f_output:
        json.dump(output_results, f_output, indent=4)
        logging.info('Done with the length of ' + str(len(output_results)))


if __name__ == '__main__':
    gather_entity_from_ade_original(input_file='linking_data/original/ade_full.json', 
                                    output_file='linking_data/original/original_ade_full_snomed.json')