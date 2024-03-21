from prompt.gpt_structure import generate_prompt, generate_with_response_parser, create_prompt_input
import sys
import re
from config import *

def run_reflect(self_id_number:str,
               self_description:str,
               self_belief_description:str,
               all_action_description:str,
               all_character_description:str,
               len_relationship_change:str,
               len_belief_change:str,
               case_of_relationship_change:str,
               case_of_belief_change:str,
               engine='gpt4',logger=None):
    gpt_param = {"temperature": 0.5, "top_p": 1, "stream": False,
                 "frequency_penalty": 0, "presence_penalty": 0, "stop": None}

    prompt_template = "prompt_files/prompt_4_reflect.txt"
    prompt_input = create_prompt_input(self_id_number,
                                       self_description,
                                       self_belief_description,
                                       all_action_description,
                                       all_character_description,
                                       len_relationship_change,
                                       len_belief_change,
                                       MAX_BELIEF_SCORE_CHANGE,
                                       MAX_RELATION_SCORE_CHANGE,
                                       case_of_relationship_change,
                                       case_of_belief_change
                                       )
    prompt = generate_prompt(prompt_input, prompt_template, fn_name=sys._getframe().f_code.co_name)

    def parse_output(gpt_response):
        ret = {}
        try:
            reflect_result = gpt_response.split('### Reflect Result')[-1].split('### Relationship Change:')[0].strip()
            relationship_change = re.search(r"### Relationship Change:(.*)\n", gpt_response).group(1).strip().split(',')
            belief_change = re.search(r"### Belief Change:(.*)", gpt_response).group(1).strip().split(',')
            judgement_change = {}
        except:
            print('ERROR\nERROR\n',gpt_response,'\nERROR\nERROR\n')
            raise Exception("[Error]: GPT response parse error")
        return reflect_result, relationship_change, belief_change, judgement_change

    if engine == 'human':  # 人类的update不重要
        reflect_result = 'This is human, no need to reflect'
        relationship_change = ['0' for i in range(int(len_relationship_change))]
        belief_change = ['0' for i in range(int(len_belief_change))]
        judgement_change = {}
    else:
        verify_result = ERROR_RETRY_TIMES
        correct = False
        while(verify_result>0):
            try:
                reflect_result, relationship_change, belief_change, judgement_change = generate_with_response_parser(prompt, gpt_param=gpt_param, parser_fn=parse_output, engine=engine, logger=logger,func_name='run_update')
                verify_result = 0
                correct = True
            except:
                verify_result -= 1
        if not correct: raise  Exception("[Error]: GPT response parse error")
        reflect_result = reflect_result.replace('\n', '')
    return 'No Reflection', relationship_change, belief_change, judgement_change



