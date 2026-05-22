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
    if any(x in channel_name for x in ["体育", "足球", "高尔夫", "网球", "台球", "垂钓", "兵器", "武术", "健身", "赛事"]):
        return "体育频道"
    
    # 7. 教育频道
    if any(x in name_upper for x in ["CETV", "教育", "中学生", "学堂", "金色学堂"]):
        return "教育频道"
    
    # 8. 港澳台/海外频道
    if any(x in channel_name for x in ["凤凰", "翡翠", "TVB"]):
        return "港澳台"
    
    # 9. 购物频道
    if any(x in channel_name for x in ["购物", "消费", "精选"]):
        return "购物频道"
    
    # 10. 数字/特种频道（默认兜底）
    return "数字特种"

def convert_txt_to_m3u(txt_path, m3u_path):
    if not os.path.exists(txt_path):
        return
    
    with open(txt_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
        
    channels = []
    i = 0
    # 按照 3 行一个循环进行解析（名称 -> copy to clip -> URL）
    while i < len(lines):
        if i + 2 < len(lines) and "copy" in lines[i+1].lower():
            name = lines[i]
            url = lines[i+2]
            channels.append((name, url))
            i += 3
        else:
            i += 1  # 容错处理：不符合格式则向下移动一行

    # 写入 M3U 文件
    with open(m3u_path, 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n")
        for name, url in channels:
            group = get_group_title(name)
            # 写入 M3U 标准格式
            f.write(f'#EXTINF:-1 tvg-name="{name}" group-title="{group}",{name}\n')
            f.write(f"{url}\n")
            
    print(f"成功转换: {txt_path} -> {m3u_path} (共 {len(channels)} 个频道)")

def main():
    config_dir = "config"
    if not os.path.exists(config_dir):
        print("未找到 config 目录")
        return

    # 遍历 config 目录下所有的 .txt 文件
    for file_name in os.listdir(config_dir):
        if file_name.endswith(".txt"):
            txt_path = os.path.join(config_dir, file_name)
            m3u_name = file_name.replace(".txt", ".m3u")
            m3u_path = os.path.join(config_dir, m3u_name)
            convert_txt_to_m3u(txt_path, m3u_path)

if __name__ == "__main__":
    main()
