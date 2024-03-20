import json
import contextvars
import uvicorn
from typing import List
from pydantic import BaseModel
from uuid import uuid4
from fastapi import FastAPI, BackgroundTasks, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from config import *
from logger_class import Logger_v2
from main import SucArena
from resources.info_bank import *
from help_functions import *


# 默认全局变量
log_dir = LOG_FOLDER
save_folder = SAVE_FOLDER

# Context局部变量
context_sid = contextvars.ContextVar('sid')
conetxt_logger = contextvars.ContextVar('logger')
context_test_folder = contextvars.ContextVar('test_folder')

app = FastAPI()

# 配置跨域
app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=False,
	allow_methods=["*"],
	allow_headers=["*"],
)


class GameConfig(BaseModel):
    game_round: int = GAME_ROUND
    battle_chat_round: int = BATTLE_CHAT_ROUND
    collabration_chat_round: int = COLLABORATION_CHAT_ROUND
    sid: str = ""


@app.post("/api/v1/create")
async def create_session(setting: GameConfig, background_tasks: BackgroundTasks):    
    # 获取sid
    if setting.sid:  # 如果sid不为空，读档
        # 如果sid不存在，返回报错信息
        all_sids = [sid for sid in os.listdir(TEST_FOLDER)]
        if setting.sid not in all_sids:
            raise HTTPException(status_code=404, detail="sid not exist")
        # 设置当前sid
        context_sid.set(setting.sid)
    else:  # 否则开始新游戏
        context_sid.set(str(uuid4().hex))

    # 获取logger
    cur_logger = await Logger_v2.create(log_dir, context_sid.get())
    conetxt_logger.set(cur_logger)

    # 获取test_folder
    cur_test_folder = os.path.join(TEST_FOLDER, context_sid.get())
    if not os.path.exists(cur_test_folder):
        # 如果test_folder不存在，创建test_folder，初始内容为SAVE_FOLDER中的内容
        os.makedirs(cur_test_folder)
        copy_dir(SAVE_FOLDER, cur_test_folder)
    context_test_folder.set(cur_test_folder)
    
    background_tasks.add_task(start_game, setting)
    return {"sid": context_sid.get()}


def start_game(setting: GameConfig):
    sucarena = SucArena(all_round_number=setting.game_round,
                        battle_chat_round=setting.battle_chat_round,
                        collabration_chat_round=setting.collabration_chat_round,
                        save_folder=context_test_folder.get(),
                        test_folder=context_test_folder.get(),
                        logger=conetxt_logger.get())
    try:
        logger = conetxt_logger.get()
        test_folder = context_test_folder.get()

        for i in range(setting.game_round):
            logger.gprint('==' * 10)
            logger.gprint('Turn %d' % (i + 1),
                          important_log='important_log',
                          source_character='',
                          target_character='',
                          log_type='Turn Change',
                          thought='',
                          log_content='Turn %d' % (i + 1))

            logger.gprint('==' * 10)
            logger.gprint('Confrontation Stage',
                          important_log='important_log',
                          source_character='',
                          target_character='',
                          log_type='Stage Change',
                          thought='',
                          log_content='Confrontation Stage')
            sucarena.compete_stage(i)

            logger.gprint('==' * 10)
            logger.gprint('Cooperation Stage',
                          important_log='important_log',
                          source_character='',
                          target_character='',
                          log_type='Stage Change',
                          thought='',
                          log_content='Cooperation Stage')
            sucarena.collaborate_stage(i)

            logger.gprint('==' * 10)
            logger.gprint('Announcement Stage',
                          important_log='important_log',
                          source_character='',
                          target_character='',
                          log_type='Stage Change',
                          thought='',
                          log_content='Announcement Stage')
            sucarena.announcement_stage(i)

            logger.gprint('==' * 10)
            logger.gprint('Update Stage',
                          important_log='important_log',
                          source_character='',
                          target_character='',
                          log_type='Stage Change',
                          thought='',
                          log_content='Update Stage')
            sucarena.update_stage(i)

            logger.gprint('Start Saving')
            sucarena.save(test_folder)

            logger.gprint('==' * 10)
            logger.gprint('',
                          important_log='important_log',
                          source_character='',
                          target_character='',
                          log_type='Turn End',
                          thought='',
                          log_content='')

        # 结算阶段
        game_name = 'Succession'

        logger.gprint('==' * 10)
        logger.gprint('Settlement Turn',
                      important_log='important_log',
                      source_character='',
                      target_character='',
                      log_type='Turn Change',
                      thought='',
                      log_content='Settlement Turn')
        local_information_winner = sucarena.settlement_stage(whole_information=False, game_name=game_name)
        logger.gprint('',
                      important_log='important_log',
                      source_character='',
                      target_character='',
                      log_type='Turn End',
                      thought='',
                      log_content='')

        logger.gprint('==' * 10)
        logger.gprint('Settlement Turn (Cheating)',
                      important_log='important_log',
                      source_character='',
                      target_character='',
                      log_type='Turn Change',
                      thought='',
                      log_content='Settlement Turn (Cheating)')
        whole_information_winner = sucarena.settlement_stage(whole_information=True, game_name=game_name)
        logger.gprint('',
                      important_log='important_log',
                      source_character='',
                      target_character='',
                      log_type='Turn End',
                      thought='',
                      log_content='')

        logger.gprint('Start Saving')
        sucarena.save(test_folder)
        logger.gprint('Game ends successfully')
        logger.close()
    except Exception as e:
        logger.gprint(e)
        logger.gprint('Game ends with error')
        logger.close()


