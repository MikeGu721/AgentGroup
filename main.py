'''
整个流程
1. 初始化Character、Environment、阵营
2. 竞争阶段
3. 合作阶段
4. reflection阶段
5. 结算阶段
'''
import collections
import json

from character.all_character_class import AllCharacter
from environment.all_resource_class import AllResource
from environment.action_history_class import ActionHistory, Action

import os
from config import *
from logger_class import Logger

def verify_constrained_action(gpt_response, action_candidates:list)->bool:
    action_candidates = [str(i) for i in action_candidates]
    gpt_response = str(gpt_response)
    if debug:
        print('='*20+'DEBUG START'+'='*20)
        print('='*19+'VERIFICATION'+'='*19)
        print()
        print(action_candidates)
        print()
        print('='*19+'GPT RESPONSE'+'='*19)
        print()
        print(gpt_response)
        print()
        print('='*15+'VERIFICATION RESULT'+'='*15)
        print()
        print(gpt_response in action_candidates)
        print()
        print('='*21+'DEBUG END'+'='*21)
    if gpt_response not in action_candidates:
        return False
    else:
        return True

def succession_winner(defender_id_number, character_vote_dict)->list:
    defender_chosen_id_number = character_vote_dict[defender_id_number]
    if defender_chosen_id_number != defender_id_number:
        return defender_chosen_id_number
    vote_list = []
    for key, vote_for in character_vote_dict.items():
        vote_list.append(vote_for)
    vote_dict = collections.Counter(vote_list)
    winner = []
    winner_get_vote = -1
    for character_id_number, get_vote in vote_dict.items():
        if get_vote > winner_get_vote:
            winner_get_vote = get_vote
            winner = []
        winner.append(character_id_number)
    if type(winner) != list:
        winner = [winner]
    return winner


