#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import sys
from types import FunctionType
from Script.Config import normal_config
from Script.Core import game_type, cache_control

cache_control.cache = game_type.Cache()
normal_config.init_normal_config()


from Script.Core import get_text
from Script.Config import game_config, map_config, name_config

_: FunctionType = get_text._
""" 翻译api """

if sys.version_info < (3, 9, 0):
    print(_("python3版本过旧(低于python3.9.0),请升级"))
    exit(0)


game_config.init()
map_config.init_map_data()
name_config.init_name_data()


from Script.Design import start_flow, handle_premise, game_time
from Script.Core import game_init
import Script.Settle
import Script.StateMachine
import Script.UI.Flow

game_time.init_time()
game_init.run(start_flow.start_frame)
