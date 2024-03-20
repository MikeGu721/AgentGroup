from prompt.gpt_structure import generate_prompt, generate_with_response_parser, create_prompt_input
import sys


def run_vote(source_character_id_number: str,
             source_character_description: str,
             self_belief_description: str,
             vote_requirement: str,
             background_information: str,
             candidates: str,
             support_character: str,
             engine='gpt4',
             requirement_list=None,
             logger=None):
    '''
    角色进行投票
    Input:
        source_character_id_number: str,
        source_character_description:str,
        self_belief_description: str, 
        vote_requirement: str 投票要求
        background_information: str 背景信息
        candidates: str 可以投票的对象

    Output:
        choice : str, 选择的角色id_number
        reasoning_process: str, 推理理由
    '''

    gpt_param = {"temperature": 0.3, "top_p": 1, "stream": False,
                 "frequency_penalty": 0, "presence_penalty": 0, "stop": None}

    if not support_character:
        support_character = '你目前不支持任何其他角色，所以你只考虑自己的利益。'

    prompt_template = "prompt_files/prompt_4_vote.txt"
    prompt_input = create_prompt_input(source_character_id_number,
                                       source_character_description,
                                       self_belief_description,
                                       vote_requirement,
                                       background_information,
                                       candidates,
                                       support_character)
    prompt = generate_prompt(prompt_input, prompt_template, fn_name=sys._getframe().f_code.co_name)

    def parse_output(gpt_response):
        ret = {}
        try:
            # reasoning_process = re.search(r"### Reasoning Process:(.*)\n", gpt_response).group(1).strip()
            # choice = re.search(r"### Choice:(.*)",gpt_response).group(1).strip()
            action_space = [i.strip() for i in gpt_response.split('### Action Space:')[-1].split('### Reasoning Process')[0].strip().split(',')]
            reasoning_process = gpt_response.split('### Reasoning Process:')[-1].split('### Choice:')[0].strip()
            choice = [i.strip() for i in gpt_response.split('### Choice:')[-1].strip().split(',')]
            ret['reasoning_process'] = reasoning_process
            ret['choice'] = choice

            if not choice or not reasoning_process:
                raise Exception("[Error]: GPT response not in given format")
        except:
            print('ERROR\nERROR\n', gpt_response, '\nERROR\nERROR\n')
            raise Exception("[Error]: GPT response parse error")
        return action_space, choice, reasoning_process

    if engine == 'human':
        action_space='[SKIP]'
        human_prompt = '你是%s，你的介绍是%s。\n候选人名单：\n%s\n请输入你想对话的角色：\n' % (source_character_id_number,
                                                                                    source_character_description,
                                                                                    candidates)
        logger.gprint(human_prompt,
                      thought=human_prompt,
                      requirement=requirement_list,
                      important_log='important_log',
                      source_character='',
                      target_character='',
                      log_type='Human Choosing',
                      log_content=human_prompt)
        choice=generate_with_response_parser(human_prompt,
                                             engine=engine,
                                             logger=logger,func_name='human_vote')
        logger.gprint(choice,
                      thought=human_prompt,
                      requirement=requirement_list,
                      important_log='important_log',
                      source_character='',
                      target_character='',
                      log_type='Human Choosing Result',
                      log_content=choice)
        choice = [choice, choice]
        reasoning_process='这是人类，不需要推理'
    else:
        action_space, choice, reasoning_process = generate_with_response_parser(prompt,
                                                                                gpt_param=gpt_param,
                                                                                parser_fn=parse_output,
                                                                                engine=engine,
                                                                                logger=logger,func_name='run_vote')
    return action_space, choice, reasoning_process


