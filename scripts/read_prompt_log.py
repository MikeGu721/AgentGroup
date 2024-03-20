import json
from collections import defaultdict
import os

# filenames = ['20240307140732.591771.json']
# filenames = ['20240307160322.938612.json','20240307165351.886054.json']
# filenames = ['20240307165351.886054.json']
filenames = ['20240307174753.552062.json']
debug = True

def func_prompt(prompt):
    if '### Plan' in prompt:
        return 'run_act'
    if '### Number of Action History:' in prompt:
        return 'run_converse'
    if 'You are playing a game. Here are rules of this game:' in prompt:
        return 'run_perceive'
    if '### Speech:' in prompt:
        return 'run_speech'
    if '### Chat Summarization:' in prompt:
        return 'run_summarization'
    if '### Belief Change:' in prompt:
        return 'run_update'
    if '### Choice:' in prompt:
        return 'run_vote'

func2token = {}
# jsonfile = json.loads(open(filename, encoding='utf-8'))
for filename in filenames:
    jsonfile = open(os.path.join('..','logs',filename), encoding='utf-8')
    for line in jsonfile:
        jsonline = json.loads(line)
        if ('args' in jsonline) and (jsonline['args'] == 'Prompt Log'):
            kwargs = json.loads(jsonline['kwargs'])
            prompt = kwargs['prompt']
            output = kwargs['output']
            if output == 'None': continue
            if 'func_name' in kwargs:
                func = kwargs['func_name']
            else:
                func = func_prompt(prompt)
            prompt_token = len(str(prompt).split(' '))
            output_token = len(str(output).split(' '))
            if func not in func2token: func2token[func] = {'Prompt Length':[], 'Output Length':[]}
            func2token[func]['Prompt Length'].append(prompt_token)
            func2token[func]['Output Length'].append(output_token)

            if debug:
                print('='*20,'FUNCTION','='*20)
                print(func)
                print('='*21,'PROMPT','='*21)
                print(prompt)
                print('='*20,'RESPONSE','='*20)
                print(output)
                print('='*50)
                print()

for func in func2token:
    print_str = func+': \n'
    for key, item in func2token[func].items():
        print_str+=key+': '+'%7.1f'%(sum(item)/len(item))+'; '
    print_str = print_str[:-1]+'\n'
    for key, item in func2token[func].items():
        print_str += key.split(' ')[0] + ' Maximum' + ': ' + '%6.f' % (max(item)) + '; '
    print(print_str)
    print()