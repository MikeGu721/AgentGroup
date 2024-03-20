from prompt.gpt_structure import generate_prompt, generate_with_response_parser, create_prompt_input
import sys

def run_summarization(self_agent_id_number: str,
                      self_agent_description: str,
                      environment_summary: str,
                      chat_history: str,
                      engine='gpt4',
                      logger=None):
    '''
    让source_character根据environment_description和target_character_list来选择target_character

    Input:
        self_agent_id_number: str,
        target_agent_description: str,
        self_agent_description: str,
        target_agent_description: str,
        environment_summary: str,
        chat_history: str, 描述当前轮数
        planning: str,
        engine: str,
        logger: Logger, 已有的logger类

    Output:
        target_character_id_number: str, 被选中角色的ID Number
    '''

    gpt_param = {"max_tokens": 500,
                 "temperature": 0, "top_p": 1, "stream": False,
                 "frequency_penalty": 0, "presence_penalty": 0, "stop": None}

    prompt_template = "prompt_files/prompt_4_summarize.txt"
    prompt_template = "prompt_files/prompt_wo_thinking/prompt_4_summarize_wo_thinking.txt"
    prompt_input = create_prompt_input(self_agent_id_number,
                      self_agent_description,
                      environment_summary,
                      chat_history)

    def parse_output(gpt_response):
        thought = gpt_response.split('### Thinking:')[-1].split('### Number of Chat Round:')[0].split(',')
        chat_round = gpt_response.split('### Number of Chat Round:')[-1].split('### Chat Summarization:')[0].strip()
        chat_summarization = gpt_response.split('### Chat Summarization:')[-1].strip()
        return thought, chat_round, chat_summarization

    prompt = generate_prompt(prompt_input, prompt_template, fn_name=sys._getframe().f_code.co_name)
    if engine == 'human':
        chat_round = '[SKIP]'
        thought = '这个是人类，不需要thought'
        chat_summarization = '这个是人类，不需要summarization'

    else:
        thought, chat_round, chat_summarization = generate_with_response_parser(prompt,
                                                                                 gpt_param=gpt_param,
                                                                                 parser_fn=parse_output,
                                                                                 engine=engine,
                                                                                 logger=logger,func_name='run_summarization')

    action_event = [self_agent_id_number,
                    self_agent_id_number,
                    '### CHAT SUMMARIZATION',
                    '%s summarization of chatting: %s' % (self_agent_id_number, chat_summarization)]
    return thought, chat_round, action_event
