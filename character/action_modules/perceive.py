from prompt.gpt_structure import generate_prompt, generate_with_response_parser, create_prompt_input
import sys


def run_perceive(self_character_id_number: str,
                self_character_description: str, 
                rule_setting: str, 
                all_resource_description: str, 
                action_history_description: str,
                chat_round_number,
                support_character,
                engine='gpt4',logger=None):
    # 如果是人的话，不需要perceive
    if engine == 'human':
        return "这是人类，不需要Perceive"

    gpt_param = {"temperature": 0.5, "top_p": 1, "stream": False,
                 "frequency_penalty": 0, "presence_penalty": 0, "stop": None}

    if not support_character:
        support_character = '你目前不支持任何其他角色，所以你只考虑自己的利益。'
    prompt_template = "prompt_files/prompt_4_perceive.txt"
    prompt_input = create_prompt_input(self_character_id_number,
                                       self_character_description,
                                       rule_setting,
                                       all_resource_description,
                                       action_history_description,
                                       chat_round_number,
                                       support_character)
    prompt = generate_prompt(prompt_input, prompt_template, fn_name=sys._getframe().f_code.co_name)


    environment_summary = generate_with_response_parser(prompt, gpt_param=gpt_param, engine=engine, logger=logger,func_name='run_perceive')
 
    return environment_summary