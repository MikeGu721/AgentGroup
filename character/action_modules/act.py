from prompt.gpt_structure import generate_prompt, generate_with_response_parser, create_prompt_input
import sys


def run_act(self_agent_id_number: str,
            self_agent_description: str,
            environment_summary: str,
            round_description: str,
            action_history_description: str,
            candidate_description: str,
            chat_round_num: str,
            engine='gpt4',
            requirement_list=None,
            logger=None):
    '''
    让source_character根据environment_description和target_character_list来选择target_character
    
    Input:
        self_agent_id_number: str,
        self_agent_description: str,
        environment_summary: str,
        round_description: str, 描述当前轮数
        action_history_description: str,
        candidate_description: str,
        logger: Logger, 已有的logger类

    Output:
        target_character_id_number: str, 被选中角色的ID Number
    '''

    gpt_param = {"max_tokens": 500,
                 "temperature": 0, "top_p": 1, "stream": False,
                 "frequency_penalty": 0, "presence_penalty": 0, "stop": None}

    prompt_template = "prompt_files/prompt_4_act.txt"
    prompt_template = "prompt_files/prompt_wo_thinking/prompt_4_act_wo_thinking.txt"
    prompt_input = create_prompt_input(self_agent_id_number,
                                       self_agent_description,
                                       environment_summary,
                                       round_description,
                                       action_history_description,
                                       candidate_description,
                                       chat_round_num)

    def parse_output(gpt_response):
        action_history = [ii.strip() for ii in
                          gpt_response.split('### Action Space:')[-1].split('### Thought:')[0].split(',')]
        thought = gpt_response.split('### Thought:')[-1].split('### Plan:')[0].strip()
        plan = gpt_response.split('### Plan:')[-1].split('### Choose:')[0].strip()
        candidate = gpt_response.split('### Choose:')[-1].strip()
        return action_history, thought, plan, candidate

    prompt = generate_prompt(prompt_input, prompt_template, fn_name=sys._getframe().f_code.co_name)
    if engine == 'human':
        action_history = '[SKIP]'
        thought = '这个是人类，不需要thought'
        plan = '这个是人类，不需要plan'
        human_prompt = '你是%s，你的介绍是%s。\n候选人名单：\n%s\n请输入你想对话的角色：\n' % (self_agent_id_number,
                                                                                    self_agent_description,
                                                                                    candidate_description)
        logger.gprint(human_prompt,
                      thought=human_prompt,
                      require=requirement_list,
                      important_log='important_log',
                      source_character='',
                      target_character='',
                      log_type='Human Choosing',
                      log_content=human_prompt)
        candidate = generate_with_response_parser(human_prompt,
                                                  engine=engine,
                                                  logger=logger,
                                                  func_name='human_act')
        logger.gprint(candidate,
                      thought=human_prompt,
                      require=requirement_list,
                      important_log='important_log',
                      source_character='',
                      target_character='',
                      log_type='Human Choosing Result',
                      log_content=candidate)
    else:
        action_history, thought, plan, candidate = generate_with_response_parser(prompt,
                                                                                 gpt_param=gpt_param,
                                                                                 parser_fn=parse_output,
                                                                                 engine=engine,
                                                                                 logger=logger,
                                                                                 func_name='run_act')
    return action_history, thought, plan, candidate
