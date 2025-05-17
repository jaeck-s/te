# 提取器实现包初始化
from .rpy_properties import (
    extract_description, 
    extract_purchase_notification, 
    extract_unlock_notification,
    extract_title_text,
    extract_description_text,
    extract_renpy_notify,
    extract_name,
    extract_dict_keys,
    extract_sponsor_description,
    extract_tooltip,
    extract_text,
    extract_textbutton,
    extract_available_tooltip,      # 添加新提取器
    extract_unavailable_tooltip,    # 添加新提取器
    extract_unavailable_notification  # 添加新提取器
)
from .json_fields import extract_display_name, extract_person_name, extract_json_description
