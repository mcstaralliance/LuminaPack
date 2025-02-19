import os
import shutil
import sys
import subprocess
import datetime
import winreg
import glob

CLEAN_ITEMS = {
    'folders': [
        '.physics_mod_cache',
        'assets',
        'cloth_local',
        'crash-reports',
        'defaultconfigs',
        'libraries',
        'local',
        'logs',
        'modernfix',
        'patchouli_books',
        'saves',
        'schematics',
        'screenshots'
    ],
    'files': [
        'authlib-injector.log',
        'hs_err*.log',
        'launcher_profiles.json',
        'usercache.json',
        'usernamecache.json',
        'patchouli_data.json',
        'replay*.log',
        'rhino.local.properties',
        'servers.dat_old'
    ]
}

def find_winrar():
    """自动检测WinRAR安装路径"""
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WinRAR", 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY) as key:
            path = winreg.QueryValueEx(key, "exe64")[0]
            if os.path.exists(path):
                return path.replace("WinRAR.exe", "rar.exe")
    except:
        pass
    
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WinRAR", 0, winreg.KEY_READ | winreg.KEY_WOW64_32KEY) as key:
            path = winreg.QueryValueEx(key, "exe32")[0]
            if os.path.exists(path):
                return path.replace("WinRAR.exe", "rar.exe")
    except:
        pass

    common_paths = [
        r"C:\Program Files\WinRAR\rar.exe",
        r"C:\Program Files (x86)\WinRAR\rar.exe"
    ]
    for path in common_paths:
        if os.path.exists(path):
            return path
    return None

def show_tutorial():
    """显示使用教程"""
    tutorial = """
=== LuminaPack 使用教程 ===

【准备工作】
1. 确保已安装 WinRAR (如未安装，请先安装)
2. 将本程序放在需要打包的 .minecraft 文件夹同级目录

【使用步骤】
1. 运行程序后，会自动检测同目录下的 .minecraft 文件夹
2. 程序会自动创建备份并清理不必要文件
3. 最后生成一个自解压程序（exe文件）

【注意事项】
- 生成的exe文件可以分享给其他人
- 运行exe时会自动解压到当前目录
- 解压完成后会自动打开目标文件夹

按Enter键继续...
"""
    print(tutorial)
    input()

def check_minecraft_dir():
    """检测当前目录下的.minecraft文件夹是否存在"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.join(current_dir, '.minecraft')
    
    if not os.path.exists(base_dir):
        print(f"[错误] 当前目录未找到.minecraft文件夹: {base_dir}")
        input("按任意键退出...")
        sys.exit(1)
    return base_dir

def create_backup(src_dir):
    """创建完整备份目录（不清理）"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(os.path.dirname(src_dir), f"mc_backup_{timestamp}")
    
    try:
        shutil.copytree(src_dir, backup_dir)
        print(f"已创建完整备份副本：{backup_dir}")
        return backup_dir
    except Exception as e:
        print(f"备份失败：{str(e)}")
        sys.exit(1)

def clean_backup(backup_dir):
    """清理备份副本（不影响原始文件）"""
    try:
        for folder in CLEAN_ITEMS['folders']:
            target = os.path.join(backup_dir, folder)
            if os.path.exists(target):
                shutil.rmtree(target)
                print(f"已清理文件夹：{folder}")

        for pattern in CLEAN_ITEMS['files']:
            for file_path in glob.glob(os.path.join(backup_dir, pattern)):
                os.remove(file_path)
                print(f"已清理文件：{os.path.basename(file_path)}")

        versions_dir = os.path.join(backup_dir, 'versions')
        if os.path.exists(versions_dir):
            versions = [v for v in os.listdir(versions_dir) if os.path.isdir(os.path.join(versions_dir, v))]
            if versions:
                latest = max(versions, key=lambda x: os.path.getmtime(os.path.join(versions_dir, x)))
                for version in versions:
                    if version != latest:
                        shutil.rmtree(os.path.join(versions_dir, version))
                print(f"保留最新版本：{latest}")

        return True
    except Exception as e:
        print(f"清理失败：{str(e)}")
        return False

