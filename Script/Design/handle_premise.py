import math
import datetime
from functools import wraps
from types import FunctionType
from Script.Core import cache_control, constant, game_type
from Script.Design import map_handle, game_time, attr_calculation
from Script.Config import game_config

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """


def add_premise(premise: int) -> FunctionType:
    """
    添加前提
    Keyword arguments:
    premise -- 前提id
    Return arguments:
    FunctionType -- 前提处理函数对象
    """

    def decoraror(func):
        @wraps(func)
        def return_wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        cache.handle_premise_data[premise] = return_wrapper
        return return_wrapper

    return decoraror


def handle_premise(premise: int, character_id: int) -> int:
    """
    调用前提id对应的前提处理函数
    Keyword arguments:
    premise -- 前提id
    character_id -- 角色id
    Return arguments:
    int -- 前提权重加成
    """
    if premise in cache.handle_premise_data:
        return cache.handle_premise_data[premise](character_id)
    else:
        return 0


@add_premise(constant.Premise.IN_CAFETERIA)
def handle_in_cafeteria(character_id: int) -> int:
    """
    校验角色是否处于取餐区中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if now_scene_data.scene_tag == "Cafeteria":
        return 1
    return 0


@add_premise(constant.Premise.IN_RESTAURANT)
def handle_in_restaurant(character_id: int) -> int:
    """
    校验角色是否处于就餐区中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if now_scene_data.scene_tag == "Restaurant":
        return 1
    return 0


@add_premise(constant.Premise.IN_BREAKFAST_TIME)
def handle_in_breakfast_time(character_id: int) -> int:
    """
    校验当前时间是否处于早餐时间段
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_time = game_time.get_sun_time(character_data.behavior.start_time)
    return now_time == 4


@add_premise(constant.Premise.IN_LUNCH_TIME)
def handle_in_lunch_time(character_id: int) -> int:
    """
    校验当前是否处于午餐时间段
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_time = game_time.get_sun_time(character_data.behavior.start_time)
    return now_time == 7


@add_premise(constant.Premise.IN_DINNER_TIME)
def handle_in_dinner_time(character_id: int) -> int:
    """
    校验当前是否处于晚餐时间段
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_time = game_time.get_sun_time(character_data.behavior.start_time)
    return now_time == 9


@add_premise(constant.Premise.HUNGER)
def handle_hunger(character_id: int) -> int:
    """
    校验角色是否处于饥饿状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    character_data.status.setdefault(27, 0)
    return math.floor(character_data.status[27] / 10)


@add_premise(constant.Premise.HAVE_FOOD)
def handle_have_food(character_id: int) -> int:
    """
    校验角色是否拥有食物
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    food_index = 0
    for food_id in character_data.food_bag:
        if character_data.food_bag[food_id].eat:
            food_index += 1
    return food_index


@add_premise(constant.Premise.NOT_HAVE_FOOD)
def handle_not_have_food(character_id: int) -> int:
    """
    校验角色是否没有食物
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    food_index = 1
    for food_id in character_data.food_bag:
        if character_data.food_bag[food_id].eat:
            return 0
    return food_index


@add_premise(constant.Premise.HAVE_TARGET)
def handle_have_target(character_id: int) -> int:
    """
    校验角色是否有交互对象
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.target_character_id == character_id:
        return 0
    return 1


@add_premise(constant.Premise.TARGET_NO_PLAYER)
def handle_target_no_player(character_id: int) -> int:
    """
    校验角色目标对像是否不是玩家
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.target_character_id > 0:
        return 1
    return 0


@add_premise(constant.Premise.HAVE_DRAW_ITEM)
def handle_have_item_by_tag_draw(character_id: int) -> int:
    """
    校验角色是否拥有绘画类道具
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    for item_id in game_config.config_item_tag_data["Draw"]:
        if item_id in character_data.item:
            return 1
    return 0