class SucArena:
    def __init__(self,
                 all_round_number: int,
                 battle_chat_round: int = 3,
                 collabration_chat_round: int = 3,
                 save_folder=None,
                 test_folder=None,
                 human_input=None,
                 logger=None):
        '''
        初始化游戏环境
        Input:
            all_round_number: int, 游戏总轮数
            battle_chat_round: int, 每次对抗阶段对话总共有几轮
            collabration_chat_round: int, 每次合作阶段对话总共有几轮
            save_folder: str 存档地址
            human_input: str 人类输入
            logger: Logger 是否需要直接输入一个Logger
        Output:
            None
        '''

        self.all_round_number = all_round_number
        self.battle_chat_round = battle_chat_round
        self.collaboration_chat_round = collabration_chat_round
        if not logger:
            self.logger = Logger()
        else:
            self.logger = logger
        self.log_file_name = self.logger.log_file

        self.save_folder = save_folder
        self.test_folder = test_folder
        if save_folder:
            self.initialize(save_folder)

            # 赋予NPC社会影响力
            for index, resource in enumerate(self.resources.get_all_resource()):
                owner_id_number = resource.owner
                self.characters.get_character_by_id(owner_id_number).give_influence(resource.influence)

        else:
            self.characters = AllCharacter(logger=self.logger)
            self.resources = AllResource()
            self.rule_setting = ''
            self.action_history = ActionHistory


    def initialize(self, save_folder) -> None:
        '''
        初始化Logger、Character、Resources、RuleSetting、ActionHistory
        Input:
            save_folder: 存档数据存放的位置
        Output:
            None
        '''
        self.logger.gprint('### Initializing Directory Found: ', save_folder)
        basic_setting = json.load(open(os.path.join(save_folder, 'basic_setting.json'), encoding='utf-8'))

        self.rule_setting_file_name = basic_setting['rule_setting']
        self.finished_states = basic_setting['finished_states']
        if basic_setting['log_file_name']:
            self.logger.read_save_file(basic_setting['log_file_name'], False)

        self.characters = AllCharacter(os.path.join(save_folder, 'characters'), logger=self.logger)
        self.resources = AllResource(os.path.join(save_folder, 'resources'))
        self.rule_setting = open(self.rule_setting_file_name, encoding='utf-8').read()
        self.action_history = ActionHistory(os.path.join(save_folder, 'action_history'), os.path.join(save_folder, 'basic_setting.json'))


        self.logger.gprint('### Number of initialized roles: ', len(self.characters.get_all_characters()))
        self.logger.gprint('### Number of main roles: ', len(self.characters.main_characters_id_number))
        self.logger.gprint('### Number of initialized resources: ', len(self.resources.get_all_resource()))
        self.logger.gprint('### Number of initialized action history: ',
                           len(self.action_history.get_all_action_history()))
    def switch_state(self):
        self.state_index = 0
        all_state = ['']

    def save(self, save_folder) -> None:
        '''
        保存环境
        Input:
            save_folder: 存放地址
        Output:
            None
        '''
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)

        config_file = open('config.py', encoding='utf-8')
        basic_setting = {}
        for line in config_file:
            line = line.split('#')[0]
            if '=' in line:
                key, value = [i.strip() for i in line.split('=')]
                basic_setting['config_file_'+key] = value
        basic_setting['rule_setting'] = self.rule_setting_file_name
        basic_setting['finished_states'] = self.finished_states
        basic_setting['log_file_name'] = self.log_file_name

        save_characters_folder = os.path.join(save_folder, 'characters')
        save_resources_folder = os.path.join(save_folder, 'resources')
        save_action_history_folder = os.path.join(save_folder, 'action_history')

        open(os.path.join(save_folder, 'basic_setting.json'), 'w', encoding='utf-8').write(json.dumps(basic_setting,
                                                                                                      indent=4,
                                                                                                      ensure_ascii=False))
        self.logger.gprint('Save basic_setting.json to: ' + str(os.path.join(save_folder, 'basic_setting.json')))
        for character in self.characters.get_all_characters(): character.save(save_characters_folder)
        self.logger.gprint('Save self.character to: ' + str(save_characters_folder))
        for resource in self.resources.get_all_resource(): resource.save(save_resources_folder)
        self.action_history.save(save_action_history_folder)
        self.logger.gprint('Save self.action_history to: ' + str(save_action_history_folder))

    def new_character_insert(self):
        '''
        插入新角色
        Input:
            待定
        Output:
            待定
        '''
        pass

    def new_resource_insert(self):
        '''
        插入新的资源
        Input:
            xxx
        Output:
            xxx
        '''
        pass

    def new_action_insert(self, new_action: list, now_round_number: int):
        '''
        插入新的行为
        Input:
            new_action: list [source_character_id_number:str, target_character_id_number:str, action_type:str, action:str]
            now_round_number: int
        Output:
            None
        '''
        action = Action(-1, new_action[0], new_action[1], new_action[2], new_action[3], now_round_number)
        action_index = self.action_history.insert_action(action)
        return action_index

    def get_rule_setting(self):
        '''
        返回Rule Setting
        Input:
            None
        Output:
            None
        '''
        return self.rule_setting

    def get_all_resource_description(self):
        '''
        返回所有资源的描述
        Input:
            None
        Output:
            None
        '''
        return self.resources.get_description()

    def get_all_character_list(self):
        '''
        返回所有角色列表
        Input:
            None
        Output:
            None
        '''
        return self.characters.get_characters_description_except_some()

    def get_round_description(self, now_round_number: int, compete=False, simple=False) -> str:
        '''
        得到一些关于当前轮数和总轮数的描述信息
        Input:
            now_round_number: int, 当前游戏进行到哪一轮
            compete: bool, 当前轮是否处于对抗阶段
        Output:
            round_description: str
        '''
        round_description = ''
        round_description += 'The game takes a total of %d rounds.' % self.all_round_number
        round_description += 'The current game is played to round %d.' % (now_round_number + 1)
        if simple:
            return round_description
        if compete:
            round_description += 'And you\'re in a confrontational phase where all of your options don\'t support you in accomplishing your goals.'
        else:
            round_description += 'And you\'re in a confrontational phase where all of your options don\'t support you in accomplishing your goals.'
        round_description += 'You\'ll talk to your chosen character for %d rounds per round.' % (
            self.battle_chat_round if compete else self.collaboration_chat_round)
        return round_description
    def announcement_stage(self, now_round_number:int)->None:
        '''
        进入宣言阶段
        Input:
            now_round_number: int,
        Output:
            None
        '''
        round_description = self.get_round_description(now_round_number, simple=True)
        candidates = ['%s: %s' % (character.get_id_number(), character.get_short_description()) for character in
                      self.characters.get_all_characters()]
        candidates = '\n'.join(candidates)
        # 主要角色按照影响力大小依次行动
        for character in self.characters.character_list:
            state_UID = 'NOW_ROUND:%d+ACTION:%s+CHARACTER:%s'%(now_round_number, 'ANNOUNCEMENT', character.id_number)
            if state_UID in self.finished_states: continue
            # 最终投票前的发言
            action_history = self.action_history.get_description(character_id_number=character.id_number, max_num=ACTIONHISTORY_RETRIEVE_NUM_ANNOUNCEMENT)
            # ======================================================================================= #
            # 调用GPT
            # 不需要校验
            # ======================================================================================= #
            speech, reasoning_process = character.speech_round(action_history,
                                                              candidates,
                                                              self.resources.get_description(),
                                                              self.rule_setting,
                                                              round_description
                                                              )
            # ======================================================================================= #

            speech = 'Round %d, public speech that character %s makes to all the other characters: %s' % (now_round_number+1, character.id_number, speech)

            self.logger.gprint(thought=reasoning_process,
                important_log='important_log',
                source_character=character.id_number,
                target_character=character.id_number,
                log_type='Open Speech In Round',
                log_content=speech)

            new_action = [character.id_number, character.id_number, '### SPEECH_NORMAL', speech]
            action_index = self.new_action_insert(new_action, now_round_number)
            self.finished_states[state_UID] = [action_index]
            if self.test_folder:
                self.save(self.test_folder)

    def compete_stage(self, now_round_number: int) -> None:
        '''
        对抗阶段——所有MC根据自身的影响力大小依次行动，选择一个不同阵营的character进行对话
        Input:
            now_round_number: int, 当前轮数
        Output:
            None
        '''
        round_description = self.get_round_description(now_round_number, compete=True)

        main_character_influence = self.characters.get_main_character_influence()
        # 主要角色按照影响力大小依次行动
        for main_character_id_number in main_character_influence:
            state_UID = 'NOW_ROUND:%d+ACTION:%s+CHARACTER:%s'%(now_round_number, 'COMPETE', main_character_id_number)
            if state_UID in self.finished_states: continue
            action_index = []
            # 获得行动的主要角色
            main_character = self.characters.get_character_by_id(main_character_id_number)
            self.logger.gprint(thought='',
                               important_log='important_log',
                               source_character=main_character.id_number,
                               target_character=main_character.id_number,
                               log_type='Action stage',
                               log_content='Confrontation stage'
                               )

            main_character_action_history_description = self.action_history.get_description(main_character_id_number, max_num=ACTIONHISTORY_RETRIEVE_NUM_COMPETE)
            # ======================================================================================= #
            # 调用GPT
            # 不需要校验
            # ======================================================================================= #
            # 让角色perceive环境，并生成总结
            main_character_environment_summary = main_character.perceive(self.rule_setting,
                                                                         self.resources.get_description(),
                                                                         main_character_action_history_description,
                                                                         self.all_round_number
                                                                         )
            # ======================================================================================= #
            self.logger.gprint(thought='',
                important_log='important_log',
                source_character=main_character.id_number,
                target_character=main_character.id_number,
                log_type='Conclusion of environment',
                log_content=main_character_environment_summary)

            # 确定可以对话的候选人
            candidates_list = '\n'.join(['%s: %s' % (candidate.id_number, candidate.get_short_description())
                                         for candidate in self.characters.get_all_characters() if
                                         (candidate.id_number != main_character.id_number and  # 剔除自己
                                          candidate.get_support_character() != main_character.id_number)])  # 选择不同阵营的人
            # 如果没有候选人，则跳过
            if not candidates_list: continue

            # ======================================================================================= #
            # 调用GPT
            # 需要校验
            # ======================================================================================= #
            # 从候选人中，确定需要对话的具体角色
            verify_result = ERROR_RETRY_TIMES
            while verify_result > 0:
                candidates = [candidate.id_number for candidate in self.characters.get_all_characters() if
                              candidate.id_number != main_character.id_number]
                action_space, thought, plan, chosen_character_id_number = main_character.act(main_character_environment_summary,
                                                            round_description,
                                                            main_character_action_history_description,
                                                            candidates_list,
                                                            self.battle_chat_round,
                                                            requirement_list=candidates)

                if verify_constrained_action(chosen_character_id_number, candidates):
                    verify_result = -10
                else:
                    verify_result -= 1
                    self.logger.gprint('ERROR! Log does not meet the requirements: ', gpt_response=chosen_character_id_number, candidates=candidates)
                if verify_result == 0:
                    raise Exception('Log does not meet the requirements.')
            # 评估事件
            evaluation_event = [main_character.id_number,
                                main_character.id_number,
                                '### EVALUATION ACTION SPACE',
                                'agent response: %s[SEP]ground truth: %s' % (str(action_space),
                                                                             str(candidates))]
            new_action_index = self.new_action_insert(evaluation_event, now_round_number)
            action_index.append(new_action_index)
            # ======================================================================================= #
            chosen_character = self.characters.get_character_by_id(chosen_character_id_number)
            chosen_character_action_history_description = self.action_history.get_description(chosen_character_id_number, max_num=ACTIONHISTORY_RETRIEVE_NUM_COMPETE)
            chosen_character_environment_summary = chosen_character.perceive(self.rule_setting,
                                                                             self.resources.get_description(),
                                                                             chosen_character_action_history_description,
                                                                             self.all_round_number)
            self.logger.gprint(thought='',
                important_log='important_log',
                source_character=chosen_character.id_number,
                target_character=chosen_character.id_number,
                log_type='Conclusion of environment',
                log_content=chosen_character_environment_summary)
            self.logger.gprint(thought=thought,
                important_log='important_log',
                source_character=main_character.id_number,
                target_character=chosen_character.id_number,
                log_type='Select dialogue role',
                log_content='')
            # 生成对话事件，标记为### MEET，所有角色可见
            action_event = [main_character.id_number, chosen_character.id_number, '### MEET',
                            "%s chat with %s in round %d, but others don't know what they are talking about." % (main_character.id_number, chosen_character.id_number, now_round_number)]
            meet_action_index = self.new_action_insert(action_event, now_round_number)
            action_index.append(meet_action_index)
            # 选择对话轮数——目前是规则限制好，就对话这么些轮数
            chat_round = BATTLE_CHAT_ROUND
            chat_history = ''
            for now_chat_round in range(chat_round):
                # ======================================================================================= #
                # 调用GPT
                # 不需要校验
                # ======================================================================================= #
                # 对话
                number_of_action_history, thought, action_event = main_character.converse(target_candidate_id_number=chosen_character.id_number,
                                                       target_character_description=chosen_character.get_short_description(),
                                                       environment_description=main_character_environment_summary,
                                                       action_history_description=main_character_action_history_description,
                                                       chat_history=chat_history,
                                                       plan=plan)
                evaluation_event = [main_character.id_number,
                                main_character.id_number,
                                '### EVALUATION ACTION HISTORY',
                                'agent response: %s[SEP]ground truth: %s' % (str(number_of_action_history),
                                                                          str(len([i for i in main_character_action_history_description.split('\n') if i])))]
                new_action_index = self.new_action_insert(evaluation_event, now_round_number)
                action_index.append(new_action_index)
                # ======================================================================================= #
                # 生成对话历史
                chat_history += action_event[-1] + '\n'
                new_action_index = self.new_action_insert(action_event, now_round_number)
                action_index.append(new_action_index)
                self.logger.gprint(thought=thought,
                    important_log='important_log',
                    source_character=main_character.id_number,
                    target_character=chosen_character.id_number,
                    log_type='Dialogue content',
                    log_content=action_event[-1])

                # ======================================================================================= #
                # 调用GPT
                # 不需要校验
                # ======================================================================================= #
                # 对话
                number_of_action_history, thought, action_event = chosen_character.converse(target_candidate_id_number=main_character.id_number,
                                                         target_character_description=main_character.get_short_description(),
                                                         environment_description=chosen_character_environment_summary,
                                                         action_history_description=chosen_character_action_history_description,
                                                         chat_history=chat_history)

                evaluation_event = [main_character.id_number,
                                main_character.id_number,
                                '### EVALUATION ACTION HISTORY',
                                'agent response: %s[SEP]ground truth: %s' % (str(number_of_action_history),
                                                                          str(len([i for i in chosen_character_action_history_description.split('\n') if i])))]
                new_action_index = self.new_action_insert(evaluation_event, now_round_number)
                action_index.append(new_action_index)
                # ======================================================================================= #
                # 生成对话历史
                chat_history += action_event[-1] + '\n'
                new_action_index = self.new_action_insert(action_event, now_round_number)
                action_index.append(new_action_index)
                self.logger.gprint(thought=thought,
                    important_log='important_log',
                    source_character=chosen_character.id_number,
                    target_character=main_character.id_number,
                    log_type='Dialogue content',
                    log_content=action_event[-1])

            # ======================================================================================= #
            # 调用GPT
            # 不需要校验
            # ======================================================================================= #
            # 双方各自总结对话内容
            for index, character in enumerate([main_character, chosen_character]):
                environment_summary = [main_character_environment_summary, chosen_character_environment_summary][index]
                number_of_chat_round, thought, action_event = character.summarize(environment_description=environment_summary,
                                                                                  chat_history=chat_history)
                evaluation_event = [character.id_number,
                                    character.id_number,
                                    '### EVALUATION CHAT ROUND',
                                    'agent response: %s[SEP]ground truth: %s' %
                                    (str(number_of_chat_round), str(chat_round))]
                new_action_index = self.new_action_insert(evaluation_event, now_round_number)
                action_index.append(new_action_index)
                new_action_index = self.new_action_insert(action_event, now_round_number)
                action_index.append(new_action_index)
                self.logger.gprint(thought=thought,
                    important_log='important_log',
                    source_character=character.id_number,
                    target_character=[main_character, chosen_character][(index+1)%2].id_number,
                    log_type='Dialogue Summarization',
                    log_content=action_event[3])

            self.finished_states[state_UID] = action_index
            if self.test_folder:
                self.save(self.test_folder)

    def collaborate_stage(self, now_round_number: int):
        '''
        合作阶段——所有MC根据自身的影响力大小依次行动，选择一个同阵营的character进行对话
        如果没有同阵营的角色，则跳过该MC
        Input:
            now_round_number: int, 当前轮数
        Output:
            None
        '''
        round_description = self.get_round_description(now_round_number, compete=False)
        main_character_influence = self.characters.get_main_character_influence()
        # 主要角色按照影响力大小依次行动
        for main_character_id_number in main_character_influence:
            state_UID = 'NOW_ROUND:%d+ACTION:%s+CHARACTER:%s'%(now_round_number, 'COLLABORATE', main_character_id_number)
            if state_UID in self.finished_states: continue
            action_index = []
            # 获得行动的主要角色
            main_character = self.characters.get_character_by_id(main_character_id_number)
            main_character_action_history_description = self.action_history.get_description(main_character_id_number, max_num=ACTIONHISTORY_RETRIEVE_NUM_COLLABORATE)
            self.logger.gprint(thought='',
                               important_log='important_log',
                               source_character=main_character.id_number,
                               target_character=main_character.id_number,
                               log_type='Action stage',
                               log_content='Cooperation stage'
                               )

            # ======================================================================================= #
            # 调用GPT
            # 不需要校验
            # ======================================================================================= #
            # 让角色perceive环境，并生成总结
            main_character_environment_summary = main_character.perceive(self.rule_setting,
                                                                         self.resources.get_description(),
                                                                         main_character_action_history_description,
                                                                         self.all_round_number)
            # ======================================================================================= #
            self.logger.gprint(thought='',
                important_log='important_log',
                source_character=main_character.id_number,
                target_character=main_character.id_number,
                log_type='Conclusion of environment',
                log_content=main_character_environment_summary)

            # 确定可以对话的候选人
            candidates_list = '\n'.join(['%s: %s' % (candidate.id_number, candidate.get_short_description())
                                         for candidate in self.characters.get_all_characters() if
                                         (candidate.id_number != main_character.id_number and  # 剔除自己
                                          candidate.get_support_character() == main_character.id_number)])  # 选择同阵营的人

            # candidates_list = '\n'.join(['%s: %s' % (candidate.id_number, candidate.get_short_description())
            #                              for candidate in self.characters.get_all_characters()])

            # 如果没有候选人，则跳过
            if not candidates_list: continue
            # ======================================================================================= #
            # 调用GPT
            # 需要校验
            # ======================================================================================= #
            # 从候选人中，确定需要对话的具体角色
            verify_result = ERROR_RETRY_TIMES
            while verify_result > 0:
                candidates = [candidate.id_number for candidate in self.characters.get_all_characters() if
                              candidate.id_number != main_character.id_number]
                action_space, thought, plan, chosen_character_id_number = main_character.act(main_character_environment_summary,
                                                                round_description,
                                                                main_character_action_history_description,
                                                                candidates_list,
                                                                self.collaboration_chat_round,
                                                                requirement_list=candidates)

                if  verify_constrained_action(chosen_character_id_number, candidates):
                    verify_result = -100
                else:
                    verify_result -= 1
                    self.logger.gprint('ERROR! Log does not meet the requirements: ', gpt_response=chosen_character_id_number, candidates=candidates)

                if verify_result == 0:
                    raise Exception('Log does not meet the requirements.')
            # 评估事件
            evaluation_event = [main_character.id_number,
                                main_character.id_number,
                                '### EVALUATION ACTION SPACE',
                                'agent response: %s[SEP]ground truth: %s' % (str(action_space),
                                                                             str(candidates))]
            new_action_index = self.new_action_insert(evaluation_event, now_round_number)
            action_index.append(new_action_index)
            chosen_character_action_history_description = self.action_history.get_description(chosen_character_id_number, max_num=ACTIONHISTORY_RETRIEVE_NUM)
            # ======================================================================================= #
            chosen_character = self.characters.get_character_by_id(chosen_character_id_number)


            # ======================================================================================= #
            # 调用GPT
            # 不需要校验
            # ======================================================================================= #
            chosen_character_environment_summary = chosen_character.perceive(self.rule_setting,
                                                                             self.resources.get_description(),
                                                                             chosen_character_action_history_description,
                                                                             self.all_round_number)
            # ======================================================================================= #
            self.logger.gprint(thought='',
                important_log='important_log',
                source_character=chosen_character.id_number,
                target_character=chosen_character.id_number,
                log_type='Conclusion of environment',
                log_content=chosen_character_environment_summary)
            self.logger.gprint(thought=thought,
                important_log='important_log',
                source_character=main_character.id_number,
                target_character=chosen_character.id_number,
                log_type='Select dialogue role',
                log_content='')

            # 生成对话事件，标记为### MEET，所有角色可见
            action_event = [main_character.id_number, chosen_character.id_number, '### MEET',
                            "%s chat with %s in round %d, but others don't know what they are talking about." % (main_character.id_number, chosen_character.id_number, now_round_number)]
            meet_action_index = self.new_action_insert(action_event, now_round_number)
            action_index.append(meet_action_index)
            # 选择对话轮数——目前是规则限制好，就对话这么些轮数
            chat_round = COLLABORATION_CHAT_ROUND
            chat_history = ''
            for now_chat_round in range(chat_round):
                # ======================================================================================= #
                # 调用GPT
                # 不需要校验
                # ======================================================================================= #
                # 对话
                number_of_action_history, thought, action_event = main_character.converse(target_candidate_id_number=chosen_character.id_number,
                                                       target_character_description=chosen_character.get_short_description(),
                                                       environment_description=main_character_environment_summary,
                                                       action_history_description=main_character_action_history_description,
                                                       chat_history=chat_history,
                                                       plan=plan)
                evaluation_event = [main_character.id_number,
                                main_character.id_number,
                                '### EVALUATION ACTION HISTORY',
                                'agent response: %s[SEP]ground truth: %s' % (str(number_of_action_history),
                                                                          str(len([i for i in main_character_action_history_description.split('\n') if i])))]
                new_action_index = self.new_action_insert(evaluation_event, now_round_number)
                action_index.append(new_action_index)
                # ======================================================================================= #
                # 生成对话历史
                chat_history += action_event[-1] + '\n'
                converse_action_index = self.new_action_insert(action_event, now_round_number)
                action_index.append(converse_action_index)
                self.logger.gprint(thought=thought,
                    important_log='important_log',
                    source_character=main_character.id_number,
                    target_character=chosen_character.id_number,
                    log_type='Dialogue content',
                    log_content=action_event[-1])

                # ======================================================================================= #
                # 调用GPT
                # 不需要校验
                # ======================================================================================= #
                # 对话
                number_of_action_history, thought, action_event = chosen_character.converse(target_candidate_id_number=main_character.id_number,
                                                         target_character_description=main_character.get_short_description(),
                                                         environment_description=chosen_character_environment_summary,
                                                         action_history_description=chosen_character_action_history_description,
                                                         chat_history=chat_history)
                evaluation_event = [chosen_character.id_number,
                                chosen_character.id_number,
                                '### EVALUATION ACTION HISTORY',
                                'agent response: %s[SEP]ground truth: %s' % (str(number_of_action_history),
                                                                          str(len([i for i in chosen_character_action_history_description.split('\n') if i])))]
                new_action_index = self.new_action_insert(evaluation_event, now_round_number)
                action_index.append(new_action_index)
                # ======================================================================================= #
                # 生成对话历史
                chat_history += action_event[-1] + '\n'
                converse_action_index = self.new_action_insert(action_event, now_round_number)
                action_index.append(converse_action_index)
                self.logger.gprint(thought=thought,
                    important_log='important_log',
                    source_character=chosen_character.id_number,
                    target_character=main_character.id_number,
                    log_type='Dialogue content',
                    log_content=action_event[-1])


            # ======================================================================================= #
            # 调用GPT
            # 不需要校验
            # ======================================================================================= #
            # 双方各自总结对话内容
            for index, character in enumerate([main_character, chosen_character]):
                environment_summary = [main_character_environment_summary, chosen_character_environment_summary][index]
                number_of_chat_round, thought, action_event = character.summarize(environment_description=environment_summary,
                                                                                  chat_history=chat_history)
                evaluation_event = [character.id_number,
                                    character.id_number,
                                    '### EVALUATION CHAT ROUND',
                                    'agent response: %s[SEP]ground truth: %s' %
                                    (str(number_of_chat_round), str(chat_round))]
                new_action_index = self.new_action_insert(evaluation_event, now_round_number)
                action_index.append(new_action_index)
                new_action_index = self.new_action_insert(action_event, now_round_number)
                action_index.append(new_action_index)
                self.logger.gprint(thought=thought,
                    important_log='important_log',
                    source_character=character.id_number,
                    target_character=[main_character, chosen_character][(index+1)%2].id_number,
                    log_type='Dialogue Summarization',
                    log_content=action_event[3])
            self.finished_states[state_UID] = action_index
            if self.test_folder:
                self.save(self.test_folder)

    def update_stage(self, now_round_number):
        '''
        更新阶段
        Input:
            now_round_number: Union[str, int], 当前游戏进行轮数
        Output:
            None
        '''

        for character in self.characters.character_list:
            state_UID = 'NOW_ROUND:%d+ACTION:%s+CHARACTER:%s'%(now_round_number, 'UPDATE', character.id_number)
            if state_UID in self.finished_states: continue
            self.finished_states[state_UID] = []

            candidates_list = '\n'.join(['%s: %s' % (candidate.id_number, candidate.get_short_description())
                                         for candidate in self.characters.get_all_characters() if candidate.id_number != character.id_number])
            candidates_id_number_list = [candidate.id_number for candidate in self.characters.get_all_characters() if candidate.id_number != character.id_number]

            self.logger.gprint(thought='',
                               important_log='important_log',
                               source_character=character.id_number,
                               target_character=character.id_number,
                               log_type='Action stage',
                               log_content='Update stage'
                               )
            # ======================================================================================= #
            # 调用GPT
            # 需要校验
            # ======================================================================================= #
            verify_result = ERROR_RETRY_TIMES
            while verify_result >= 0:
                if verify_result == 0:
                    raise Exception('Log does not meet the requirements.')
                len_relationship_change=len([candidate.id_number for candidate in self.characters.get_all_characters() if candidate.id_number != character.id_number])

                reflect_thought, relationship_change, belief_change, judgement_change = character.update_relation_judgement(
                    all_action_description=self.action_history.get_description(character.id_number,[int(now_round_number)], max_num=ACTIONHISTORY_RETRIEVE_NUM_UPDATE),
                    all_character_description=candidates_list,
                    len_relationship_change=len_relationship_change
                    )

                retry = False
                # 格式校验
                try:
                    if ':' in relationship_change[0]:
                        relationship_change = [int(i.split(':')[-1]) for i in relationship_change]
                    elif '：' in relationship_change[0]:
                        relationship_change = [int(i.split('：')[-1]) for i in relationship_change]
                    else:
                        relationship_change = [int(i) for i in relationship_change]
                except:
                    verify_result -= 1
                    self.logger.gprint('ERROR! Log does not meet the requirements: ', gpt_response=relationship_change, candidates='+5, -6, xxxx')
                    retry = True
                # 格式校验
                if not retry:
                    try:
                        if ':' in belief_change[0]:
                            belief_change = [int(i.split(':')[-1]) for i in belief_change]
                        elif '：' in belief_change[0]:
                            belief_change = [int(i.split('：')[-1]) for i in belief_change]
                        else:
                            belief_change = [int(i) for i in belief_change]
                    except:
                        verify_result -= 1
                        self.logger.gprint('ERROR! Log does not meet the requirements: ', gpt_response=belief_change, candidates='+5, -6, xxxx')
                        retry = True
                # 长度evaluation
                if not retry:
                    new_evaluation_event = [character.id_number,
                                            character.id_number,
                                            '### EVALUATION RELATIONSHIP LENGTH',
                                            'agent response: %s[SEP]ground truth: %s' % (len(relationship_change),
                                                                                       len([candidate.id_number for
                                                                                            candidate in
                                                                                            self.characters.get_all_characters()
                                                                                            if
                                                                                            candidate.id_number != character.id_number]))]
                    action_index = self.new_action_insert(new_evaluation_event, now_round_number)
                    self.finished_states[state_UID].append(action_index)
                    # 长度evaluation
                    new_evaluation_event = [character.id_number,
                                            character.id_number,
                                            '### EVALUATION BELIEF LENGTH',
                                            'agent response: %s[SEP]ground truth: %s' % (len(belief_change),
                                                                                       len(character.belief))]
                    action_index = self.new_action_insert(new_evaluation_event, now_round_number)
                    self.finished_states[state_UID].append(action_index)
                    try:
                        # 值域evaluation
                        new_evaluation_event = [character.id_number,
                                                character.id_number,
                                                '### EVALUATION RELATIONSHIP VALUE',
                                                'agent response: %s[SEP]ground truth: %s' % (str([int(i) for i in relationship_change]),
                                                                                           str([max(min(int(i), MAX_RELATION_SCORE_CHANGE),-MAX_RELATION_SCORE_CHANGE) for i in relationship_change]))]
                    except:
                        # 值域evaluation
                        new_evaluation_event = [character.id_number,
                                                character.id_number,
                                                '### EVALUATION RELATIONSHIP VALUE',
                                                'agent response: %s[SEP]ground truth: %s' % (
                                                str([int(i) for i in relationship_change]),'ERROR FORMAT')]

                    action_index = self.new_action_insert(new_evaluation_event, now_round_number)
                    self.finished_states[state_UID].append(action_index)
                    # 值域evaluation
                    try:
                        new_evaluation_event = [character.id_number,
                                                character.id_number,
                                                '### EVALUATION BELIEF VALUE',
                                                'agent response: %s[SEP]ground truth: %s' % (str([int(i) for i in belief_change]),
                                                                                       str([max(min(int(i), MAX_BELIEF_SCORE_CHANGE),-MAX_BELIEF_SCORE_CHANGE) for i in belief_change]))]
                    except:
                        new_evaluation_event = [character.id_number,
                                                character.id_number,
                                                '### EVALUATION BELIEF VALUE',
                                                'agent response: %s[SEP]ground truth: %s' % (
                                                str([int(i) for i in belief_change]),'ERROR FORMAT')]

                    action_index = self.new_action_insert(new_evaluation_event, now_round_number)
                    self.finished_states[state_UID].append(action_index)
                if retry: continue
                # 对relationship_change进行校验
                # 长度校验
                if not len(relationship_change) == len([candidate.id_number for candidate in self.characters.get_all_characters() if candidate.id_number != character.id_number]):
                    verify_result -= 1
                    self.logger.gprint('ERROR! Log does not meet the requirements: ', gpt_response=relationship_change, candidates='len(relationship_change) == %d != %d'%(len(relationship_change),len([candidate.id_number for candidate in self.characters.get_all_characters() if candidate.id_number != character.id_number])))
                    continue

                # 对Belief_change进行校验
                # 长度校验
                if not len(belief_change) == len(character.belief):
                    verify_result -= 1
                    self.logger.gprint('ERROR! Log does not meet the requirements: ', gpt_response=belief_change, candidates='len(belief_change) == %d'%len(character.belief))
                    continue
                verify_result = -10
            # ======================================================================================= #

            # 更新信念
            for belief, item in zip(character.belief, belief_change):
                character.belief[belief] += item
                character.belief[belief] = max(character.belief[belief], MIN_BELIEF_SCORE)  # 判断最小值
                character.belief[belief] = min(character.belief[belief], MAX_BELIEF_SCORE)  # 判断最大值
                self.logger.gprint(thought='',
                                   important_log='important_log',
                                   source_character=character.id_number,
                                   target_character=belief,
                                   log_type='Belief update',
                                   log_content=character.belief[belief])

            # 更新关系分数
            for target_character_id_number, change_score in zip(candidates_id_number_list, relationship_change):
                if target_character_id_number not in character.relation:
                    character.relation[target_character_id_number] = INITIAL_RELATION_SCORE
                character.relation[target_character_id_number] += change_score
                character.relation[target_character_id_number] = max(character.relation[target_character_id_number],
                                                                     MIN_RELATION_SCORE)  # 判断最小值
                character.relation[target_character_id_number] = min(character.relation[target_character_id_number],
                                                                     MAX_RELATION_SCORE)  # 判断最大值
                self.logger.gprint(thought='',
                                   important_log='important_log',
                                   source_character=character.id_number,
                                   target_character=target_character_id_number,
                                   log_type='Relation update',
                                   log_content=character.relation[target_character_id_number])

            # 更新判断分数
            for source_character_id_number, target_character_N_change_score in judgement_change.items():
                if source_character_id_number not in character.judgement:
                    character.judgement[source_character_id_number] = {}
                for target_character_id_number, change_score in target_character_N_change_score.items():
                    if target_character_id_number not in character.judgement:
                        character.judgement[source_character_id_number][
                            target_character_id_number] = INITIAL_RELATION_SCORE
                        character.judgement[source_character_id_number][target_character_id_number] += change_score

            # 根据关系分数更新支持者
            support_character_id_number = 'None'
            support_relation_score = character.min_support_relation_score - 1
            for target_character_id_number in character.relation:
                relation_score = character.relation[target_character_id_number]
                if relation_score >= character.min_support_relation_score and relation_score > support_relation_score:
                    support_character_id_number = target_character_id_number
                    support_relation_score = relation_score
            self.logger.gprint(thought='',
                               important_log='important_log',
                               source_character=character.id_number,
                               target_character=support_character_id_number,
                               log_type='Support update',
                               log_content=support_character_id_number)
            character.support_character = support_character_id_number

            # 生成新的事件
            new_action = [character.id_number, character.id_number, '### REFLECTION', "A reflection result of %s in Round %d: %s" %(character.id_number, now_round_number, reflect_thought)]
            action_index = self.new_action_insert(new_action, now_round_number)
            self.logger.gprint(thought='',
                               important_log='important_log',
                               source_character=character.id_number,
                               target_character=character.id_number,
                               log_type='Relation status',
                               log_content=character.relation)
            self.logger.gprint(thought='',
                               important_log='important_log',
                               source_character=character.id_number,
                               target_character=character.id_number,
                               log_type='Environment judgement',
                               log_content=character.judgement)
            self.logger.gprint(thought=reflect_thought,
                               important_log='important_log',
                               source_character=character.id_number,
                               target_character=character.id_number,
                               log_type='Reflection result',
                               log_content=reflect_thought)
            # Reflection
            self.finished_states[state_UID].append(action_index)
            if self.test_folder:
                self.save(self.test_folder)
        self.characters.get_influence_for_main_character()

    def succession_settlement(self, whole_information):
        '''
        针对于继承之战的结算，每个角色可以发言一次，然后再进行投票
        Input:
            whole_information: bool, 让Agent知道全局信息还是局部信息？
        Output:
            character_vote_dict: dict 每个角色投票给谁
            character_vote_others: 每个角色除了自己，投票给谁
        '''
        character_vote_dict = {}
        character_vote_others = {}


        candidates = ['%s: %s' % (character.get_id_number(), character.get_short_description()) for character in
                      self.characters.get_all_characters() if character.main_character]
        candidates = '\n'.join(candidates)

        action_history = ''
        background_information = 'Under the condition that the Agent knows only the actions it should know.'

        if whole_information:
            background_information = 'Under the condition that the Agent knows only the actions it should know.'
            action_history = self.action_history.get_description(character_id_number=None, max_num=ACTIONHISTORY_RETRIEVE_NUM_WHOLE_INFORMATION)
        self.logger.gprint(important_log='important_log',
                      source_character='',
                      target_character='',
                      log_type='Stage Change',thought='',
                      log_content='Open Speech Stage')
        # 最终投票前的发言
        for character in self.characters.character_list:
            if not whole_information:
                action_history = self.action_history.get_description(character_id_number=character.id_number, max_num=ACTIONHISTORY_RETRIEVE_NUM_PARTIAL_INFORMATION)

            state_UID = 'NOW_ROUND:%s+ACTION:%s+CHARACTER:%s' % ('SETTELMENT' if not whole_information else 'SETTLEMENT(CHEATING)', 'OPENSPEECHSTAGE', character.id_number)
            if state_UID in self.finished_states: continue
            # ======================================================================================= #
            # 调用GPT
            # 不需要校验
            # ======================================================================================= #
            # 角色发言内容
            speech, reasoning_process = character.speech(action_history, self.rule_setting,
                                                         candidates,
                                                         self.resources.get_description())
            # ======================================================================================= #

            self.logger.gprint(thought = reasoning_process,
                               important_log='important_log',
                               source_character=character.id_number,
                               target_character=character.id_number,
                               log_type='Open Speech',
                               log_content='Settlement: %s，final presentation of character %s: %s' % (background_information, character.id_number, speech))

            new_action = [character.id_number, character.id_number, '### SPEECH_VOTE', '%s And public speech that character %s makes to all the other characters: %s' %
                          (background_information, character.id_number,speech)]
            action_index = self.new_action_insert(new_action, -1)
            # 最终宣讲
            self.finished_states[state_UID] = [action_index]
            if self.test_folder:
                self.save(self.test_folder)
        self.logger.gprint(important_log='important_log',
                      source_character='',
                      target_character='',
                      log_type='Stage Change',thought='',
                      log_content='Vote Stage')
        # 最终投票
        for character in self.characters.character_list:
            if not whole_information:
                action_history = self.action_history.get_description(character_id_number=character.id_number, max_num=ACTIONHISTORY_RETRIEVE_NUM_PARTIAL_INFORMATION)

            state_UID = 'NOW_ROUND:%s+ACTION:%s+CHARACTER:%s' % ('SETTELMENT' if not whole_information else 'SETTLEMENT(CHEATING)', 'VOTE', character.id_number)
            if state_UID in self.finished_states: continue
            # 正常投票
            vote_for_requirement = './prompt/prompt_files/succession_vote_requirement/vote_for_winner.txt'
            # ======================================================================================= #
            # 调用GPT
            # 需要校验
            # ======================================================================================= #
            verify_result = ERROR_RETRY_TIMES
            while verify_result>0:
                action_space, vote_for, reasoning_process = character.vote(vote_for_requirement,
                                          is_file=True,
                                          background_information=action_history,
                                          candidates=candidates)  # 角色投票
                candidates_verification_list = [candidate_id_number for candidate_id_number in self.characters.main_characters_id_number]

                if verify_constrained_action(vote_for[0], candidates_verification_list):
                    vote_for = vote_for[0]
                    verify_result = -10
                elif verify_constrained_action(vote_for[1], candidates_verification_list):
                    vote_for = vote_for[1]
                    verify_result = -10
                else:
                    self.logger.gprint('ERROR! Log does not meet the requirements: ', gpt_response=vote_for, candidates=candidates_verification_list)
                    verify_result -= 1
                if verify_result == 0:
                    raise Exception('Log does not meet the requirements.')

            # 评估事件
            evaluation_event = [character.id_number,
                                character.id_number,
                                '### EVALUATION ACTION SPACE',
                                'agent response: %s[SEP]ground truth: %s' % (str(action_space),
                                                                             str(candidates_verification_list))]
            new_action_index = self.new_action_insert(evaluation_event, -1)
            # ======================================================================================= #
            self.logger.gprint(thought = reasoning_process,
                               important_log='important_log',
                               source_character=character.id_number,
                               target_character=vote_for,
                               log_type='Voting',
                               log_content='Settlement Stage：%s, final voting results of character %s: %s' % (background_information, character.id_number, vote_for))
            character_vote_dict[character.id_number] = vote_for
            new_action = [character.id_number, vote_for, '### VOTE', '%s, and %s votes for %s when it can vote for itself.' %
                          (background_information, character.id_number, vote_for)]
            action_index = self.new_action_insert(new_action, -1)
            # 投票可自己
            self.finished_states[state_UID] = [new_action_index, action_index]
            if self.test_folder:
                self.save(self.test_folder)

        self.logger.gprint(important_log='important_log',
                      source_character='',
                      target_character='',
                      log_type='Stage Change',thought='',
                      log_content='Vote Others Stage')
        for character in self.characters.character_list:
            state_UID = 'NOW_ROUND:%s+ACTION:%s+CHARACTER:%s' % ('SETTELMENT' if not whole_information else 'SETTLEMENT(CHEATING)', 'VOTEOTHER', character.id_number)
            if state_UID in self.finished_states: continue
            candidates_except_self = [
                '%s: %s' % (character_temp.get_id_number(), character_temp.get_short_description())
                for character_temp in self.characters.get_all_characters() if
                (character_temp.get_main_character() and character_temp.id_number != character.id_number)]
            candidates_except_self = '\n'.join(candidates_except_self)
            if not whole_information:
                action_history = self.action_history.get_description(character_id_number=character.id_number,
                                                                     max_num=ACTIONHISTORY_RETRIEVE_NUM_PARTIAL_INFORMATION)
            # 不能投给自己的投票
            vote_for_except_requirement = './prompt/prompt_files/succession_vote_requirement/vote_for_winner_except_self.txt'
            # ======================================================================================= #
            # 调用GPT
            # 需要校验
            # ======================================================================================= #
            verify_result = ERROR_RETRY_TIMES
            while verify_result > 0:
                action_space, vote_for_except_self, reasoning_process = character.vote(vote_for_except_requirement,
                                                      is_file=True,
                                                      background_information=action_history,
                                                      candidates=candidates_except_self)  # 除了自己之外再投票
                candidates_verification_list = [candidate_id_number for candidate_id_number in self.characters.main_characters_id_number if candidate_id_number != character.id_number]
                if verify_constrained_action(vote_for_except_self[0], candidates_verification_list):
                    vote_for_except_self = vote_for_except_self[0]
                    verify_result = -10
                elif verify_constrained_action(vote_for_except_self[1], candidates_verification_list):
                    vote_for_except_self = vote_for_except_self[1]
                    verify_result = -10
                else:
                    self.logger.gprint('ERROR! Log does not meet the requirements: ', gpt_response=vote_for_except_self, candidates=candidates_verification_list)
                    verify_result -= 1
                if verify_result == 0:
                    raise Exception('Log does not meet the requirements.')
            # 评估事件
            evaluation_event = [character.id_number,
                                character.id_number,
                                '### EVALUATION ACTION SPACE',
                                'agent response: %s[SEP]ground truth: %s' % (str(action_space),
                                                                             str(candidates_verification_list))]
            new_action_index = self.new_action_insert(evaluation_event, -1)
            # ======================================================================================= #
            self.logger.gprint(thought = reasoning_process,
                               important_log='important_log',
                               source_character=character.id_number,
                               target_character=vote_for_except_self,
                               log_type='Voting Except Self',
                               log_content='Settlement Stage：%s, final voting result of character %s on the premise that it cannot vote itself: %s' % (background_information, character.id_number, vote_for_except_self))
            character_vote_others[character.id_number] = vote_for_except_self
            new_action = [character.id_number, vote_for_except_self, '### VOTE_OTHERS', '%s, under the restrains of not voting for itself, %s win the game due to the support of %s' %
                          (background_information, vote_for_except_self, character.id_number)]
            action_index = self.new_action_insert(new_action, -1)
            # 投票非自己
            self.finished_states[state_UID] = [new_action_index, action_index]
            if self.test_folder:
                self.save(self.test_folder)
        # return character_vote_dict, character_vote_others

    def settlement_stage(self, whole_information, game_name='Succession'):
        '''
        pass
        '''
        action_history = ''
        background_information = 'Under the condition that the Agent knows only the actions it should know.'
        if whole_information == True:
            # 获得所有的action_history
            background_information = 'Under the condition that the Agent knows only the actions it should know.'
            action_history = self.action_history.get_description(character_id_number=None, max_num=ACTIONHISTORY_RETRIEVE_NUM_PARTIAL_INFORMATION)

        # 每个Agent猜测哪个Agent能够获胜【可选对象是Main Character，投票对象为所有角色】
        agent_guess = {}
        # 对所有主要角色投票 包括自己
        candidates = ['%s: %s' % (character.get_id_number(), character.get_short_description()) for character in
                      self.characters.get_all_characters() if character.get_main_character()]
        candidates = '\n'.join(candidates)

        self.logger.gprint(important_log='important_log',
                      source_character='',
                      target_character='',
                      log_type='Stage Change',thought='',
                      log_content='Guess Stage')
        for character in self.characters.character_list:
            if not whole_information:
                action_history = self.action_history.get_description(character.id_number, max_num=ACTIONHISTORY_RETRIEVE_NUM_PARTIAL_INFORMATION)
            state_UID = 'NOW_ROUND:%s+ACTION:%s+CHARACTER:%s' % ('SETTELMENT' if not whole_information else 'SETTLEMENT(CHEATING)', 'GUESS', character.id_number)
            if state_UID in self.finished_states: continue
            vote_requirement = 'prompt/prompt_files/vote_requirement_4_guess.txt'

            # ======================================================================================= #
            # 调用GPT
            # 需要校验
            # ======================================================================================= #
            # 每个agent都要猜哪个重要角色能赢
            verify_result = ERROR_RETRY_TIMES
            while verify_result > 0:
                action_space, choice, history_summary = character.vote(vote_requirement=vote_requirement,
                                                         is_file=True,
                                                         background_information=action_history,
                                                         candidates=candidates)
                choice = choice[0]
                candidates = [candidate.id_number for candidate in self.characters.get_all_characters()]
                if verify_constrained_action(choice, candidates):
                    verify_result = -10
                else:
                    self.logger.gprint('ERROR! Log does not meet the requirements: ', gpt_response=choice, candidates=candidates)
                    verify_result -= 1
                if verify_result == 0:
                    raise Exception('Log does not meet the requirements.')
            # 评估事件
            evaluation_event = [character.id_number,
                                character.id_number,
                                '### EVALUATION ACTION SPACE',
                                'agent response: %s[SEP]ground truth: %s' % (str(action_space),
                                                                             str(candidates))]
            new_action_index = self.new_action_insert(evaluation_event, -1)
            # ======================================================================================= #

            agent_guess[character.id_number] = [choice, history_summary]
            new_action = [character.id_number, choice, '### GUESS', '%s, %s guesses that %s would win the game.'%(background_information, character.id_number, choice)]
            action_index = self.new_action_insert(new_action, -1)
            self.logger.gprint(thought=history_summary,
                               important_log='important_log',
                               source_character=character.id_number,
                               target_character=choice,
                               log_type='Guess Who Will Win',
                               log_content='Settlement Stage: %s, character %s guesses the important character that eventually wins: %s' % (background_information, character.id_number, choice))
            # 猜测结果
            self.finished_states[state_UID] = [new_action_index, action_index]
            if self.test_folder:
                self.save(self.test_folder)
        # Story-Specific Settlement
        winner = ''
        if game_name == 'Succession':
            self.succession_settlement(whole_information)
            character_vote_dict, character_vote_others = self.succession_get_character_vote_dict()
            # 1. Defender选哪个Attacker，哪个Attacker就赢
            # 2. Defender若选自己，则大家一起投票，谁票多谁赢
            # 3. 先看character_vote_dict，平票时，看character_vote_others
            winner_include_self = succession_winner('C0000', character_vote_dict)
            winner_except_self = succession_winner('C0000', character_vote_others)
            if type(winner_include_self) != list: winner_include_self = [winner_include_self]
            if type(winner_except_self) != list: winner_except_self = [winner_except_self]
            if len(winner_include_self) == 1:
                winner = winner_include_self[0]
            elif len(winner_except_self) == 1:
                winner = winner_except_self[0]
            else:
                winner_list = [i for i in winner_include_self if i in winner_except_self]
                if len(winner_list) == 1:
                    winner = winner_list[0]
                else:
                    winner = ', '.join(winner_list)

            self.logger.gprint(thought='',
                               important_log='important_log',
                               source_character=winner,
                               target_character=winner,
                               log_type='Winner Announcement',
                               log_content='Settlement Stage：%s, character %s wins the game.' % (background_information, winner))
        return winner

    def succession_get_character_vote_dict(self):
        '''
        根据action history得到character_vote和character_vote_others
        '''
        character_vote = {}
        character_vote_others = {}

        for action in self.action_history.get_all_action_history():
            _, source_character, target_character, action_type, event, _ = action.read()
            if action_type == '### VOTE':
                character_vote[source_character] = target_character
            elif action_type == '### VOTE_OTHERS':
                character_vote_others[source_character] = target_character
        return character_vote, character_vote_others


