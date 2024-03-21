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
from character.action_modules.groupchat import run_groupchat


class Character:
    def __init__(self, id_number=None, main_character=False, save_file_folder=None, logger: Logger = None) -> None:
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
        self.influence = influence

    def get_influence(self) -> int:
        return self.influence

    def get_objective(self) -> str:
        return self.objective

    def get_support_character(self) -> str:
        if self.support_character:
            return self.support_character
        else:
            return 'Nobody, you support yourself for the moment.'
    def get_id_number(self) -> str:
        return self.id_number

    def get_main_character(self) -> bool:
        return self.main_character

    def get_relationship(self) -> dict:
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
        if not save_file_folder.endswith('.json'):
            save_file_folder = os.path.join(save_file_folder, self.id_number + '.json')
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
        all_belief = ''
        for belief in self.belief:
            all_belief += belief+' : '+str(self.belief[belief]) + '\n'
        return all_belief

    def get_all_belief_number(self) -> int:
        return len(self.belief)

    def get_short_description(self) -> str:
        # description = 'This role: %s.'%self.id_number
        description = self.background
        return description

    def update_relation_judgement(self, all_action_description: str,
                                  all_character_description: str,
                                  len_relationship_change: int):
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

    def groupchat(self, action_history_desc, rule_setting, candidates, resources):
        speech, reasoning_process = run_groupchat(self.id_number,
                                               self.get_self_description(),
                                               action_history_desc,
                                               candidates,
                                               resources,
                                               rule_setting,
                                               self.get_support_character(),
                                               engine=self.engine,
                                               logger=self.logger
                                               )
        return speech, reasoning_process

    def groupchat_round(self, action_history_desc, candidates, resources, rule_setting, round_description):
        speech, reasoning_process = run_groupchat(self.id_number,
                                               self.get_self_description(),
                                               action_history_desc,
                                               candidates,
                                               resources,
                                               rule_setting + '\n' + round_description,
                                               self.get_support_character(),
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