@add_premise(constant.Premise.HAVE_SHOOTING_ITEM)
def handle_have_item_by_tag_shooting(character_id: int) -> int:
    """
    校验角色是否拥有射击类道具
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    for item_id in game_config.config_item_tag_data["Shooting"]:
        if item_id in character_data.item:
            return 1
    return 0


@add_premise(constant.Premise.HAVE_GUITAR)
def handle_have_guitar(character_id: int) -> int:
    """
    校验角色是否拥有吉他
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if 4 in character_data.item:
        return 1
    return 0


@add_premise(constant.Premise.HAVE_HARMONICA)
def handle_have_harmonica(character_id: int) -> int:
    """
    校验角色是否拥有口琴
    Keyword arguments:
    character_id --角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if 5 in character_data.item:
        return 1
    return 0


@add_premise(constant.Premise.HAVE_BAM_BOO_FLUTE)
def handle_have_bamboogflute(character_id: int) -> int:
    """
    校验角色是否拥有竹笛
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if 6 in character_data.item:
        return 1
    return 0


@add_premise(constant.Premise.HAVE_BASKETBALL)
def handle_have_basketball(character_id: int) -> int:
    """
    校验角色是否拥有篮球
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if 0 in character_data.item:
        return 1
    return 0


@add_premise(constant.Premise.HAVE_FOOTBALL)
def handle_have_football(character_id: int) -> int:
    """
    校验角色是否拥有足球
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if 1 in character_data.item:
        return 1
    return 0


@add_premise(constant.Premise.HAVE_TABLE_TENNIS)
def handle_have_tabletennis(character_id: int) -> int:
    """
    校验角色是否拥有乒乓球
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if 2 in character_data.item:
        return 1
    return 0


@add_premise(constant.Premise.IN_SWIMMING_POOL)
def handle_in_swimming_pool(character_id: int) -> int:
    """
    校验角色是否在游泳池中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if now_scene_data.scene_tag == "SwimmingPool":
        return 1
    return 0


@add_premise(constant.Premise.IN_CLASSROOM)
def handle_in_classroom(character_id: int) -> int:
    """
    校验角色是否处于教室中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if now_scene_data.scene_tag.startswith("Classroom"):
        return 1
    return 0


@add_premise(constant.Premise.IS_STUDENT)
def handle_is_student(character_id: int) -> int:
    """
    校验角色是否是学生
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.age <= 18:
        return 1
    return 0


@add_premise(constant.Premise.IS_TEACHER)
def handle_is_teacher(character_id: int) -> int:
    """
    校验角色是否是老师
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.age > 18:
        return 1
    return 0


@add_premise(constant.Premise.IN_SHOP)
def handle_in_shop(character_id: int) -> int:
    """
    校验角色是否在商店中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if now_scene_data.scene_tag == "Shop":
        return 1
    return 0


@add_premise(constant.Premise.IN_SLEEP_TIME)
def handle_in_sleep_time(character_id: int) -> int:
    """
    校验角色当前是否处于睡觉时间
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_time: datetime.datetime = character_data.behavior.start_time
    if now_time.hour >= 22 or now_time.hour <= 4:
        return 1
    return 0


@add_premise(constant.Premise.IN_SIESTA_TIME)
def handle_in_siesta_time(character_id: int) -> int:
    """
    校验角色是否处于午休时间
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    now_time: datetime.datetime = character_data.behavior.start_time
    if now_time.hour >= 12 or now_time.hour <= 15:
        return 1
    return 0


@add_premise(constant.Premise.TARGET_IS_FUTA_OR_WOMAN)
def handle_target_is_futa_or_woman(character_id: int) -> int:
    """
    校验角色的目标对象性别是否为女性或扶她
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.sex in {1, 2}:
        return 1
    return 0


@add_premise(constant.Premise.TARGET_IS_FUTA_OR_MAN)
def handle_target_is_futa_or_man(character_id: int) -> int:
    """
    校验角色的目标对象性别是否为男性或扶她
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.sex in {0, 1}:
        return 1
    return 0


