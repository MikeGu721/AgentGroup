import os
root_dir = os.getcwd()
import sys
sys.path.append(root_dir)
import json

log_file = os.path.join(root_dir, "../temp_log/20231222173722.026320.json")
with open(log_file, 'r', encoding='utf-8') as f:
    for line in f:
        json_data = json.loads(line)
        if 'ERROR' not in json_data['args']: continue
        cc = json_data['kwargs']
        kwargs = json.loads(cc)
        if 'important_log' in kwargs and 'log_type' in kwargs:
            try:
                print(kwargs['prompt'])
                # print('Action Type', kwargs['log_type'])
                # print('Source Character', kwargs['source_character'])
                # print('Target Character', kwargs['target_character'])
                # print('Thought', kwargs['thought'])
                # print('Content', kwargs['log_content'])
                # print('==='*20)
            except:
                print('ERROR')
                print('==='*20)
        elif 'prompt' in kwargs:
            print('### Thought\n')
            print(kwargs['prompt'])
            print()
            print('长度:',len(kwargs['prompt']))
            print('==='*20)
        
        # log = eval(log)
        # log_common = {'sid': log['sid'], 'id': log['id'], 'time': log['time'], 'args': log['args']}
        # log_kwargs = eval(log['kwargs'])
        # log = {**log_common, **log_kwargs}

        # if log['args'] == 'Prompt Log' and '### Thought:' in log['prompt']:
        #     character = log['prompt'].split('You are ')[1].split(',')[0]
        #     print(f"{character} Act (Thought and Choose): {log['output']}")
        # elif 'important_log' in log.keys():
        #     if log['log_type'] == 'Conclusion of environment':
        #         character = log['source_character']
        #         content = log['log_content'].replace("\n\n", "")
        #         print(f"{character} {log['log_type']}: {content}")
        #     elif log['log_type'] == 'Dialogue content':
        #         content = log['log_content'].replace("\n\n", "")
        #         character1 = log['source_character']
        #         character2 = log['target_character']
        #         print(f"{character1} to {character2} {log['log_type']}: {content}")
        #     elif log['log_type'] in ['Belief update']:
        #         print(f"{log['log_type']}: {log['args']}")
        #     elif log['log_type'] in ['Relation status', 'Environment judgement', 'Reflection result']:
        #         print(f"{log['args']}{log['log_content']}")