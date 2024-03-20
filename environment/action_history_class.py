from collections import defaultdict
import os
import json


class Action:
    def __init__(self, idd, source_character_id_number, to_character_id_number, action_type, action, happen_time=0):
        '''
        Action Type:
            ### MEET: 所有人可见的信息——谁和谁见面了
            ### CHAT: 仅对话双方可见的信息——谁和谁交谈了
            ### REFLECT: 仅自己可见——反思结果

        Input:
            source_character_id_number, str
            to_character_id_number, str
            action_type, str
            action, str
            happen_time, int

        Output:
            None
        '''
        self.build_up(idd, source_character_id_number, to_character_id_number, action_type, action, happen_time)

    def read(self):
        return self.id, self.source_character_id_number, self.to_character_id_number, self.action_type, self.action, self.happen_time

    def build_up(self, idd, source_character_id_number, to_character_id_number, action_type, action, happen_time):
        '''
        构建一个Action，source_character对to_character做了action_type类型的事，具体是：action，发生在happen_time时间
        Input:
            idd, int
            source_character_id_number, str
            to_character_id_number, str
            action_type, str
            action, str
            happen_time, int

        Output:
            None
        '''
        self.id = idd
        self.source_character_id_number = source_character_id_number
        self.to_character_id_number = to_character_id_number
        self.action_type = action_type
        self.action = action
        self.happen_time = happen_time


class ActionHistory:
    def __init__(self, save_folder=None, basic_setting_file=None)->None:
        '''
        初始化ActionHistory类
        Input:
            save_folder: str, 存档所在地址
        Output:
            None
        '''
        self.action_history = []
        self.all_happen_time = set()
        if save_folder:
            self.initialize(save_folder, basic_setting_file)

    def initialize(self, save_folder, basic_setting_file)->int:
        '''
        从具体的存档初始化整个ActionHistory类
        Input:
            save_folder: str, 存档所在地址
        Output:
            success_number: int, 成功读取多少条action
        '''
        effective_ids = []
        if basic_setting_file:
            basic_setting = json.load(open(basic_setting_file, encoding='utf-8'))
            state_uid = basic_setting['finished_states']
            for i, j in state_uid.items():
                effective_ids.extend(j)
            effective_ids = list(set(effective_ids))
        success_number = 0
        for file in os.listdir(save_folder):
            save_file = os.path.join(save_folder, file)
            success_number += self.load(save_file, effective_ids)
        return success_number

    def save(self, save_folder, action_number_in_each_file=1000)->None:
        '''
        保存所有的行为到指定的文件夹
        Input:
            save_folder: str, 存放地址
            action_number_in_each_file: int, 每个文件存放多少条action
        Output:
            None
        '''
        start_file_index = 0  # 或者可以直接搞整除
        start_action_index = 0
        # 防一手error
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)
        fw = open(os.path.join(save_folder, '%04d.json' % start_file_index), 'w', encoding='utf-8')
        while start_action_index < len(self.action_history):
            if start_action_index % action_number_in_each_file == 0:
                fw = open(os.path.join(save_folder, '%04d.json' % start_file_index), 'w', encoding='utf-8')
                start_file_index += 1

            action = self.action_history[start_action_index]
            json_data = {'id':action.id,
                         'source_character_id_number': action.source_character_id_number,
                         'to_character_id_number': action.to_character_id_number,
                         'action_type': action.action_type,
                         'action': action.action,
                         'happen_time': action.happen_time}
            fw.write(json.dumps(json_data, ensure_ascii=False) + '\n')
            start_action_index += 1

    def load(self, save_log_file, effectiveness_ids:list)->int:
        '''
        从文件读取游戏中发生的所有行为
        Input:
            save_file: str, 保存文件的地址
        Output:
            success_number: int, 读取了多少条历史动作
        '''
        success_number = 0
        json_file = open(save_log_file, encoding='utf-8')
        for json_line in json_file:
            json_data = json.loads(json_line)
            if json_data['id'] not in effectiveness_ids: continue
            action = Action(json_data['id'],
                            json_data['source_character_id_number'],
                            json_data['to_character_id_number'],
                            json_data['action_type'],
                            json_data['action'],
                            json_data['happen_time'])
            self.insert_action(action)
            success_number += 1
        return success_number
    def get_description(self, character_id_number, happen_time_list:list=None, max_num:int=9999, type_list=None)->str:
        '''
        获得某个角色能看到的所有行为的描述
        Input:
            character_id_number: str
            happen_time_list: list [int], 检索这个几个时间点的事件
            max_num: int, 最大检索记忆数
        Output:
            action_description: str
        '''
        visible_action = self.retrieve_character_history(character_id_number, happen_time_list, type_list)
        if not visible_action: return 'This is the first round of the game, and nothing has happened so far.'
        action_description = ''

        # 越晚发生的排在visible_action后面
        for index, action in enumerate(visible_action[-100:][::-1]):
            action_description += action.action.strip()+'\n'
            if index + 1 > max_num: break  # 超出最大数
        action_description = action_description.strip()
        if action_description == '':
            action_description = 'This is the first round of the game, and nothing has happened so far.'
        return action_description.strip()

    def get_all_action_history(self)->list:
        '''
        获得self character所有行动的历史
        Input:
            None
        Output:
            action_history: list
        '''
        return self.action_history

    def insert_action(self, new_action: Action)->int:
        '''
        插入动作
        Input:
            new_action
        Output:
            None
        '''
        new_action.id = len(self.action_history)
        self.all_happen_time.add(new_action.happen_time)
        self.action_history.append(new_action)
        return new_action.id

    def extend_actions(self, new_action_list: list)->None:
        '''
        插入一堆动作
        Input:
            new_action_list: list (Action)
        Output:
            None
        '''
        for new_action in new_action_list:
            self.insert_action(new_action)

    def retrieve_character_history(self, character_id_number: str, happen_time_list:list=None,type_list:list=None)->list:
        '''
        获得某个角色能看到的所有行为历史
        Input:
            character_id_number: str
            happen_time_list: list [int], 检索这个几个时间点的事件
        Output:
            visible_action: list, 角色能看到的所有行为
        '''
        if not happen_time_list: happen_time_list = list(self.all_happen_time)
        # if character_id_number:
        #     visible_action = [i for i in self.action_history if self.see_action(i, happen_time_list, character_id_number)]
        # else:

        visible_action = [i for i in self.action_history if self.see_action(i, happen_time_list, character_id_number, type_list)]
        # 时序——list后面的内容是最新的action
        visible_action = visible_action[::-1]
        return visible_action

    def see_action(self, action:Action, happen_time_list, character_id_number,type_list):
        if type_list:
            pass
        else:
            if action.action_type in ['### SAY']: return False  # ### SAY只有在Summarize时可见，并且summarize不会调用action_history
            if action.happen_time not in happen_time_list: return False
            if character_id_number in [action.to_character_id_number, action.source_character_id_number]: return True
            if action.action_type in ['### MEET', '### SPEECH_NORMAL', '### SPEECH_VOTE']: return True  # 所有人的MEET和SPEEC事件都能见到
            if action.action_type not in ['### REFLECT', '### CHAT_SUMMARIZATION']: return False  # 所有人只能回忆自己说了啥以及反思了啥
