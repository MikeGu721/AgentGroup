
# Agent Group Chat: An Interactive Group Chat Simulacra For Better Eliciting Collective Emergent Behavior

<img src="figures/headfigure.png">

## Change Log
- [2024.03.20]: 🔥🔥 Open-sourced the git repository, including the detailed configuration steps to implement our Agent Group Chat!

## Introduction

## Demo
- Coming Soon!

## Quick Start
### w/o Front-end for now, we will upload Front-end code soon.
- `pip install -r requirements.txt`
- set your api url and key in `./prompt/utils.py`
- set some hyper-parameters in `config.py`
- `python main.py`

## How to Customize Your Story
- construct a new folder in `./storage` like `./storage/xxxx` 
- copy `./storage/succession/` into `./storage/xxxx` 
- rewrite your story setting in `./storage/xxxx/succession_rule_setting.txt`
- rewrite your character setting in `./storage/xxxx/characters`, as for specific description of each field, please refer **Character Setting** 
- rewrite your resources setting in `./storage/xxxx/resources` , as for specific description of each field, please refer **Resources Setting** 
- rewrite your basic setting in `./storage/xxxx/basic_setting.json`

## How to incorporate your Large Language Models:
- write your code in `./prompt/gpt_structure.py`

## Human Interaction
- 在`initial_version/characters/xxx.json`里，将"engine"换为"human"便可以设置人类参与
- 人类需要输入以下内容
  - act——选人
  - converse——对话
  - speech——对话
  - guess——选人
  - vote——选人
  - vote_others——选人
  - 选人
    - log_type: "Human Choosing"
    - requirement: 候选list
    - thought: context
  - 对话
    - log_type: "Human Speaking"
    - thought: context

## Character
```markdown
"name": 角色名字【只在前端展示出来】,
"id_name": 角色ID【后端交互时，都使用ID】,
"main_character": 是否为主要角色,
"support_character": 支持哪个角色【暂时设定为主要角色不会支持其他角色】,
"objective": 角色的目标
"scratch": 角色的脚本【仅自己可见】
"background": 角色的背景【所有人可见】
"engine": 角色是由哪个模型驱动的【gpt3.5, gpt4, human, glm-3-turbo, glm-4, hunyuan-chatpro, hunyuan-chatstd, huggingface上的模型参数(THUDM/chatglm3-6b-32k)】
"belief": 角色的信念【可能会在不同信念之间发生跳转】
"judgement": 对于其他角色之间关系的判断【还没实现】
"relation": 对于其他角色的关系【初始置空】
"portrait": 角色头像存放位置
"small_portrait": 角色小头像存放位置
```

## Resource
```markdown
"name": 资源名字
"id_number": R + 资源的ID Number
"description": 资源的介绍【所有人可见】
"influence": 资源的影响力数值
"owner": 资源的拥有者
"topic": 资源所能够提供的话题
"portrait": 资源的显示头像【暂时无用】
"small_portrait": 资源的显示头像【暂时无用】
```

## Logger
```markdown
"source_character": 日志发起角色
"target_character": 动作对象
"thought": 思考过程
"log_type": 日志事件【参考下表】
"log_content": 事件具体【参考下表】
```

## Action History
```markdown
"source_character": 动作发起者
"target_character": 动作接受者
"action_type": 动作类型
"action_content": 动作内容
```

## Action Type
- SAY
- CHAT_SUMMARIZATION
- MEET
- REFLECT
- SPEECH_NORMAL
- SPEECH_VOTE
- GUESS
- VOTE
- VOTE_OTHERS

## TODO List:
[ ] Open Source Online Platform
[ ] Put more demos into the project
[ ] Open Source Benchmark