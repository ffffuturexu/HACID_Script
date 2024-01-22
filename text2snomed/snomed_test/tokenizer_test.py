import stanza

nlp = stanza.Pipeline('en')
phrases = ["Additive pulmonary toxicity", 
            "constellation of dermatitis",
            "acute renal failure",
            "central nervous toxicity",
            "human teratogen",
            "doubling of the lamotrigine blood level",
            "sero - negative rheumatoid arthritis"]

def chunker(input_phrase, root_id, root_text=None):
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

    return chunked_phrase.strip()

for phrase in phrases:
    doc = nlp(phrase)
    doc.sentences[0].print_dependencies()
    for dep in doc.sentences[0].dependencies:
        if dep[1] == 'root':
            chunked_phrase = chunker(phrase.split(), dep[2].id)
            print('chunked_phrase: ', chunked_phrase)
            break
        
    print('=' * 50)

