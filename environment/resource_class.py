import json
import os


class Resource:
    def __init__(self, id_number=None, saved_folder=None)->None:
        '''
        初始化Resource类
        Input:
            id_number: str, 赋予一个id_number
            saved_folder: str, resource存放地址
        Output:
            None
        '''
        if id_number:
            self.id_number = id_number
        
        if saved_folder:
            self.saved_folder = saved_folder
            self.load(saved_folder)
        
        self.name = ''
        self.description = ''
        self.influence = ''
        self.owner = ''
        self.topic = []

        if saved_folder: self.load(saved_folder)
    
    def load(self, save_file_folder)->None:
        '''
        从save_file_folder文件 or 文件夹中读取资源
        Input:
            save_file_folder: str,
        Output:
            None
        '''
        # 如果是个文件夹
        if not save_file_folder.endswith('.json'):
            save_file_folder = os.path.join(save_file_folder, str(self.id_number) + '.json')

        # 准备好json文件
        save_file = save_file_folder
        json_data = json.load(open(save_file, encoding='utf-8'))
        self.name = json_data['name']
        self.id_number = json_data['id_number']
        self.description = json_data['description']
        self.influence = int(json_data['influence'])
        self.owner = json_data['owner']
        self.topic = json_data['topic'].split('[TOPIC_SEP]')

    def save(self, save_file_folder)->None:
        '''
        将resource保存到文件
        Input:
            save_file_folder: str,
        Output:
            None
        '''
        if not save_file_folder.endswith('.json'):
            if not os.path.exists(save_file_folder):
                os.makedirs(save_file_folder)
            save_file_folder = os.path.join(save_file_folder, str(self.id_number) + '.json')
        save_file = save_file_folder
        json_data = {'name': self.name,
                     'id_number': self.id_number,
                     'description': self.description,
                     'influence': self.influence,
                     'owner': self.owner,
                     'topic': '[TOPIC_SEP]'.join(self.topic)}
        open(save_file, 'w', encoding='utf-8').write(json.dumps(json_data, indent=4, ensure_ascii=False))

    def get_description(self):
        '''
        获得这个资源的描述（大家都可见）
        Input:
            None
        Output:
            description: str,
        '''
        # topic_text = ', '.join(self.topic)
        # description_str = f'{self.id_number}, which has {self.influence} social influence score, and is owned by {self.owner}. People can go there for {topic_text}. {self.description}'
        description = ''
        description += 'Institution ID Number: %s;' % self.id_number
        description += 'Influence of Institution: %s;' % str(self.influence)
        description += 'Owner of Institution: %s (Role ID Number);' % self.owner
        description += 'Description of Institution: %s;' % self.description
        description += 'Topics that can be considered in all roles related to them: %s\n' % ', '.join(self.topic)
        return description.strip()
