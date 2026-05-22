import os
import re

# 定义频道分组规则
def get_group_title(channel_name):
    name_upper = channel_name.upper()
    
    # 1. 央视频道
    if "CCTV" in name_upper or "CGTN" in name_upper:
        return "央视频道"
    
    # 2. 湖北频道
    if any(x in channel_name for x in ["湖北", "武汉", "蔡甸", "房县", "阳新"]):
        return "湖北频道"
    
    # 3. 卫视频道
    if "卫视" in channel_name:
        return "卫视频道"
    
    # 4. 少儿/动漫频道
    if any(x in channel_name for x in ["卡通", "少儿", "动漫", "玩具"]):
        return "少儿频道"
    
    # 5. 影视频道
    if any(x in channel_name for x in ["影迷", "动作", "剧场", "电影", "影视", "电视剧"]):
        return "影视频道"
    
    # 6. 体育频道
    if any(x in channel_name for x in ["体育", "足球", "高尔夫", "网球", "台球", "垂钓", "乒羽", "兵器", "武术", "赛事"]):
        return "体育频道"
    
    # 7. 教育频道
    if any(x in name_upper for x in ["CETV", "教育", "中学生", "学堂", "金色学堂"]):
        return "教育频道"
    
    # 8. 港澳台/海外频道
    if any(x in channel_name for x in ["凤凰", "港台", "翡翠", "TVB"]):
        return "港澳台"
    
    # 9. 购物频道
    if any(x in channel_name for x in ["购物", "消费", "精选"]):
        return "购物频道"
    
    # 10. 数字/特种频道（默认兜底）
    return "数字特种"

def parse_txt_file(txt_path):
    channels = []
    if not os.path.exists(txt_path):
        return channels
    
    with open(txt_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
        
    i = 0
    # 按照 3 行一个循环进行解析
    while i < len(lines):
        if i + 2 < len(lines) and "copy" in lines[i+1].lower():
            name = lines[i]
            url = lines[i+2]
            channels.append((name, url))
            i += 3
        else:
            i += 1  # 容错处理
    return channels

def main():
    config_dir = "config"
    output_file = "live.m3u"  # 根目录下的合并输出文件名
    
    if not os.path.exists(config_dir):
        print("未找到 config 目录")
        return

    # 过滤出所有的 .txt 文件
    txt_files = [f for f in os.listdir(config_dir) if f.endswith(".txt")]
    
    # 按照文件名中的数字进行自然排序（防止 10.txt 排在 2.txt 前面）
    def extract_number(filename):
        match = re.search(r'(\d+)', filename)
        return int(match.group(1)) if match else filename

    txt_files.sort(key=extract_number)

    all_channels = []
    # 依次解析每个 txt 文件并合并
    for file_name in txt_files:
        txt_path = os.path.join(config_dir, file_name)
        channels = parse_txt_file(txt_path)
        all_channels.extend(channels)
        print(f"已解析 {file_name}，获取到 {len(channels)} 个频道")

    # 写入统一的 M3U 文件到根目录
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n")
        for name, url in all_channels:
            group = get_group_title(name)
            f.write(f'#EXTINF:-1 tvg-name="{name}" group-title="{group}",{name}\n')
            f.write(f"{url}\n")
            
    print(f"合并完成！已生成根目录下的 M3U 文件: {output_file} (总计 {len(all_channels)} 个频道)")

if __name__ == "__main__":
    main()
