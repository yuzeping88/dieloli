from functools import wraps
from typing import Set
from types import FunctionType
from Script.Core import constant, cache_control, game_type, get_text
from Script.Design import update, character
# from Script.Flow import buy_food, eat_food


cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """


def handle_instruct(instruct:int):
    """
    处理执行指令
    Keyword arguments:
    instruct -- 指令id
    """
    if instruct in cache.instruct_premise_data:
        cache.handle_instruct_data[instruct]()


def add_instruct(instruct_id:int,instruct_type:int,name:str,premise_set:Set):
    """
    添加指令处理
    Keyword arguments:
    instruct_id -- 指令id
    instruct_type -- 指令类型
    name -- 指令绘制文本
    premise_set -- 指令所需前提集合
    """

    def decorator(func):
        @wraps(func)
        def return_wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        cache.handle_instruct_data[instruct_id] = return_wrapper
        cache.instruct_premise_data[instruct_id] = premise_set
        cache.instruct_type_data.setdefault(instruct_type,set())
        cache.instruct_type_data[instruct_type].add(instruct_id)
        cache.handle_instruct_name_data[instruct_id] = name
        return return_wrapper

    return decorator


@add_instruct(constant.Instruct.REST,constant.InstructType.REST,_("休息"),{})
def handle_rest():
    """ 处理休息指令 """
    character.init_character_behavior_start_time(0)
    character_data = cache.character_data[0]
    character_data.behavior.duration = 10
    character_data.behavior.behavior_id = constant.Behavior.REST
    character_data.state = constant.CharacterStatus.STATUS_REST
    if character_data.hit_point > character_data.hit_point_max:
        character_data.hit_point = character_data.hit_point_max
    target_character = cache.character_data[character_data.target_character_id]
    if (
        target_character.state == constant.CharacterStatus.STATUS_ARDER
        and target_character.behavior.behavior_id == constant.Behavior.SHARE_BLANKLY
    ):
        target_character.state = constant.CharacterStatus.STATUS_REST
        character.init_character_behavior_start_time(character_data.target_character_id)
        target_character.behavior.duration = 10
        target_character.behavior.behavior_id = constant.Behavior.REST
    update.game_update_flow(10)



@add_instruct(constant.Instruct.BUY_FOOD,constant.InstructType.ACTIVE,_("购买食物"),{constant.Premise.IN_CAFETERIA})
def handle_buy_food():
    """ 处理购买食物指令 """
    #buy_food.buy_food()


@add_instruct(constant.Instruct.EAT,constant.InstructType.ACTIVE,_("进食"),{})
def handle_eat():
    """ 处理进食指令 """
    character.init_character_behavior_start_time(0)
    """
    judge, now_food = eat_food.eat_food()
    if judge:
        character_data = cache.character_data[0]
        character_data.behavior.behavior_id = constant.Behavior.EAT
        character_data.behavior.eat_food = now_food
        character_data.behavior.duration = 1
        character_data.state = constant.CharacterStatus.STATUS_EAT
    update.game_update_flow(1)
    """