@add_premise(constant.Premise.IS_MAN)
def handle_is_man(character_id: int) -> int:
    """
    校验角色是否是男性
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if not character_data.sex:
        return 1
    return 0


@add_premise(constant.Premise.IS_WOMAN)
def handle_is_woman(character_id: int) -> int:
    """
    校验角色是否是女性
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.sex == 1:
        return 1
    return 0


@add_premise(constant.Premise.TARGET_SAME_SEX)
def handle_target_same_sex(character_id: int) -> int:
    """
    校验角色目标对像是否与自己性别相同
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.sex == character_data.sex:
        return 1
    return 0


@add_premise(constant.Premise.TARGET_AGE_SIMILAR)
def handle_target_age_similar(character_id: int) -> int:
    """
    校验角色目标对像是否与自己年龄相差不大
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if character_data.age >= target_data.age - 2 and character_data.age <= target_data.age + 2:
        return 1
    return 0


@add_premise(constant.Premise.TARGET_AVERAGE_HEIGHT_SIMILAR)
def handle_target_average_height_similar(character_id: int) -> int:
    """
    校验角色目标身高是否与平均身高相差不大
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    age_tem = attr_calculation.judge_age_group(target_data.age)
    average_height = cache.average_height_by_age[age_tem][target_data.sex]
    if (
        target_data.height.now_height >= average_height * 0.95
        and target_data.height.now_height <= average_height * 1.05
    ):
        return 1
    return 0


@add_premise(constant.Premise.TARGET_AVERAGE_HEIGHT_LOW)
def handle_target_average_height_low(character_id: int) -> int:
    """
    校验角色目标的身高是否低于平均身高
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    age_tem = attr_calculation.judge_age_group(target_data.age)
    average_height = cache.average_height_by_age[age_tem][target_data.sex]
    if target_data.height.now_height <= average_height * 0.95:
        return 1
    return 0


@add_premise(constant.Premise.TARGET_IS_PLAYER)
def handle_is_player(character_id: int) -> int:
    """
    校验角色目标是否是玩家
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.target_character_id == 0:
        return 1
    return 0


@add_premise(constant.Premise.TARGET_AVERGAE_STATURE_SIMILAR)
def handle_target_average_stature_similar(character_id: int) -> int:
    """
    校验角色目体型高是否与平均体型相差不大
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    age_tem = attr_calculation.judge_age_group(target_data.age)
    if age_tem in cache.average_bodyfat_by_age:
        average_bodyfat = cache.average_bodyfat_by_age[age_tem][target_data.sex]
        if target_data.bodyfat >= average_bodyfat * 0.95 and target_data.bodyfat <= average_bodyfat * 1.05:
            return 1
    return 0


@add_premise(constant.Premise.TARGET_NOT_PUT_ON_UNDERWEAR)
def handle_target_not_put_underwear(character_id: int) -> int:
    """
    校验角色的目标对象是否没穿上衣
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if (1 not in target_data.put_on) or (target_data.put_on[1] == ""):
        return 1
    return 0


@add_premise(constant.Premise.TARGET_NOT_PUT_ON_SKIRT)
def handle_target_put_on_skirt(character_id: int) -> int:
    """
    校验角色的目标对象是否穿着短裙
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if (3 not in target_data.put_on) or (target_data.put_on[3] == ""):
        return 0
    return 1


@add_premise(constant.Premise.IS_PLAYER)
def handle_is_player(character_id: int) -> int:
    """
    校验是否是玩家角色
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if not character_id:
        return 1
    return 0


@add_premise(constant.Premise.NO_PLAYER)
def handle_no_player(character_id: int) -> int:
    """
    校验是否不是玩家角色
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if character_id:
        return 1
    return 0


