import json
from speak import sp_to_txt,txt_to_sp
import spacy
from spacy import displacy
from spacy.symbols import NOUN, NUM, ADJ, VERB, PROPN
from nltk import Tree
import speech_recognition as sr
from spacy.matcher import Matcher
from pathlib import Path

mic = sr.Microphone()
##Start Loading KB
with open('KB_rest_full.json', 'r') as f:
    rest_dict = json.load(f)

cd = []
alc_cd = []
hd = []
alc_hd = []

print("\n Hot Drinks:")
for each in rest_dict['hot_drinks']:
    #print(each['drink'],each['alc'])
    hd.append(each['drink'])
    alc_hd.append(each['alc'])
    
print(hd) 

print("Cold Drinks:")
for each in rest_dict['cold_drinks']:
    #print(each['drink'],each['alc'])
    cd.append(each['drink'])
    alc_cd.append(each['alc'])

print(cd) 
##Done Loading KB

def concatanate_elements(list_drinks):
    list_sentence = list_drinks[0]
    for each in range(1,len(list_drinks)-1):
        list_sentence = list_sentence+', '+list_drinks[each]
    list_sentence = list_sentence+" and "+ list_drinks[len(list_drinks)-1]
    #print(list_sentence)
    return list_sentence

def menu(hot,cold):
    
    hot_drinks_sentence = concatanate_elements(hot)
    cold_drinks_sentence = concatanate_elements(cold)

    #welcome = "Ciao! Welcome to Sapienza bar! We have hot and cold drinks for you!"
    #txt_to_sp(welcome,'en')

    #hd_list= "Ciao! Welcome to Sapienza bar! We have hot and cold drinks for you! We offer "+hot_drinks_sentence+" as a hot drink"
    #txt_to_sp(hd_list,'en')

    cd_list = "Ciao! Welcome to Sapienza bar! We have hot and cold drinks for you! We offer "+hot_drinks_sentence+" as a hot drink. And, as a cold drink we have "+cold_drinks_sentence
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

def get_adj_noun(nlp_doc): #Eg Cold Beer
    pattern = [{'POS': 'ADJ'}, {'POS': 'NOUN'}]
    matcher.add('FULL_NAME', None, pattern)
    matches = matcher(nlp_doc)
    for match_id, start, end in matches:
        span = nlp_doc[start:end]
        return span.text

def get_double_ppn(nlp_doc): #Eg Green Tea
    pattern = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]
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
    if res in hot:
        flag='h'
        return res,flag

    elif res in cold:
        flag='c'
        return res,flag
    else:
        return None,None


def is_alc(order,flag,hot,cold,alc_hot,alc_cold):
    if flag=='h':
        return alc_hot[hot.index(order)]
    elif flag=='c':
        return alc_cold[cold.index(order)]

def yes_alc(your_order):
    bot_answer = your_order+" is alcoholic. Please tell us your age"
    print(bot_answer)
    txt_to_sp(bot_answer,'en')
    
    cust_age = sp_to_txt(mic)
    #cust_age = input("Enter age: ")
    print(cust_age)

    nlp = spacy.load('en_core_web_sm')

    while not cust_age:
        txt_to_sp("Sorry, I did not understand your age, please say it loudly",'en')
        cust_age = sp_to_txt(mic)
        #cust_age = input("Enter age: ")
        print(cust_age)
    age_doc = nlp(cust_age)
    yrs = []
    # for possible_subject in age_doc:
    #     # if str(possible_subject.pos).isdigit():
    #     #     print(str(possible_subject.pos))
    #     #     # yrs.append(possible_subject.text)
    #     #     print('You are ', yrs[0], 'years old')
    #     #     if int(yrs[0]) < 18:
    #     #         bot_answer = 'Sorry, we can not sell you alcoholic drink'
    #     #     else:
    #     #         bot_answer = "Your "+ your_order +" is coming right now"
    #     #     print(bot_answer)
    #     #     txt_to_sp(bot_answer,'en')
    #     #     break

    age_consideration= []
    for possible_subject in age_doc:
        if str(possible_subject).isdigit():
            age_consideration.append(int(str(possible_subject)))
            print('You are ', age_consideration[0], 'years old')
            if age_consideration[0] < 18:
                bot_answer = 'Sorry, we can not sell you alcoholic drink'
            else:
                bot_answer = "Your "+ your_order +" is coming right now"
            print(bot_answer)
            txt_to_sp(bot_answer,'en')
            break
    else:
        bot_answer = "You did not provide us your age sorry, bye"
        print(bot_answer)
        txt_to_sp(bot_answer,'en')    

