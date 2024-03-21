from prompt.gpt_structure import generate_prompt, generate_with_response_parser, create_prompt_input
import sys


def run_facechat(source_character_id_number: str,
                target_character_id_number: str,
                source_character_description:str,
                target_character_description: str,
                environment_description: str,
                action_history_description: str, 
                chat_history: str,
                plan: str,
                engine='gpt4',logger=None):
    gpt_param = {"temperature": 0.5, "top_p": 1, "stream": False,
                 "frequency_penalty": 0, "presence_penalty": 0, "stop": None}

    prompt_template = "prompt_files/prompt_4_facechat.txt"
    # prompt_template = "prompt_files/prompt_wo_thinking/prompt_4_converse_wo_thinking.txt"
    prompt_input = create_prompt_input(source_character_id_number,
                                        target_character_id_number,
                                        source_character_description,
                                        target_character_description,
                                        environment_description,
                                        action_history_description,
                                        chat_history,
                                        plan)
    prompt = generate_prompt(prompt_input, prompt_template, fn_name=sys._getframe().f_code.co_name)

    def parse_output(gpt_response):
        # print(gpt_response)

        # thought = re.search(r"### Reasoning Process:(.*)### Response:", gpt_response).group(1).strip()
        number_of_action_history = gpt_response.split('### Number of Action History:')[-1].split('### Reasoning Process')[0].strip()
        thought = gpt_response.split("### Reasoning Process:")[-1].split("### Response:")[0].strip()
        response = gpt_response.split('### Response:')[-1].strip()
        return number_of_action_history, thought, response

    if engine == 'human':
        number_of_action_history='[SKIP]'
        thought = '这个是人类，不需要thought'
        human_prompt = '你作为%s,%s\n和%s,%s\n已经发生了的对话内容：\n%s\n请输入你想说的话：\n' % (source_character_id_number,
                                                                                                                    source_character_description,
                                                                                                                    target_character_id_number,
                                                                                                                    target_character_description,
                                                                                                                    chat_history)
        logger.gprint(human_prompt,
                      thought=human_prompt,
                      important_log='important_log',
                      source_character='',
                      target_character='',
                      log_type='Human Speaking',
                      log_content=human_prompt)
        response = generate_with_response_parser(human_prompt,
                                                  engine=engine,
                                                  logger=logger,
                                                 func_name='human_converse')

        logger.gprint(human_prompt,
                      thought=human_prompt,
                      important_log='important_log',
                      source_character='',
                      target_character='',
                      log_type='Human Speaking Result',
                      log_content=response)
    else:
        number_of_action_history, thought, response = generate_with_response_parser(prompt, gpt_param=gpt_param, parser_fn=parse_output, engine=engine, logger=logger,func_name='run_converse')
        response = response.replace('\n','')
    action_event = [source_character_id_number, 
                    target_character_id_number, 
                    '### SAY',
                    '%s say to %s: %s' % (source_character_id_number, target_character_id_number, response)]
    return number_of_action_history, thought, action_event
