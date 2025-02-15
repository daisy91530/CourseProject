import torch
import operator
from pytorch_pretrained_bert import BertTokenizer, BertModel, BertForMaskedLM
import nltk
nltk.download('wordnet')
from nltk import *
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer

data_path = "Question.txt"

with open(data_path, 'r', encoding='UTF-8') as f:
    data = f.read()
    
lines = data.split('\n')
train_set = list()
train_statement = list()
train_question = list()
train_choice = list()
train_answer = list()

for i, line in enumerate(lines):
    if len(line) == 0:
        train_set.append(lines[i - 21 : i])

for problem in train_set:
    last_line = problem[20].split('\t')
    train_statement.append(problem[:-1])
    train_question.append(last_line[0])
    train_answer.append(last_line[1])
    ch = last_line[3].lower().split('|')
    train_choice.append(ch)

train_statement_string = list()
for problem in train_statement:
    final_string = ""
    for id, line in enumerate(problem):
        line = line.split(' ')
        line = line[1:]
        for i in range(len(line)):
            if not line[i][0].isalpha() and not line[i][-1].isalpha():
                line[i] = ''
            elif line[i][0].isalpha() and not line[i][-1].isalpha():
                line[i] = line[i][:-1]
            elif not line[i][0].isalpha() and line[i][-1].isalpha():
                line[i] = line[i][1:]
        final_string = final_string + ' '.join(line)
    train_statement_string.append(final_string)

train_question_string = list()
for problem in train_question:
    final_string = ""
    for word in problem.split(' '):
        if len(word) >= 5 and word[0:5] == 'XXXXX':
            word = '$'
        elif word[0].isalpha() == False and word[-1].isalpha() == False:
            word = ','
        final_string = final_string + word + ' '
    train_question_string.append(final_string[1:])

def BERT(textA, textB):
    tokenizer = BertTokenizer.from_pretrained('bert-large-uncased')

    tokenized_textA = tokenizer.tokenize(textA)
    tokenized_textB = tokenizer.tokenize(textB)

    masked_index = len(tokenized_textA) + tokenized_textB.index('$')
    tokenized_text = tokenized_textA + tokenized_textB
    tokenized_text[masked_index] = '[MASK]'

    indexed_tokens = tokenizer.convert_tokens_to_ids(tokenized_text)
    segments_ids = [0] * len(tokenized_textA) + [1] * len(tokenized_textB)

    tokens_tensor = torch.tensor([indexed_tokens])
    segments_tensors = torch.tensor([segments_ids])
    
    model = BertForMaskedLM.from_pretrained('bert-large-uncased')
    model.eval()

    predictions = model(tokens_tensor, segments_tensors)

    predicted_index = torch.argmax(predictions[0, masked_index]).item()
    predicted_token = tokenizer.convert_ids_to_tokens([predicted_index])[0]
    print(predicted_token)

    return predicted_token

wnl = WordNetLemmatizer()

def isplural(word):
    lemma = wnl.lemmatize(word, 'n')
    plural = True if word is not lemma else False
    return plural, lemma

def wordtovec(pred, choise):
    pred = isplural(pred)[1]
    WF_pred = wordnet.synsets(pred)
    
    score = dict()
    for c in choise:
        if pred == c:
            return c
        nc = isplural(c)[1]
        WF_c = wordnet.synsets(nc)
        if WF_pred and WF_c:
            score[c] = WF_pred[0].wup_similarity(WF_c[0])
            if score[c] == None:
                score[c] = 0

    return max(score.items(), key=operator.itemgetter(1))[0]

def main():
    for idx in range(9):
        i = idx
        pred = BERT(train_statement_string[i], train_question_string[i])
        my_answer = wordtovec(pred, train_choice[i])
        print("Choice:", my_answer)
        print("Answer:", train_answer[i])

main()