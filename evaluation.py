'''
effectiveness evaluation内容
1. 自己接受了多少条action_history
2. 自己的action_space
3. 收到了多少个belief
4. 收到了多少个relationship
5. update分数是否在规定范围内

reasonability evaluation
1. 生成thought、goal、action来让GPT判断行为是否一致
2. 某个角色说的所有内容
3. 所有角色
4. 设计特定的action history来判断
    - relationship的更新值
    - belief的更新值
    - guess的合理性
    - vote的合理性
    - vote except self的合理性
5. 对于所有结局，guess、vote、vote except self之间的差异性
6.
'''
import collections
import json
import os.path

import numpy
from config import TEST_FOLDER
# evaluate_saving_dir = './storage/test_version'
# evaluate_saving_dir = './storage/succession/saving/gpt35_7'
suc_dir = './storage/succession/saving'
# action_history_dir = os.path.join(evaluate_saving_dir, 'action_history')
chn = True
qe = False
n_gram=2


if qe:
    print('='*50)
    print('Quantity Evaluation')
    print('='*50)
    print()

    for evaluate_saving in os.listdir(suc_dir):
        if evaluate_saving == 'initial_version': continue
        evaluate_saving_dir = os.path.join(suc_dir, evaluate_saving)
        if not os.path.isdir(evaluate_saving_dir): continue
        action_history_dir = os.path.join(evaluate_saving_dir, 'action_history')
        line_to_be_evaluated = collections.defaultdict(list)
        for json_file in os.listdir(action_history_dir):
            json_data = open(os.path.join(action_history_dir, json_file), encoding='utf-8')
            for json_line in json_data:
                json_line = json.loads(json_line)
                action_type = json_line['action_type']
                action = json_line['action']
                agent_response = action.split('agent response: ')[-1].split('[SEP]')[0].strip()
                ground_truth = action.split('ground truth: ')[-1].strip()

                if action_type.startswith('### EVALUATION') and agent_response != '[SKIP]':
                    line_to_be_evaluated[action_type].append([agent_response, ground_truth])
        if line_to_be_evaluated:
            print(evaluate_saving)
            [print(j,'mean=',numpy.mean([1 if i[0] == i[1] else 0 for i in line_to_be_evaluated[j]])) for j in line_to_be_evaluated]

print('='*50)
print('Entropy Evaluation')
print('='*50)
print()
for evaluate_saving in os.listdir(suc_dir):
    if evaluate_saving == 'initial_version': continue
    evaluate_saving_dir = os.path.join(suc_dir, evaluate_saving)
    if not os.path.isdir(evaluate_saving_dir): continue
    action_history_dir = os.path.join(evaluate_saving_dir, 'action_history')
    n_gram_dict = collections.defaultdict(int)
    count = 0
    for json_file in os.listdir(action_history_dir):
        json_data = open(os.path.join(action_history_dir, json_file), encoding='utf-8')
        for json_line in json_data:
            json_line = json.loads(json_line)
            action_type = json_line['action_type']
            action = json_line['action']
            if not chn:
                action = action.split(' ')
            if action_type == '### SAY' or action_type.startswith('### SPEECH'):
                for i in range(len(action)-n_gram+1):
                    n_gram_dict[action[i:i+n_gram]] += 1
                    count += 1
    entropy = 0
    for key, item in n_gram_dict.items():
        p = item/count
        entropy -= p * numpy.log(p)
    print('%30s, %d-gram count: %7d, Entropy: %7.5f, All Token: %10d'%(evaluate_saving,n_gram, len(n_gram_dict),entropy, count))