def collect_nouns(ord_doc):
    nouns = []
    for possible_subject in ord_doc:
        if possible_subject.pos == NOUN or possible_subject.pos ==PROPN:
            #Beer is noun, vodka is proper noun, espresso is verb
            nouns.append(possible_subject.text)
            #break
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

def bot_ans(res,hotd,coldd,alc_hd,alc_cd,ord_doc):
    if res:
        #print("res: " +res)
        #print("length: " +str(len(res)))
        flag = "False"
        your_order,flag=match_in_menu(res,hotd,coldd)
        if flag:
            is_order_alc=is_alc(your_order,flag,hotd,coldd,alc_hd,alc_cd)
            print("In res, order is "+your_order+" & it is "+is_order_alc+" alcoholic")
            if is_order_alc=='yes':
                yes_alc(your_order)

            else:
                bot_answer = "Your "+ your_order +" is coming right now"
                print(bot_answer)
                txt_to_sp(bot_answer,'en')
        # else:
        #     bot_answer="Sorry we do not sell what you asked for"
        #     print(bot_answer)
        #     txt_to_sp(bot_answer,'en')
            return

    #else:
    nouns = collect_nouns(ord_doc)
    for noun in nouns:
        print("Nouns are :"+noun)
    if is_cold_or_hot(nouns, coldd):
        drink = drink_explicitly(nouns, coldd)
        is_order_alc=is_alc(drink,'c',hotd,coldd,alc_hd,alc_cd)
        if is_order_alc=='yes':
            yes_alc(drink)
        else:
            bot_answer="Your "+drink+" is coming right now!"
            print(bot_answer)
            txt_to_sp(bot_answer,'en')
    elif is_cold_or_hot(nouns, hotd):
        drink= drink_explicitly(nouns, hotd)
        is_order_alc=is_alc(drink,'h',hotd,coldd,alc_hd,alc_cd)
        if is_order_alc=='yes':
            yes_alc(drink)
        else:
            bot_answer="Your "+drink+" is coming right now!"
            print(bot_answer)
            txt_to_sp(bot_answer,'en')
    else:
        bot_answer="Sorry we do not sell what you asked for"
        print(bot_answer)
        txt_to_sp(bot_answer,'en')


more_order="Do you want anything else?"
no_order_1="I do not want anything"
no_order_2="I don't want anything"
menu(hd,cd)
repeat_pls = "Sorry, I did not understand, please say it loudly"

while True:
    
    cust_order = sp_to_txt(mic)
    #cust_order = input("Enter drink: ")
    print(cust_order)

    nlp = spacy.load('en_core_web_sm')

    while not cust_order:
        txt_to_sp(repeat_pls,'en')
        cust_order = sp_to_txt(mic)
        #cust_order = input("Enter another drink: ")
        print(cust_order)


    if (cust_order==no_order_1 or cust_order==no_order_2):
        txt_to_sp("See you soon. Have a nice day!",'en')
        print("See you soon. Have a nice day!")
        exit()
    order_doc = nlp(cust_order)
    matcher = Matcher(nlp.vocab)

    result = get_double_noun(order_doc)
    if not result:
        #print("D N didn't work")
        result = get_adj_noun(order_doc)
        if not result:
            #print("Adj didn't work")
            result = get_double_ppn(order_doc)

    #print("Get result is: " + str(result))
    #[to_nltk_tree(sent.root).pretty_print() for sent in order_doc.sents]
    
    #displacy.serve(order_doc, style='dep')
    svg = displacy.render(order_doc, style="dep")
    output_path = Path("sentence.svg")
    output_path.open("w", encoding="utf-8").write(svg)

    bot_ans(result,hd,cd,alc_hd,alc_cd,order_doc)
    
    txt_to_sp(more_order,'en')