@app.get("/api/v1/get")
async def get_logs(sid: str, last: int):
    """
    Retrieve logs of session with sid.

    INPUT:
        sid: session id
        last: the last retrieved log id
    OUTPUT:
        important logs from (last + 1)
    """
    from_id = last + 1
    log_file = os.path.join(log_dir, f"{sid}.json")
    lines = await read_logs(log_file, from_id)
    results = []
    for line in lines:
        line = eval(text_translation(line, id_trans_table))  # 替换角色名后转成字典
        line_common = {'sid': line['sid'], 'id': line['id'], 'time': line['time'], 'args': line['args']}
        line_kwargs = eval(line['kwargs'])
        results.append({**line_common, **line_kwargs})
    return results


async def read_logs(log_file, from_id):
    with open(log_file, 'r', encoding='utf-8') as log_fw:
        lines = log_fw.readlines()[from_id:]
    return lines


class UserInput(BaseModel):
    sid: str = ""
    input_str: str = ""


@app.post("/api/v1/input")
async def get_input(user_input: UserInput):
    if not os.path.exists(INPUT_FOLDER):
        os.mkdir(INPUT_FOLDER)
    # 如果sid不存在，返回报错信息
    all_sids = [sid.split('.txt')[0] for sid in os.listdir(INPUT_FOLDER)]
    if user_input.sid not in all_sids:
        raise HTTPException(status_code=404, detail="sid not exist")
    # 写入文件
    save_input_path = os.path.join(INPUT_FOLDER, user_input.sid + ".txt")
    with open(save_input_path, "w", encoding="utf-8") as f:
        f.write(user_input.input_str)


@app.get("/api/v1/quicksimulate")
async def quick_simulate():
    """
    获取筛选后的sid用于快速simulate

    OUTPUT:
        {
            "Simulation1": "2e295fa3cddd47e8bccbc377608cf179",
            "Simulation2": "be141b8d5e2c4befb34e2cf358dd705e",
            "Simulation3": "c81e3621c50640aba0aad3feae9dae7c"
        }
    """
    return quick_simulate_sids


@app.get("/api/v1/getsettings")
async def get_settings():
    """
    角色和社会资源展示

    OUTPUT:
        {
            "characters": [{character1 details}, {character2 details}, ...],
            "resources": [{resource1 details}, {resource2 details}, ...]
        }
    """
    characters, resources = [], []
    save_characters_folder = os.path.join(save_folder, "characters")
    save_resources_folder = os.path.join(save_folder, "resources")
    for character_file in os.listdir(save_characters_folder):
        f_path = os.path.join(save_characters_folder, character_file)
        with open(f_path, 'r', encoding='utf-8') as f:
            character_detail = json.load(f)
        characters.append(character_detail)
    for resource_file in os.listdir(save_resources_folder):
        f_path = os.path.join(save_resources_folder, resource_file)
        with open(f_path, 'r', encoding='utf-8') as f:
            resource_detail = json.load(f)
        resources.append(resource_detail)
    return {"characters": characters, "resources": resources}


