from Script.Core import cache_contorl, text_loading, era_print, constant
from Script.Design import cmd_button_queue, map_handle, game_time


def see_instruct_head_panel() -> list:
    """
    绘制指令面板的头部过滤器面板
    Return arguments:
    list -- 绘制的按钮列表
    """
    era_print.little_title_print(
        text_loading.get_text_data(constant.FilePath.STAGE_WORD_PATH, "146")
    )
    instruct_data = text_loading.get_text_data(
        constant.FilePath.CMD_PATH, constant.CmdMenu.INSTRUCT_HEAD_PANEL
    )
    if cache_contorl.instruct_filter == {}:
        cache_contorl.instruct_filter = {
            instruct: 0 for instruct in instruct_data
        }
        cache_contorl.instruct_filter["Dialogue"] = 1
    style_data = {
        instruct_data[instruct]: "selectmenu"
        for instruct in instruct_data
        if cache_contorl.instruct_filter[instruct] == 0
    }
    on_style_data = {
        instruct_data[instruct]: "onselectmenu"
        for instruct in instruct_data
        if cache_contorl.instruct_filter[instruct] == 0
    }
    era_print.line_feed_print(
        text_loading.get_text_data(constant.FilePath.STAGE_WORD_PATH, "147")
    )
    return cmd_button_queue.option_str(
        None,
        len(instruct_data),
        "center",
        False,
        False,
        list(instruct_data.values()),
        "",
        list(instruct_data.keys()),
        style_data,
        on_style_data,
    )


instruct_data = text_loading.get_text_data(
    constant.FilePath.CMD_PATH, constant.CmdMenu.INSTRUCT_PANEL
)
instruct_text_data = {
    instruct: instruct_data[instruct_type][instruct]
    for instruct_type in instruct_data
    for instruct in instruct_data[instruct_type]
}
instruct_cmd_id_data = {
    list(instruct_text_data.keys())[i]: i
    for i in range(len(instruct_text_data))
}
instruct_id_cmd_data = {
    instruct_cmd_id_data[instruct]: instruct
    for instruct in instruct_cmd_id_data
}


def instract_list_panel() -> list:
    """
    绘制指令面板
    Return arguments:
    list -- 绘制的按钮列表
    """
    instruct_list = [
        instruct
        for instruct_type in instruct_data
        if instruct_type in cache_contorl.instruct_filter
        and cache_contorl.instruct_filter[instruct_type]
        for instruct in instruct_data[instruct_type]
        if judge_instract_available(instruct)
    ]
    return_data = [
        str(instruct_cmd_id_data[instruct]) for instruct in instruct_list
    ]
    cmd_data = [
        "      "
        + cmd_button_queue.id_index(return_data[i])
        + instruct_text_data[instruct_list[i]]
        for i in range(len(instruct_list))
    ]
    if len(return_data) > 0:
        cmd_button_queue.option_str(
            None,
            5,
            "left",
            False,
            False,
            cmd_data,
            "",
            return_data,
            {},
            {},
            False,
        )
    return return_data


def judge_instract_available(instract: str) -> bool:
    """
    校验指令是否可用
    Keyword arguments:
    instract -- 指令Id
    Return arguments:
    bool -- 可用性校验
    """
    config_data = text_loading.get_game_data(constant.FilePath.INSTRUCT_PATH)[
        instract
    ]
    if len(config_data) == 0:
        return 1
    if "MustTarget" in config_data and config_data["MustTarget"]:
        if not cache_contorl.now_character_id:
            return 0
    if "ItemTag" in config_data:
        now_judge = 1
        for item in cache_contorl.character_data[0].item:
            if (
                cache_contorl.character_data[0].item[item][
                    "ItemTag"
                ]
                == config_data["ItemTag"]
            ):
                now_judge = 0
                break
        if now_judge:
            return 0
    if "Item" in config_data:
        now_judge = 1
        for item in cache_contorl.character_data[0].item:
            if item == config_data["Item"]:
                now_judge = 0
                break
        if now_judge:
            return 0
    if "SceneTag" in config_data:
        scene_data = cache_contorl.scene_data[
            map_handle.get_map_system_path_str_for_list(
                cache_contorl.character_data[0].position
            )
        ]
        if scene_data["SceneTag"] != config_data["SceneTag"]:
            return 0
    if "TargetClothingTag" in config_data:
        if (
            cache_contorl.character_data[
                cache_contorl.now_character_id
            ].put_on[config_data["TargetClothingTag"]]
            == ""
        ):
            return 0
    if "TargetSex" in config_data:
        if (
            cache_contorl.character_data[
                cache_contorl.now_character_id
            ].sex
            not in config_data["TargetSex"]
        ):
            return 0
    if "TargetUnderwear" in config_data:
        if (
            cache_contorl.character_data[
                cache_contorl.now_character_id
            ].put_on["Underwear"]
            != ""
        ):
            if not config_data["TargetUnderwear"]:
                return 0
        else:
            if config_data["TargetUnderwear"]:
                return 0
    if "TimeSlice" in config_data:
        if (
            config_data["TimeSlice"]
            != game_time.get_now_time_slice(0)["TimeSlice"]
        ):
            return 0
    if "Occupation" in config_data:
        if (
            config_data["Occupation"]
            != cache_contorl.character_data[0].occupation
        ):
            return 0
    return 1
