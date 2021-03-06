import json
from speak import sp_to_txt,txt_to_sp
import spacy
from spacy import displacy
from spacy.symbols import NOUN, NUM, ADJ
from nltk import Tree
import speech_recognition as sr
from spacy.matcher import Matcher

mic = sr.Microphone()
##Start Loading KB
with open('KB_rest_full.json', 'r') as f:
	rest_dict = json.load(f)

# for rest in rest_dict:
# 	print(rest['places'][0]['post code'])
cd = []
alc_cd = []
hd = []
alc_hd = []

for each in rest_dict['cold_drinks']:
	print(each['drink'],each['alc'])
	cd.append(each['drink'])
	alc_cd.append(each['alc'])

for each in rest_dict['hot_drinks']:
    print(each['drink'],each['alc'])
    hd.append(each['drink'])
    alc_hd.append(each['alc'])

print(cd)	
print(alc_cd)
##Done Loading KB

def concatanate_elements(list_drinks):
    list_sentence = list_drinks[0]
    for each in range(1,len(list_drinks)-1):
        list_sentence = list_sentence+', '+list_drinks[each]
    list_sentence = list_sentence+" and "+ list_drinks[len(list_drinks)-1]
    print(list_sentence)
    return list_sentence

def menu(hot,cold):
    
    hot_drinks_sentence = concatanate_elements(hot)
    cold_drinks_sentence = concatanate_elements(cold)

    welcome = "Ciao! Welcome to Sapienza bar! We have hot and cold drinks for you!"
    txt_to_sp(welcome,'en')

    hd_list= "We offer "+hot_drinks_sentence+" as a hot drink"
    txt_to_sp(hd_list,'en')

    cd_list = "And, as a cold drink we have "+cold_drinks_sentence
    txt_to_sp(cd_list,'en')

    order_asking = "What would you like to have?"
    txt_to_sp(order_asking,'en')

def get_double_noun(nlp_doc): #Eg Lemon Juice
    pattern = [{'POS': 'NOUN'}, {'POS': 'NOUN'}]
    matcher.add('FULL_NAME', None, pattern)
    matches = matcher(nlp_doc)
    for match_id, start, end in matches:
        span = nlp_doc[start:end]
        return span.text

def get_adj_noun(nlp_doc): #Eg Orange Juice
    pattern = [{'POS': 'ADJ'}, {'POS': 'NOUN'}]
    matcher.add('FULL_NAME', None, pattern)
    matches = matcher(nlp_doc)
    for match_id, start, end in matches:
        span = nlp_doc[start:end]
        return span.text

def tok_format(tok):
    return "_".join([tok.orth_, tok.tag_])


def to_nltk_tree(node):
    if node.n_lefts + node.n_rights > 0:
        return (Tree(tok_format(node),
                     [to_nltk_tree(child) for child in node.children]))
    else:
        return tok_format(node)

def match_in_menu(res,hot,cold):
    for each_hot_drink, each_cold_drink in zip(hot,cold):
        if res==each_hot_drink or res==each_cold_drink:
            return res

def collect_nouns(ord_doc):
    nouns = []
    for possible_subject in ord_doc:
        if possible_subject.pos == NOUN:
            nouns.append(possible_subject.text)
    return nouns

def is_cold_or_hot(list_of_nouns,list_of_drinks):
    for each_noun in list_of_nouns:
        for each_drink in list_of_drinks:
            if each_noun==each_drink:
                return True
    return False

def drink_explicitly(list_of_nouns,list_of_drinks):
    for each_noun in list_of_nouns:
        for each_drink in list_of_drinks:
            if each_noun==each_drink:
                return each_drink

def bot_ans(res,hotd,coldd,ord_doc):
    if res:
        your_order=match_in_menu(res,hotd,coldd)
        bot_answer = "Your" + your_order+" is coming right now"
    else:
        nouns = collect_nouns(ord_doc)
        for noun in nouns:
            print(noun)
        if is_cold_or_hot(nouns, coldd):
            drink = drink_explicitly(nouns, coldd)
            bot_answer="Your "+drink+" is coming right now!"
            print(bot_answer)
        elif is_cold_or_hot(nouns, hotd):
            drink= drink_explicitly(nouns, hotd)
            bot_answer="Your "+drink+" is coming right now!"
            print(bot_answer)
        else:
            bot_answer="Sorry we do not sell what you asked for"
    txt_to_sp(bot_answer,'en')

more_order="Do you want anything else?"
menu(hd,cd)
repeat_pls = "Sorry, I did not understand, please say it loudly"

while True:
    
    cust_order = sp_to_txt(mic)
    print(cust_order)

    nlp = spacy.load('en_core_web_sm')

    while not cust_order:
        txt_to_sp(repeat_pls,'en')
        cust_order = sp_to_txt(mic)
        print(cust_order)
    order_doc = nlp(cust_order)
    matcher = Matcher(nlp.vocab)

    result = get_double_noun(order_doc)
    if not result:
        result = get_adj_noun(order_doc)
        #Change1
        # if not result:
        #     result = extract_double_ppn(order_doc)

    print(result)
    [to_nltk_tree(sent.root).pretty_print() for sent in order_doc.sents]


    bot_ans(result,hd,cd,order_doc)
    
    txt_to_sp(more_order,'en')
