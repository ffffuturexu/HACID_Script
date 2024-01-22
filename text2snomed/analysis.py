import json
from collections import Counter

def count_retry(input_file):
    with open(input_file, 'r') as f:
        lines = f.readlines()

        retry = []
        tried = []
        count_list = []
        count = 0
        retry_entities = []

        for line in lines[:]:
            line = line.strip()
            if "WARNING" in line:
                # print(line)
                current_retry = line.split(', Retry')[-1].strip()
                current_tried = line.split(', Retry')[0].split('No results for')[-1].strip()
      
                if len(retry) == 0 or len(tried) == 0:
                    retry.append(current_retry)
                    tried.append(current_tried)
                    count += 1

                else:
                    if current_tried == retry[-1]:
                        # print('current_tried: ', current_tried)
                        # print('retry: ', retry)
                        retry.append(current_retry)
                        tried.append(current_tried)
                        count += 1

                    else:
                        retry.append(current_retry)
                        tried.append(current_tried)
                        count_list.append(count)
                        retry_entities.append(tried[-count-1])
                        count = 1

    return count_list, retry_entities   

def not_identified(input_file):
    with open(input_file, 'r') as f:
        data = json.load(f)

        entity_list = []

        not_identified = 0

        for sample in data:
            for entity in sample['entities']:
                entity_list.append(entity['text'])
                if 'snomed_name' not in entity:
                    not_identified += 1

        print('total: ', len(entity_list))
        print('not_identified: ', not_identified)
        print('not_identified percentage: ', round(not_identified / len(entity_list), 3))
        print('identified: ', len(entity_list) - not_identified)
        print('identified percentage: ', round(1 - (not_identified / len(entity_list)), 3))

    return entity_list


def write_retry_entities(retry_entities, output_file):
    with open(output_file, 'w') as f:
        for entity in retry_entities:
            f.write(entity + '\n')

if __name__ == '__main__':

    print('input: original')
    input_file = 'data/original/original_ade_full_snomed.json'
    entity_list = not_identified(input_file)
    
    input_file = 'data/original/original_ade_full.log'
    count_list, retry_entities = count_retry(input_file)
    print('retry count: ', len(count_list))
    print('retry percentage: ', round(len(count_list) / len(entity_list), 3))
    # write_retry_entities(retry_entities, 'data/original/retry_entities.txt')
    for e in sorted(Counter(count_list)):
        print('retry {} times: {} entities, percentage: {}'.format(e, Counter(count_list)[e], round(Counter(count_list)[e] / len(entity_list), 3)))

    print('=' * 50)
            
    print('input: bioner')
    input_file = 'data/bioner/bioner_ade_full_snomed.json'
    not_identified(input_file)

    input_file = 'data/bioner/bioner_ade_full.log'
    count_list, retry_entities = count_retry(input_file)
    print('retry count: ', len(count_list))
    print('retry percentage: ', round(len(count_list) / len(entity_list), 3))
    for e in sorted(Counter(count_list)):
        print('retry {} times: {} entities, percentage: {}'.format(e, Counter(count_list)[e], round(Counter(count_list)[e] / len(entity_list), 3)))
    # write_retry_entities(retry_entities, 'data/bioner/retry_entities.txt')
    