if __name__ == '__main__':
    save_folder = SAVE_FOLDER
    test_folder = TEST_FOLDER
    game_round = GAME_ROUND
    log_dir = LOG_FOLDER
    battle_chat_round = BATTLE_CHAT_ROUND
    collabration_chat_round = COLLABORATION_CHAT_ROUND

    logger = Logger(log_dir)
    sucarena = SucArena(all_round_number=game_round,
                        battle_chat_round=battle_chat_round,
                        collabration_chat_round=collabration_chat_round,
                        save_folder=save_folder,
                        test_folder=test_folder,
                        logger=logger)

    for i in range(game_round):

        logger.gprint(important_log='important_log',
                      source_character='',
                      target_character='',
                      log_type='Turn Change', thought='',
                      log_content='Turn %d' % (i + 1))

        logger.gprint(important_log='important_log',
                      source_character='',
                      target_character='',
                      log_type='Stage Change', thought='',
                      log_content='Confrontation Stage')
        sucarena.compete_stage(i)

        logger.gprint(important_log='important_log',
                      source_character='',
                      target_character='',
                      log_type='Stage Change', thought='',
                      log_content='Cooperation Stage')
        sucarena.collaborate_stage(i)

        logger.gprint(important_log='important_log',
                      source_character='',
                      target_character='',
                      log_type='Stage Change', thought='',
                      log_content='Announcement Stage')
        sucarena.announcement_stage(i)

        logger.gprint(important_log='important_log',
                      source_character='',
                      target_character='',
                      log_type='Stage Change',
                      thought='',
                      log_content='Update Stage')
        sucarena.update_stage(i)

        logger.gprint('Start Saving')
        sucarena.save(test_folder)
        logger.gprint(important_log='important_log',
                      source_character='',
                      target_character='',
                      log_type='Turn End',
                      thought='',
                      log_content='')


    game_name = 'Succession'

    logger.gprint(important_log='important_log',
                  source_character='',
                  target_character='',
                  log_type='Turn Change',
                  thought='',
                  log_content='Settlement Turn')
    local_information_winner = sucarena.settlement_stage(whole_information=False, game_name=game_name)
    logger.gprint(important_log='important_log',
                  source_character='',
                  target_character='',
                  log_type='Turn End',
                  thought='',
                  log_content='')

    logger.gprint(important_log='important_log',
                  source_character='',
                  target_character='',
                  log_type='Turn Change',
                  thought='',
                  log_content='Settlement Turn (Cheating)')
    whole_information_winner = sucarena.settlement_stage(whole_information=True, game_name=game_name)
    logger.gprint(important_log='important_log',
                  source_character='',
                  target_character='',
                  log_type='Turn End',
                  thought='',
                  log_content='')


    logger.gprint('Start Saving')
    # sucarena.new_action_insert(['empty_action','empty_action','empty_action','empty_action'], i+1)
    sucarena.save(test_folder)
    logger.gprint('Game ends successfully')