def read_sfx_config():
    """读取SFX配置文件（终极加固版）"""
    # 硬编码默认值
    DEFAULT_TITLE = 'LuminaPack 安装向导'
    DEFAULT_DESC = '正在解压到当前目录...'
    
    config = {
        'title': DEFAULT_TITLE,
        'description': DEFAULT_DESC
    }

    try:
        import configparser
        cfg = configparser.ConfigParser()
        
        # 强制添加Settings段避免KeyError
        if not cfg.has_section('Settings'):
            cfg.add_section('Settings')
            
        # 带异常捕获的读取
        try:
            cfg.read('sfx_config.ini', encoding='utf-8-sig')
        except UnicodeDecodeError:
            print("检测到文件编码错误，尝试GBK编码...")
            cfg.read('sfx_config.ini', encoding='gbk')
            
        # 直接读取键值
        title = cfg.get('Settings', 'title', fallback=DEFAULT_TITLE)
        description = cfg.get('Settings', 'description', fallback=DEFAULT_DESC)
        
        # 过滤非法字符
        config['title'] = str(title).strip()[:50] or DEFAULT_TITLE
        config['description'] = str(description).strip()[:100] or DEFAULT_DESC
        
    except Exception as e:
        print(f"配置读取异常，已使用默认值: {str(e)}")
        config = {
            'title': DEFAULT_TITLE,
            'description': DEFAULT_DESC
        }
    
    # 最终验证
    config['title'] = config.get('title', DEFAULT_TITLE)
    config['description'] = config.get('description', DEFAULT_DESC)
    
    return config

