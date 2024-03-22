import json
import os
import random
from collections import defaultdict
from config import *

from logger_class import Logger
from character.action_modules.summarization import run_summarization
from character.action_modules.choose import run_choose
from character.action_modules.facechat import run_facechat
from character.action_modules.perceive import run_perceive
from character.action_modules.reflection import run_reflect
from character.action_modules.vote import run_vote
from character.action_modules.groupchat import run_groupchat, run_speech


class Character:
    def __init__(self, id_number=None, main_character=False, save_file_folder=None, logger: Logger = None) -> None:
        '''
        初始化Character类
        Input:
            id_number: str,
            main_character: bool,
            save_file_folder: str, 如果输入的话，就自动读取这个文件or文件夹下的角色信息
            logger: Logger, 如果输入，则将该角色的数据输出到logger里
        Output:
            None
        '''
        if logger:
            self.logger = logger
        else:
            self.logger = None
        self.main_character = main_character
        self.influence = 0
        self.support_character = ''  # 存放id_number
        self.objective = ''
        self.name = ''
        self.scratch = ''
        self.background = ''
        self.engine = ''
        self.belief = {}
        self.judgement = defaultdict(lambda: INITIAL_RELATION_SCORE)
        self.relation = defaultdict(lambda: INITIAL_RELATION_SCORE)
        self.id_number = ''
        if id_number:
            self.id_number = id_number
        if save_file_folder:
            self.load(save_file_folder)

    def give_influence(self, influence: int) -> None:
        '''
        赋予角色的影响力数值
        Input:
            influence: int
        Output:
            None
        '''
        self.influence = influence

    def get_influence(self) -> int:
        '''
        得到角色的影响力数值
        Input:
            None
        Output:
            influence: int
        '''
        return self.influence

    def get_objective(self) -> str:
        '''
        得到角色的目标
        Input:
            None
        Output:
            objective: str
        '''
        return self.objective

    def get_support_character(self) -> str:
        '''
        获得该角色所支持的角色
        Input:
            None
        Output:
            support_character: str
        '''
        if self.support_character:
            return self.support_character
        else:
            return 'Nobody, you support yourself for the moment.'
    def get_id_number(self) -> str:
        '''
        获得角色的ID Number
        Input:
            None
        Output:
            ID Number: str
        '''
        return self.id_number

    def get_main_character(self) -> bool:
        '''
        输出角色是否为主要角色
        Input:
            None
        Output:
            is main character: bool
        '''
        return self.main_character

    def get_relationship(self) -> dict:
        '''
        获得self角色的关系
        Input:
            None
        Output:
            self.relation: dict
        '''
        return self.relation
    def summarize(self, environment_description, chat_history):
        number_of_action_history, thought, new_action_history = run_summarization(self.id_number,
                                                                             self.get_self_description(),
                                                                             environment_description,
                                                                             chat_history,
                                                                             engine=self.engine,
                                                                             logger=self.logger)
        return number_of_action_history, thought, new_action_history

    def load(self, save_file_folder) -> None:
        '''
        从文件中读取角色信息
        Input:
            save_file_folder: str, 保存的json文件or文件夹
        Output:
            None
        '''

        # 如果是个文件夹
        if not save_file_folder.endswith('.json'):
            save_file_folder = os.path.join(save_file_folder, self.id_number + '.json')

        # 确定文件
        save_file = save_file_folder
        json_data = json.load(open(save_file, encoding='utf-8'))

        self.name = json_data['name']
        if not self.id_number:
            self.id_number = json_data['id_name']
        self.main_character = True if json_data['main_character'] == 'True' else False
        self.support_character = json_data['support_character']
        self.objective = json_data['objective']
        self.scratch = json_data['scratch']
        self.background = json_data['background']
        self.engine = json_data['engine']
        self.belief = json_data['belief']
        self.judgement = json_data['judgement']
        self.relation = json_data['relation']
        self.portrait = json_data['portrait']
        self.small_portrait = json_data['small_portrait']
        self.min_support_relation_score = MIN_SUPPORT_RELATION_SCORE

    def save(self, save_file_folder) -> None:
        '''
        将角色信息保存到save_file_folder
        Input:
            save_file_folder: str, 角色信息保存地址
        Output:
            None
        '''
        if not save_file_folder.endswith('.json'):
            if not os.path.exists(save_file_folder):
                os.makedirs(save_file_folder)
            save_file_folder = os.path.join(save_file_folder, self.id_number + '.json')
        save_file = save_file_folder
        json_data = {'name': self.name,
                     'id_name': self.id_number,
                     'main_character': 'True' if self.main_character else 'False',
                     'support_character': self.support_character,
                     'objective': self.objective,
                     'scratch': self.scratch,
                     'background': self.background,
                     'engine': self.engine,
                     'belief': self.belief,
                     'judgement': self.judgement,
                     'portrait': self.portrait,
                     'small_portrait': self.small_portrait,
                     'relation': self.relation}
        open(save_file, 'w', encoding='utf-8').write(json.dumps(json_data, ensure_ascii=False, indent=4))

    def get_self_description(self) -> str:
        '''
        生成一段自我介绍——这段description是Character脑中的对白，所以可以用第二人称呼
        Input:
            None
        Output:
            description: str, 只给自己看的描述
        '''
        # description = self.name

        description = 'You: %s.\n' % self.id_number
        description += 'Your goal: %s\n' % self.objective
        if not self.main_character:
            if self.support_character:
                description += 'You are currently supporting %s in achieving his/her goals.\n' % (
                    self.support_character)
            else:
                description += 'You are not supporting anyone at the moment.\n'
        description += 'Here is your role setting: %s\n' % self.scratch
        description += 'In the public eye, you are: %s\n' % self.background
        if self.main_character:
            description += 'Your thought: %s' % self.get_main_belif()

        return description.strip()

    def get_main_belif(self) -> str:
        '''
        获得分数最高的信念
        Input:
            None
        Output:
            main_belif: str
        '''
        main_belief = []
        main_belief_score = 0
        for belief, score in self.belief.items():
            if score > main_belief_score:
                main_belief_score = score
                main_belief = []

            if score == main_belief_score:
                # 把句号去掉
                main_belief.append(belief.strip('。'))
        return '; '.join(main_belief) + '. '

    def get_all_belief(self) -> str:
        '''
        获得角色的所有信念
        Input:
            None
        Output:
            all_belief: str
        '''
        all_belief = ''
        for belief in self.belief:
            all_belief += belief+' : '+str(self.belief[belief]) + '\n'
        return all_belief

    def get_all_belief_number(self) -> int:
        return len(self.belief)

    def get_short_description(self) -> str:
        '''
        生成一段简短的自我介绍，暂时没用
        Input:
            None
        Output:
            description: str, 别人能够看到的一行内的简短描述
        '''
        # description = 'This role: %s.'%self.id_number
        description = self.background
        return description

    def update_relation_judgement(self, all_action_description: str,
                                  all_character_description: str,
                                  len_relationship_change: int):
        '''
        Input:
            all_action_description: str, self角色能看到的所有行为
            all_character_description: str, self角色能看到的所有角色的描述信息
        Output:
            reflect_thought, str
            relationship_change: list
            belief_change: list
            judgement_change: dict
        '''
        change_case = [random.randint(-10, 10) for i in range(100)]
        change_case = ['+%d' % i if i > 0 else str(i) for i in change_case]
        case_of_relationship_change = ', '.join(change_case[:int(len_relationship_change)])
        case_of_belief_change = ', '.join(change_case[:self.get_all_belief_number()])
        reflect_thought, relationship_change, belief_change, judgement_change = run_reflect(self.id_number,
                                                                                           self.get_self_description(),
                                                                                           self.get_all_belief(),
                                                                                           all_action_description,
                                                                                           all_character_description,
                                                                                           str(len_relationship_change),
                                                                                           str(self.get_all_belief_number()),
                                                                                           case_of_relationship_change,
                                                                                           case_of_belief_change,
                                                                                           engine=self.engine,
                                                                                           logger=self.logger)
        return reflect_thought, relationship_change, belief_change, judgement_change

    def speech(self, action_history_desc, candidates, resources):
        '''
        让角色最终发言
        '''
        speech, reasoning_process = run_speech(self.id_number,
                                               self.get_self_description(),
                                               action_history_desc,
                                               candidates,
                                               resources,
                                               self.get_support_character(),
                                               engine=self.engine,
                                               logger=self.logger
                                               )
        return speech, reasoning_process

    def groupchat(self, action_history_desc, candidates, resources, round_description):
        '''
        群聊
        '''
        speech, reasoning_process = run_groupchat(self.id_number,
                                               self.get_self_description(),
                                               action_history_description=action_history_desc,
                                               candidates_description=candidates,
                                               resources=resources,
                                               round_description=round_description,
                                               support_character=self.get_support_character(),
                                               engine=self.engine,
                                               logger=self.logger
                                               )
        return speech, reasoning_process

    def choose(self,
            environment_summary: str,
            round_description: str,
            action_history_description: str,
            candidates_description: str,
            chat_round_num: int,
            requirement_list: list=None):
        '''
        输入环境，根据是否处于竞争阶段，选择对话的对象
        Input:
            environment_summary: str, 对于环境的总结
            round_description: str, 对于当前轮数的描述
            action_history_description: str, 行动历史
            candidates_description: 对于所有候选者的描述
        Output:
            chosen_candidate: str, 被选中要跟self角色对话的另一个角色的id_number
        '''
        action_history, thought, plan, candidate = run_choose(self.id_number,
                                                           self.get_self_description(),
                                                           environment_summary,
                                                           round_description,
                                                           action_history_description,
                                                           candidates_description,
                                                           str(chat_round_num),
                                                           engine=self.engine,
                                                           requirement_list=requirement_list,
                                                           logger=self.logger)
        return action_history, thought, plan, candidate

    def get_belief_and_score(self):
        '''
        belief + score
        Input:
            None
        Output:
            belief_score_dict: dict, belief -> score
        '''
        belief_score_dict = {}
        for belief, score in self.belief.items():
            belief_score_dict[belief] = score
        return belief_score_dict

    def vote(self,
             vote_requirement,
             is_file: bool,
             background_information: str,
             candidates: str,
             requirement_list: list=None):
        '''
        根据投票要求、背景信息、所选角色，来进行结算阶段的投票
        Input:
            vote_requirement: 投票要求，这里应该会设置为一个文件
            background_information:
            candidates:
        Output:
            choice:
            reasoning_process:
        '''
        if is_file:
            vote_requirement = \
            open(vote_requirement, encoding='utf-8').read().split('<commentblockmarker>###</commentblockmarker>')[
                -1].strip()
        action_space, choice, reasoning_process = run_vote(self.id_number,
                                                           self.get_self_description(),
                                                           '\n'.join(['%s: %s' % (belief, score) for belief, score in
                                                                      self.get_belief_and_score().items()]),
                                                           vote_requirement,
                                                           background_information,
                                                           candidates,
                                                           self.get_support_character(),
                                                           engine=self.engine,
                                                           requirement_list=requirement_list,
                                                           logger=self.logger)
        return action_space, choice, reasoning_process

    def facechat(self,
                 target_candidate_id_number: str,
                 target_character_description: str,
                 environment_description: str,
                 action_history_description: str,
                 chat_history: str,
                 plan: str = None):
        '''
        和target_candidate_id_number讲话
        Input:
            target_candidate_id_number: str
            target_character_description: str
            environment_description: str
            action_history_description: str
            chat_history: str
        Output:
            new_action_history: list
        '''
        if not plan:
            plan = '你没什么计划，请根据你的角色设定和你的目标进行回复即可。'
        number_of_action_history, thought, new_action_history = run_facechat(self.id_number,
                                                                             target_candidate_id_number,
                                                                             self.get_self_description(),
                                                                             target_character_description,
                                                                             environment_description,
                                                                             action_history_description,
                                                                             chat_history,
                                                                             plan,
                                                                             engine=self.engine,
                                                                             logger=self.logger)
        return number_of_action_history, thought, new_action_history

    def perceive(self, rule_setting: str, all_resource_description: str, action_history_description: str, chat_round_number) -> str:
        '''
        输入自己的性格，输入环境，输出对于环境的总结，以及自己的思考方案
        Input:
            rule_setting: str,
            all_resource_description: str,
            action_history_description: str,
        Output:
            environment_description: str, 环境描述的总结
        '''
        environment_description = run_perceive(self.id_number,
                                               self.get_self_description(),
                                               rule_setting,
                                               all_resource_description,
                                               action_history_description,
                                               chat_round_number=chat_round_number,
                                               support_character=self.get_support_character(),
                                               engine=self.engine,
                                               logger=self.logger)
        return environment_description