@add_premise(constant.Premise.IN_PLAYER_SCENE)
def handle_in_player_scene(character_id: int) -> int:
    """
    校验角色是否与玩家处于同场景中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    now_character_data = cache.character_data[character_id]
    if now_character_data.position == cache.character_data[0].position:
        return 1
    return 0


@add_premise(constant.Premise.LEAVE_PLAYER_SCENE)
def handle_leave_player_scene(character_id: int) -> int:
    """
    校验角色是否是从玩家场景离开
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    now_character_data = cache.character_data[character_id]
    if now_character_data.behavior.move_src == cache.character_data[0].position:
        return 1
    return 0


@add_premise(constant.Premise.TARGET_IS_ADORE)
def handle_target_is_adore(character_id: int) -> int:
    """
    校验角色当前目标是否是自己的爱慕对象
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_id = character_data.target_character_id
    character_data.social_contact.setdefault(5, set())
    if target_id in character_data.social_contact[5]:
        return 1
    return 0


@add_premise(constant.Premise.TARGET_IS_ADMIRE)
def handle_target_is_admire(character_id: int) -> int:
    """
    校验角色当前的目标是否是自己的恋慕对象
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_id = character_data.target_character_id
    character_data.social_contact.setdefault(4, set())
    if target_id in character_data.social_contact[4]:
        return 1
    return 0


@add_premise(constant.Premise.PLAYER_IS_ADORE)
def handle_player_is_adore(character_id: int) -> int:
    """
    校验玩家是否是当前角色的爱慕对象
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    character_data.social_contact.setdefault(5, set())
    if 0 in character_data.social_contact[5]:
        return 1
    return 0


@add_premise(constant.Premise.EAT_SPRING_FOOD)
def handle_eat_spring_food(character_id: int) -> int:
    """
    校验角色是否正在食用春药品质的食物
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.behavior.food_quality == 4:
        return 1
    return 0


@add_premise(constant.Premise.IS_HUMOR_MAN)
def handle_is_humor_man(character_id: int) -> int:
    """
    校验角色是否是一个幽默的人
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    value = 0
    character_data: game_type.Character = cache.character_data[character_id]
    for i in {0, 1, 2, 5, 13, 14, 15, 16}:
        nature = character_data.nature[i]
        if nature > 50:
            value -= nature - 50
        else:
            value += 50 - nature
    if value < 0:
        value = 0
    return value


@add_premise(constant.Premise.TARGET_IS_BEYOND_FRIENDSHIP)
def handle_target_is_beyond_friendship(character_id: int) -> int:
    """
    校验是否对目标抱有超越友谊的想法
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if (
        character_data.target_character_id in character_data.social_contact_data
        and character_data.social_contact_data[character_data.target_character_id] > 2
    ):
        return character_data.social_contact_data[character_data.target_character_id]
    return 0


@add_premise(constant.Premise.IS_BEYOND_FRIENDSHIP_TARGET)
def handle_is_beyond_friendship_target(character_id: int) -> int:
    """
    校验目标是否对自己抱有超越友谊的想法
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if (
        character_id in target_data.social_contact_data
        and target_data.social_contact_data[character_id] > 2
    ):
        return target_data.social_contact_data[character_id]
    return 0


@add_premise(constant.Premise.SCENE_HAVE_OTHER_CHARACTER)
def handle_scene_have_other_target(character_id: int) -> int:
    """
    校验场景里是否有其他角色
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    scene_path = map_handle.get_map_system_path_str_for_list(character_data.position)
    scene_data: game_type.Scene = cache.scene_data[scene_path]
    return len(scene_data.character_list) - 1


@add_premise(constant.Premise.NO_WEAR_UNDERWEAR)
def handle_no_wear_underwear(character_id: int) -> int:
    """
    校验角色是否没穿上衣
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if 1 not in character_data.put_on or character_data.put_on[1] == None or character_data.put_on[1] == "":
        return 1
    return 0


@add_premise(constant.Premise.NO_WEAR_UNDERPANTS)
def handle_no_wear_underpants(character_id: int) -> int:
    """
    校验角色是否没穿内裤
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if 7 not in character_data.put_on or character_data.put_on[7] == None or character_data.put_on[7] == "":
        return 1
    return 0


