from .resource_class import Resource
import os

class AllResource:
    def __init__(self, save_folder=None)->None:
        '''
        初始化AllResource类
        Input:
            save_folder: str
        Output:
            None
        '''
        self.resource_dict = {}
        self.resource_list = []
        self.initialize(save_folder)

    def initialize(self, save_folder)->int:
        '''
        从save_folder中读取AllResource信息
        Input:
            save_folder: str
        Output:
            success_number: int, 成功读取了多少resource
        '''
        success_number = 0
        for file in os.listdir(save_folder):
            resource_file = os.path.join(save_folder, file)
            resource = Resource(saved_folder=resource_file)
            self.append(resource)
            success_number += 1
        return success_number

    def append(self, new_resource: Resource)->None:
        '''
        将new_resource加入AllResource
        Input:
            new_resource: Resource,
        Output:
            None
        '''
        self.resource_dict[new_resource.id_number] = new_resource
        self.resource_list.append(new_resource)

    def get_resource_by_id_number(self, id_number)->Resource:
        '''
        根据ID Number获得资源
        Input:
            id_number: str
        Output:
            resource: Resource
        '''
        return self.resource_dict[id_number]

    def get_all_resource(self)->list:
        '''
        获得所有的资源列表
        Input:
            None
        Output:
            resource_list: list, [Resource]
        '''
        return self.resource_list

    def get_description(self)->str:
        '''
        获得所有资源的描述
        Input:
            None
        Output:
            description: str, 所有资源的描述
        '''
        description = ''
        for resource in self.get_all_resource():
            description += resource.get_description() + '\n'
        return description.strip()