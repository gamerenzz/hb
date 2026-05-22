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
    # 数值越小排在越前面
    priorities = {
        "央视频道": 0,
        "卫视频道": 1,
        "湖北频道": 2,
        "港澳台": 3,
        "影视频道": 4,
        "数字特种": 5,
        # 其他未指定的分组默认优先级为 50（排在数字特种之后，4K频道之前）
        "4K频道": 99   # 确保 4K 频道永远在最后
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

    # 使用字典将频道按分组名归类存储
    grouped_channels = defaultdict(list)

    # 依次解析每个 txt 文件并将频道分类
    for file_name in txt_files:
        txt_path = os.path.join(config_dir, file_name)
        channels = parse_txt_file(txt_path)
        for name, url in channels:
            group = get_group_title(name)
            grouped_channels[group].append((name, url))
        print(f"已解析 {file_name}，获取到 {len(channels)} 个频道")

    # 对现有的分组名称进行排序
    sorted_group_names = sorted(grouped_channels.keys(), key=sort_groups_key)

    # 按照排好的分组顺序写入到 live.m3u
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n")
        for group in sorted_group_names:
            for name, url in grouped_channels[group]:
                f.write(f'#EXTINF:-1 tvg-name="{name}" group-title="{group}",{name}\n')
                f.write(f"{url}\n")
            
    print(f"排序及合并完成！已生成根目录下的 M3U 文件: {output_file} (含有 {len(sorted_group_names)} 个分组)")

if __name__ == "__main__":
    main()
