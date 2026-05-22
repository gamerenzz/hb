import os
import re
from collections import defaultdict

# 1. 定义频道分组规则
def get_group_title(channel_name):
    name_upper = channel_name.upper()
    
    # 优先提取 4K 频道
    if "4K" in name_upper:
        return "4K频道"
    
    # 央视频道
    if "CCTV" in name_upper or "CGTN" in name_upper:
        return "央视频道"
    
    # 湖北频道
    if any(x in channel_name for x in ["湖北", "武汉", "蔡甸", "房县", "阳新"]):
        return "湖北频道"
    
    # 卫视频道
    if "卫视" in channel_name:
        return "卫视频道"
    
    # 少儿/动漫频道
    if any(x in channel_name for x in ["卡通", "少儿", "动漫", "玩具"]):
        return "少儿频道"
    
    # 影视频道
    if any(x in channel_name for x in ["影迷", "动作", "剧场", "电影", "影视", "电视剧"]):
        return "影视频道"
    
    # 体育频道
    if any(x in channel_name for x in ["体育", "足球", "高尔夫", "网球", "台球", "垂钓", "乒羽", "兵器", "武术", "赛事"]):
        return "体育频道"
    
    # 教育频道
    if any(x in name_upper for x in ["CETV", "教育", "中学生", "学堂", "金色学堂"]):
        return "教育频道"
    
    # 港澳台/海外频道
    if any(x in channel_name for x in ["凤凰", "港台", "翡翠", "TVB"]):
        return "港澳台"
    
    # 购物频道
    if any(x in channel_name for x in ["购物", "消费", "精选"]):
        return "购物频道"
    
    # 数字/特种频道（默认兜底）
    return "数字特种"

# 2. 定义分组间的排序优先级
def sort_groups_key(group_name):
    priorities = {
        "央视频道": 0,
        "卫视频道": 1,
        "湖北频道": 2,
        "港澳台": 3,
        "影视频道": 4,
        "数字特种": 5,
        "4K频道": 99   # 4K 频道永远在最后
    }
    priority = priorities.get(group_name, 50)
    return (priority, group_name)

def parse_txt_file(txt_path):
    channels = []
    if not os.path.exists(txt_path):
        return channels
    
    with open(txt_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
        
    i = 0
    while i < len(lines):
        if i + 2 < len(lines) and "copy" in lines[i+1].lower():
            name = lines[i]
            url = lines[i+2]
            channels.append((name, url))
            i += 3
        else:
            i += 1
    return channels

def main():
    config_dir = "config"
    output_file = "live.m3u"
    
    if not os.path.exists(config_dir):
        print("未找到 config 目录")
        return

    # 过滤出所有的 .txt 文件并进行自然排序
    txt_files = [f for f in os.listdir(config_dir) if f.endswith(".txt")]
    def extract_number(filename):
        match = re.search(r'(\d+)', filename)
        return int(match.group(1)) if match else filename
    txt_files.sort(key=extract_number)

    # 记录基础频道名（去除了HD/SD后的名字）首次出现的顺序，用于保持频道的自然排布
    base_name_order = {}
    # 使用字典存储分组频道，结构为：{分组名: [(净化后的名字, URL, 原始后缀类型, 基础名字)]}
    grouped_channels = defaultdict(list)

    # 依次解析每个 txt 文件
    for file_name in txt_files:
        txt_path = os.path.join(config_dir, file_name)
        channels = parse_txt_file(txt_path)
        
        for original_name, url in channels:
            # 1. 4K 频道不作更名处理
            if "4K" in original_name.upper():
                suffix_type = 'OTHER'
                cleaned_name = original_name
            else:
                # 2. 去除名字末尾的 HD 或 SD
                if original_name.upper().endswith("HD"):
                    suffix_type = 'HD'
                    cleaned_name = original_name[:-2].strip()
                elif original_name.upper().endswith("SD"):
                    suffix_type = 'SD'
                    cleaned_name = original_name[:-2].strip()
                else:
                    suffix_type = 'OTHER'
                    cleaned_name = original_name
            
            base_name = cleaned_name
            # 记录频道出现的先后顺序
            if base_name not in base_name_order:
                base_name_order[base_name] = len(base_name_order)
                
            group = get_group_title(original_name)
            grouped_channels[group].append((cleaned_name, url, suffix_type, base_name))
            
        print(f"已解析 {file_name}，获取到 {len(channels)} 个频道")

    # 对现有的分组名称进行排序
    sorted_group_names = sorted(grouped_channels.keys(), key=sort_groups_key)

    # 写入到 live.m3u
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n")
        for group in sorted_group_names:
            channels_in_group = grouped_channels[group]
            
            # 3. 排序函数：确保相同 base_name 挨在一起，且 HD 排在 SD 前面
            def channel_sort_key(item):
                cleaned_name, url, suffix_type, base_name = item
                base_idx = base_name_order.get(base_name, 999999)
                # 定义后缀优先级值：HD 优先(0)，无后缀次之(1)，SD 最后(2)
                suffix_order = 0 if suffix_type == 'HD' else (2 if suffix_type == 'SD' else 1)
                return (base_idx, suffix_order)
                
            sorted_channels = sorted(channels_in_group, key=channel_sort_key)
            
            for cleaned_name, url, suffix_type, base_name in sorted_channels:
                f.write(f'#EXTINF:-1 tvg-name="{cleaned_name}" group-title="{group}",{cleaned_name}\n')
                f.write(f"{url}\n")
            
    print(f"排序及合并完成！已生成无HD/SD后缀的 M3U 文件: {output_file}")

if __name__ == "__main__":
    main()
