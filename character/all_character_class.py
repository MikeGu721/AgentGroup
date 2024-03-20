from character.character_class import Character
import os
from config import *
from collections import defaultdict


class AllCharacter:
    def __init__(self, save_folder=None, logger=None) -> None:
        '''
        初始化AllCharacter类
        Input:
            save_folder: str, 存档地址
            logger: Logger, 已有的logger
        Output:
            None
        '''
        self.character_dict = {}
        self.character_list = []

        self.main_characters_id_number = []

        self.initial_relation_score = INITIAL_RELATION_SCORE
        self.relationships = defaultdict(dict)

        self.initial_influence_score = int(INITIAL_INFLUENCE_SCORE)
        self.main_character_influence = defaultdict(lambda: self.initial_influence_score)

        if save_folder:
            self.initialize(save_folder, logger=logger)
            self.get_influence_for_main_character()

    def get_influence_for_main_character(self) -> dict:
        '''
        获得所有主要角色的影响力大小
        Input:
            None
        Output:
            main character influence: dict (main_character_id_number (str) -> main_character_influence (int))
        '''
        # 重建每个main character的influence score
        for character in self.character_list:
            if character.main_character:
                self.main_character_influence[character.id_number] = int(self.initial_influence_score)

        # 计算每个main character的influence score
        for character in self.character_list:
            if character.main_character: continue
            support_character_id_number = character.support_character
            support_character = self.get_character_by_id(support_character_id_number)
            if support_character.main_character:
                self.main_character_influence[support_character_id_number] += int(character.get_influence())

        return self.main_character_influence

    def initialize(self, save_folder, logger=None) -> int:
        '''
        初始化AllCharacter里的所有内容
        Input:
            save_folder: str, 存档地址
            logger: Logger
        Output:
            success_number: 初始化了多少个角色
        '''
        success_number = 0
        for file in os.listdir(save_folder):
            character_file = os.path.join(save_folder, file)
            character = Character(save_file_folder=character_file, logger=logger)
            self.append(character)
            success_number += 1

            # 如果是主要角色
            if character.get_main_character():
                self.main_characters_id_number.append(character.get_id_number())
                self.main_character_influence[character.get_id_number()] = 0

            # 登记每个角色和其他所有角色的关系
            relation_items = character.get_relationship().items()
            for target_character_id_number, relation_score in relation_items:
                if target_character_id_number not in self.relationships[character.get_id_number()]:
                    self.relationships[character.get_id_number()][target_character_id_number] = INITIAL_RELATION_SCORE
                self.relationships[character.get_id_number()][target_character_id_number] = relation_score
        return success_number

    def get_main_character_influence(self) -> dict:
        '''
        返回排序好的主要角色影响力字典  TODO: 还没排序
        Input:
            None
        Output:
            排序好的main_character_influence
        '''
        return self.main_character_influence

    def append(self, character: Character) -> None:
        '''
        加入新角色
        Input:
            character: Character
        Output:
            None
        '''
        self.character_dict[character.get_id_number()] = character
        self.character_list.append(character)

    def get_character_by_index(self, idx: int) -> Character:
        '''
        用索引查character
        Input:
            index: int, Character的index
        Output:
            character: Character
        '''
        return self.character_list[idx]

    def get_character_by_id(self, id_number: str) -> Character:
        '''
        通过id找角色
        Input:
            character_id_number: str
        Output:
            character: Character
        '''
        return self.character_dict.get(id_number, Character())

    def get_all_characters(self, except_for:str=None) -> list:
        '''
        获得所有角色
        Input:
            except_for: str, 某个角色的id_number
        Output:
            all_character_list: list
        '''
        if except_for:
            return_list = [i for i in self.character_list if i != except_for]
            if len(return_list) != len(self.character_list):
                print('选择角色时的candidate list已去除',except_for)
            else:
                print('选择角色时的candidate list中未找到',except_for)
            return return_list
        return self.character_list

    def __item__(self, item) -> Character:
        '''
        我也不知道我为啥写了这个函数，也不知道要干嘛，留着吧
        '''
        return self.get_character_by_index[item]

    def get_characters_description_except_some(self, except_characters: list) -> str:
        '''
        返回除了except_characters的其他所有characters的描述
        Input:
            except_characters: list (character_id_number (str))
        Output:
            all_character_description: str, 所有角色的描述
        '''
        all_character_description = ''
        for character in self.character_list:
            if character.id_number in except_characters: continue
            all_character_description += 'Role ID Number：%s。\n' % character.id_number
        return all_character_description.strip()
