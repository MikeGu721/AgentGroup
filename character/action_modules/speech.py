from prompt.gpt_structure import generate_prompt, generate_with_response_parser, create_prompt_input
import sys
import re


def run_speech(character_id_number,
               character_description,
               action_history_description,
               candidates_description,
               resources,
               rule_setting,
               support_character,
               engine='gpt4',logger=None):
    gpt_param = {"temperature": 0.3, "top_p": 1, "stream": False,
                 "frequency_penalty": 0, "presence_penalty": 0, "stop": None}

    prompt_template = "prompt_files/prompt_4_speech.txt"
    prompt_template = "prompt_files/prompt_wo_thinking/prompt_4_speech_wo_thinking.txt"
    prompt_input = create_prompt_input(character_id_number,
                                       character_description,
                                       action_history_description,
                                       candidates_description,
                                       resources,
                                       support_character,
                                       rule_setting)
    prompt = generate_prompt(prompt_input, prompt_template, fn_name=sys._getframe().f_code.co_name)

    def parse_output(gpt_response):
        try:
            # reasoning_process = re.search(r"### Reasoning Process:(.*)### SPEECH", gpt_response).group(1).strip()
            # speech = re.search(r"### SPEECH:(.*)", gpt_response).group(1).strip().split(',')
            reasoning_process = gpt_response.split('### Reasoning Process:')[-1].split('### Speech:')[0].strip()
            speech = gpt_response.split('### Speech:')[-1]
        except:
            print('ERROR\nERROR\n', gpt_response, '\nERROR\nERROR\n')
            raise Exception("[Error]: GPT response parse error")
        return speech, reasoning_process

    if engine == 'human':

        human_prompt = '你作为%s，%s\n请你对所有其他角色发表一些宣言：\n' % (
                                                            character_id_number,
                                                            character_description)
        logger.gprint(human_prompt,
                      thought=human_prompt,
                      important_log='important_log',
                      source_character='',
                      target_character='',
                      log_type='Human Speaking',
                      log_content=human_prompt)

        reasoning_process = '这个是人类，不需要推理过程'
        speech = generate_with_response_parser(human_prompt, engine=engine, logger=logger,func_name='human_speech')


        logger.gprint(human_prompt,
                      thought=human_prompt,
                      important_log='important_log',
                      source_character='',
                      target_character='',
                      log_type='Human Speaking Result',
                      log_content=speech)
    else:
        speech, reasoning_process = generate_with_response_parser(prompt, gpt_param=gpt_param, parser_fn=parse_output, engine=engine,
                                                  logger=logger,func_name='run_speech')
    speech = speech.replace('\n', '')
    return speech, reasoning_process

def run_speech_round(character_id_number,
               character_description,
               action_history_description,
               candidates_description,
               resources,
               rule_setting,
               round_description,
               support_character,
               engine='gpt4',
               logger=None):
    gpt_param = {"temperature": 0.3, "top_p": 1, "stream": False,
                 "frequency_penalty": 0, "presence_penalty": 0, "stop": None}

    if not support_character:
        support_character = '你目前不支持任何其他角色，所以你只考虑自己的利益。'
    prompt_template = "prompt_files/prompt_4_speech_round.txt"
    prompt_input = create_prompt_input(character_id_number,
                                       character_description,
                                       action_history_description,
                                       candidates_description,
                                       resources,
                                       rule_setting,
                                       round_description,
                                       support_character)
    prompt = generate_prompt(prompt_input, prompt_template, fn_name=sys._getframe().f_code.co_name)

    def parse_output(gpt_response):
        try:
            reasoning_process = re.search(r"### Reasoning Process:(.*)\n", gpt_response).group(1).strip()
            # speech = re.search(r"### SPEECH:(.*)", gpt_response).group(1).strip().split(',')
            speech = gpt_response.split('### SPEECH:')[-1]
        except:
            print('ERROR\nERROR\n', gpt_response, '\nERROR\nERROR\n')
            raise Exception("[Error]: GPT response parse error")
        return speech, reasoning_process

    if engine == 'human':
        reasoning_process = '这个是人类，不需要推理过程'
        speech = generate_with_response_parser('你作为%s，请你对所有其他角色发表一些宣言：\n' % (character_id_number),
                                               engine=engine, logger=logger,func_name='human_speech_round')
    else:
        speech, reasoning_process = generate_with_response_parser(prompt, gpt_param=gpt_param, parser_fn=parse_output, engine=engine,
                                                  logger=logger,func_name='run_speech_round')
    speech = speech.replace('\n', '')
    return speech, reasoning_process