def create_sfx(backup_dir, output_exe, folder_name):
    """生成自解压程序"""
    temp_parent = os.path.join(os.path.dirname(output_exe), "temp_packaging")
    config_path = os.path.join(os.path.dirname(__file__), "sfx_config.txt")
    
    try:
        sfx_config = read_sfx_config()
        
        # 需要复制的额外文件列表（可扩展）
        additional_files = [
            'hmcl.json',
            'HMCL-3.6.11.exe'
        ]
        
        # 创建带父文件夹的临时目录结构
        target_dir = os.path.join(temp_parent, folder_name)
        
        # 复制.minecraft文件夹
        shutil.copytree(backup_dir, os.path.join(target_dir, '.minecraft'))
        
        # 复制并清理hmcl.json
        original_dir = os.path.dirname(backup_dir)
        for file_name in additional_files:
            src = os.path.join(original_dir, file_name)
            dst = os.path.join(target_dir, file_name)
            
            if file_name == 'hmcl.json':
                try:
                    if not os.path.exists(src):
                        print("[提示] 未找到hmcl.json，跳过处理")
                        continue
                    
                    import json
                    with open(src, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # 清理特定路径字段
                    data.pop('commonpath', None)
                    
                    # 清理所有配置项中的gameDir
                    if 'configurations' in data:
                        for conf in data['configurations'].values():
                            if 'global' in conf:
                                conf['global'].pop('gameDir', None)
                    
                    with open(dst, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    print(f"已清理并添加：{file_name}")
                    
                except json.JSONDecodeError:
                    print(f"[警告] {file_name} 格式错误，已跳过")
                except Exception as e:
                    print(f"处理{file_name}失败：{str(e)}")
            else:
                try:
                    shutil.copy2(src, dst)
                    print(f"已添加额外文件：{file_name}")
                except FileNotFoundError:
                    print(f"[警告] 未找到额外文件：{file_name}")
                except Exception as e:
                    print(f"复制{file_name}失败：{str(e)}")

        # 获取最终输出路径的绝对路径
        output_dir = os.path.abspath(os.path.dirname(output_exe))
        
        config_content = f"""\
{{{{注释}}}}
; 自解压脚本配置
Title={sfx_config['title']}
Text={sfx_config['description']}
BeginPrompt=确定要解压 Minecraft 客户端吗？
Progress=yes
Overwrite=1
Path="{output_dir}"
Silent=0
SavePath
Presetup=echo 正在解压，请稍候...
"""

        with open(config_path, 'w', encoding='gbk') as f:
            f.write(config_content)

        cmd = [
            WINRAR_PATH,
            "a", "-ep1", "-r", "-m5",
            "-sfx", f"-z{config_path}",
            "-s",
            output_exe,
            temp_parent + "\\*"  # 打包整个临时父目录
        ]

        subprocess.run(cmd, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        print(f"\n自解压程序已生成：{output_exe}")
        if os.path.exists(config_path):
            os.remove(config_path)
        # 清理临时目录
        shutil.rmtree(temp_parent)
        return True
    except Exception as e:
        print(f"致命错误: {str(e)}")
        # 清理所有可能残留的文件
        if os.path.exists(config_path):
            os.remove(config_path)
        if os.path.exists(temp_parent):
            shutil.rmtree(temp_parent)
        return False

def main():
    backup_dir = None
    try:
        show_tutorial()
        
        print("Minecraft客户端打包工具")
        print("=" * 40)

        global WINRAR_PATH
        WINRAR_PATH = find_winrar()
        if not WINRAR_PATH:
            print("[错误] 未找到WinRAR，请确保已正确安装WinRAR")
            print("常见安装位置：")
            print("- C:\\Program Files\\WinRAR")
            print("- C:\\Program Files (x86)\\WinRAR")
            input("按任意键退出...")
            sys.exit(1)
        print(f"[已找到] WinRAR路径: {WINRAR_PATH}")

        folder_name = input("请输入解压后的文件夹名称（例如：MyMinecraftClient）: ").strip()
        while not folder_name or any(c in folder_name for c in '\\/:*?"<>|'):
            print("名称不能包含特殊字符且不能为空！")
            folder_name = input("请重新输入有效的文件夹名称: ").strip()

        original_dir = check_minecraft_dir()
        print(f"[1/5] 验证原始目录：{original_dir}")

        backup_dir = create_backup(original_dir)
        print(f"[2/5] 已创建完整备份副本")

        print(f"[3/5] 正在清理临时文件...")
        if clean_backup(backup_dir):
            print("清理完成，准备打包...")
        else:
            print("清理过程中出现问题")

        output_name = f"{folder_name}_Installer.exe"
        print(f"[4/5] 正在生成安装程序...")
        success = create_sfx(backup_dir, output_name, folder_name)
        
        if not success:
            print("\n[错误] 打包过程失败")
            if backup_dir and os.path.exists(backup_dir):
                shutil.rmtree(backup_dir)
            temp_parent = os.path.join(os.path.dirname(output_name), "temp_packaging")
            if os.path.exists(temp_parent):
                shutil.rmtree(temp_parent)
            sys.exit(1)
            
        print("\n操作成功！生成文件信息：")
        print(f"大小：{round(os.path.getsize(output_name)/1024/1024, 1)} MB")
        print(f"路径：{os.path.abspath(output_name)}")

        print("[5/5] 正在清理临时文件...")
        # 清理备份目录
        if os.path.exists(backup_dir):
            shutil.rmtree(backup_dir)
            print("已清理临时备份")
        # 清理临时打包目录（冗余检查）
        temp_parent = os.path.join(os.path.dirname(output_name), "temp_packaging")
        if os.path.exists(temp_parent):
            shutil.rmtree(temp_parent)
            print("已清理临时打包目录")

        input("\n按Enter键退出...")
    except Exception as e:
        print(f"\n未捕获的异常: {str(e)}")
        # 最终清理
        if backup_dir and os.path.exists(backup_dir):
            shutil.rmtree(backup_dir)
        temp_parent = os.path.join(os.path.dirname(__file__), "temp_packaging")
        if os.path.exists(temp_parent):
            shutil.rmtree(temp_parent)
        sys.exit(1)

if __name__ == "__main__":
    main()