class NewCharacterRequest(BaseModel):
    name: str = ""
    main_character: str = ""
    support_character: str = ""
    objective: str = ""
    scratch: str = ""
    background: str = ""
    belief: List[int] = []  # 5个信念分
    relation: List[int] = []  # 与9个默认角色的关系分
    portrait: str = ""
    small_portrait: str = ""


@app.post("/api/v1/addcharacter", status_code=status.HTTP_201_CREATED)
async def add_character(request: NewCharacterRequest):
    """
    插入新角色

    INPUT: NewCharacterRequest
        name: str
        main_character: str
        support_character: str
        objective: str
        scratch: str
        background: str
        belief: List[int] = []  # 5个信念分
        relation: List[int] = []  # 与9个默认角色的关系分
        portrait: str
        small_portrait: str
    """
    # get new index
    save_characters_folder = os.path.join(save_folder, "characters")
    max_idx = 0
    for character_file in os.listdir(save_characters_folder):
        curr_idx = int(character_file.split("C")[1].split(".json")[0])
        if curr_idx > max_idx:
            max_idx = curr_idx
    new_idx = "C" + str(max_idx + 1).zfill(4)

    # some check
    # check support character in all characters
    all_characters = [character.split('.json')[0] for character in os.listdir(save_characters_folder)]
    if request.support_character not in all_characters:
        raise HTTPException(status_code=404, detail="Support character not exist")
    # check belief and relation score num
    if len(request.belief) != len(all_characters) or len(request.relation) != len(all_characters):
        raise HTTPException(status_code=500, detail="Element number of belief or relation not equal to all character number")

    # create new character
    character = {
        "name": request.name,
        "id_name": new_idx,
        "main_character": request.main_character,
        "support_character": request.support_character,
        "objective": request.objective,
        "scratch": request.scratch,
        "background": request.background,
        "belief": {f"Stand with C000{i}": request.belief[i] for i in range(len(request.belief))},
        "judgement": {},
        "relation": {f"C000{i}": request.relation[i] for i in range(len(request.relation))},
        "portrait": request.portrait,
        "small_portrait": request.small_portrait
    }
    # save new character
    save_path = os.path.join(save_characters_folder, new_idx + ".json")
    with open(save_path, 'w', encoding='utf-8') as f:    
        json_data = json.dumps(character, indent=4, ensure_ascii=False)    
        f.write(json_data)
    return "New Character Created"


class NewResourceRequest(BaseModel):
    name: str = ""
    description: str = ""
    influence: str = ""
    owner: str = ""
    topic: List[str] = []
    portrait: str = ""
    small_portrait: str = ""


@app.post("/api/v1/addresource", status_code=status.HTTP_201_CREATED)
async def add_resource(request: NewResourceRequest):
    """
    插入新社会资源 

    INPUT: NewResourceRequest
        name: str
        description: str
        influence: str
        owner: str
        topic: str
        portrait: str
        small_portrait: str
    """
    # get new index
    save_resources_folder = os.path.join(save_folder, "resources")
    max_idx = 0
    for resource_file in os.listdir(save_resources_folder):
        curr_idx = int(resource_file.split("R")[1].split(".json")[0])
        if curr_idx > max_idx:
            max_idx = curr_idx
    new_idx = "R" + str(max_idx + 1).zfill(4)

    # some check
    # check if influence is a number
    try:
        influence_score = int(request.influence)
    except Exception:
        raise HTTPException(status_code=500, detail="Influnce score should be a integer")
    # check owner in all characters
    save_characters_folder = os.path.join(save_folder, "characters")
    all_characters = [character.split('.json')[0] for character in os.listdir(save_characters_folder)]
    if request.owner not in all_characters:
        raise HTTPException(status_code=404, detail="Owner not exist")

    # create new resource
    resource = {
        "name": request.name,
        "id_number": new_idx,
        "description": request.description,
        "influence": request.influence,
        "owner": request.owner,
        "topic": "[TOPIC_SEP]".join(request.topic),
        "portrait": request.portrait,
        "small_portrait": request.small_portrait
    }
    # save new resource
    save_path = os.path.join(save_resources_folder, new_idx + ".json")
    with open(save_path, 'w', encoding='utf-8') as f:    
        json_data = json.dumps(resource, indent=4, ensure_ascii=False)    
        f.write(json_data)
    return "New Resource Created"


@app.get("/test")
def test():
    return "hello"


if __name__ == '__main__':
    uvicorn.run(app='server:app', host='0.0.0.0', port=8080, reload=True)