@add_premise(constant.Premise.NO_WEAR_BRA)
def handle_no_wear_bra(character_id: int) -> int:
    """
    校验角色是否没穿胸罩
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if 6 not in character_data.put_on or character_data.put_on[6] == None or character_data.put_on[6] == "":
        return 1
    return 0


@add_premise(constant.Premise.NO_WEAR_PANTS)
def handle_no_wear_pants(character_id: int) -> int:
    """
    校验角色是否没穿裤子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if 2 not in character_data.put_on or character_data.put_on[2] == None or character_data.put_on[2] == "":
        return 1
    return 0


@add_premise(constant.Premise.NO_WEAR_SKIRT)
def handle_no_wear_skirt(character_id: int) -> int:
    """
    校验角色是否没穿短裙
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if 3 not in character_data.put_on or character_data.put_on[3] == None or character_data.put_on[3] == "":
        return 1
    return 0


@add_premise(constant.Premise.NO_WEAR_SHOES)
def handle_no_wear_shoes(character_id: int) -> int:
    """
    校验角色是否没穿鞋子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if 4 not in character_data.put_on or character_data.put_on[4] == None or character_data.put_on[4] == "":
        return 1
    return 0


@add_premise(constant.Premise.NO_WEAR_SOCKS)
def handle_no_wear_socks(character_id: int) -> int:
    """
    校验角色是否没穿袜子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if 5 not in character_data.put_on or character_data.put_on[5] == None or character_data.put_on[5] == "":
        return 1
    return 0


@add_premise(constant.Premise.WANT_PUT_ON)
def handle_want_put_on(character_id: int) -> int:
    """
    校验角色是否想穿衣服
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return (not character_data.no_wear) * 10


@add_premise(constant.Premise.HAVE_UNDERWEAR)
def handle_have_underwear(character_id: int) -> int:
    """
    校验角色是否拥有上衣
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if 1 in character_data.clothing and len(character_data.clothing[1]):
        return 1
    return 0


@add_premise(constant.Premise.HAVE_UNDERPANTS)
def handle_have_underpants(character_id: int) -> int:
    """
    校验角色是否拥有内裤
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if 7 in character_data.clothing and len(character_data.clothing[7]):
        return 1
    return 0


@add_premise(constant.Premise.HAVE_BRA)
def handle_have_bra(character_id: int) -> int:
    """
    校验角色是否拥有胸罩
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if 6 in character_data.clothing and len(character_data.clothing[6]):
        return 1
    return 0


@add_premise(constant.Premise.HAVE_PANTS)
def handle_have_pants(character_id: int) -> int:
    """
    校验角色是否拥有裤子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if 2 in character_data.clothing and len(character_data.clothing[2]):
        return 1
    return 0


@add_premise(constant.Premise.HAVE_SKIRT)
def handle_have_skirt(character_id: int) -> int:
    """
    校验角色是否拥有短裙
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if 3 in character_data.clothing and len(character_data.clothing[3]):
        return 1
    return 0


@add_premise(constant.Premise.HAVE_SHOES)
def handle_have_shoes(character_id: int) -> int:
    """
    校验角色是否拥有鞋子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if 4 in character_data.clothing and len(character_data.clothing[4]):
        return 1
    return 0


@add_premise(constant.Premise.HAVE_SOCKS)
def handle_have_socks(character_id: int) -> int:
    """
    校验角色是否拥有袜子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if 5 in character_data.clothing and len(character_data.clothing[5]):
        return 1
    return 0


@add_premise(constant.Premise.IN_DORMITORY)
def handle_in_dormitory(character_id: int) -> int:
    """
    校验角色是否在宿舍中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_position = map_handle.get_map_system_path_str_for_list(character_data.position)
    return now_position == character_data.dormitory


@add_premise(constant.Premise.CHEST_IS_NOT_CLIFF)
def handle_chest_is_not_cliff(character_id: int) -> int:
    """
    校验角色胸围是否不是绝壁
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return attr_calculation.judge_chest_group(character_data.chest.now_chest)
