# LuminaPack 🎮✨

[![License](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-green.svg)](https://www.python.org/)
[![WinRAR Required](https://img.shields.io/badge/WinRAR-Required-orange.svg)](https://www.win-rar.com/)

## 🌟 功能特性
- 🧹 智能清理非必要文件  
- 🔄 自动创建完整备份  
- 🎁 生成自解压安装程序  
- 🔒 HMCL配置安全处理  
- 📦 支持添加额外文件  
- 🛡️ 四级错误处理机制  
- 📂 自动清理临时文件  

## 🛠️ 环境要求
- **操作系统**: Windows 10/11  
- **Python**: 3.8+ ([下载](https://www.python.org/downloads/))  
- **WinRAR**: 已安装 ([下载](https://www.win-rar.com/))  
- **磁盘空间**: ≥客户端大小×2  

## 🚀 快速开始
1. 准备目录结构：

LuminaPack/
├── .minecraft/    # 必需
├── hmcl.json      # 可选
├── HMCL-*.exe     # 可选
└── LuminaPack.py  # 主程序

2. 运行命令：

```bash
python LuminaPack.py
```

3. 按提示输入文件夹名称（示例）：
```bash
> 请输入解压后的文件夹名称: MyMinecraft
```

## ⚙️ 配置文件
创建 `sfx_config.ini`：
```ini
[Settings]
title = 我的游戏客户端
description = 正在解压文件...
```

支持编码格式：  
✅ UTF-8 with BOM (推荐)  
✅ GBK  
✅ ANSI  

## 📖 完整流程
1. **验证目录**  
   - 检查.minecraft文件夹是否存在
2. **创建备份**  
   - 生成带时间戳的备份副本
3. **清理文件**  
   - 删除缓存/日志等非必要文件
4. **打包程序**  
   - 生成自解压安装程序
5. **清理临时文件**  
   - 自动删除备份和临时目录

## 🚨 注意事项
⚠️ 命名规范：  
- 禁止使用特殊字符 `\/:*?"<>|`  
- 建议使用英文命名  

💡 最佳实践：  
- 操作前关闭所有Minecraft相关进程  
- 保留至少10GB可用空间  
- 定期清理旧备份文件  

## 📜 许可证
[GNU GPLv3](https://www.gnu.org/licenses/gpl-3.0) © 2025 LDS_XiaoYe

---

## 🚑 故障排查
### ❌ 出现KeyError: 'title

1. 检查配置文件编码：
```bash
file sfx_config.ini
# 应显示: UTF-8 Unicode (with BOM) text
```

2. 验证文件内容：
```ini
[Settings]
title = 有效标题
description = 有效描述
```

3. 临时解决方案：
```bash
rm sfx_config.ini  # 删除配置文件使用默认值
```

### ❌ 找不到 WinRAR

1. 手动指定路径：
```python
# 修改LuminaPack.py中的路径
common_paths = [
    r"C:\Your\Custom\Path\WinRAR\rar.exe"
]
```
2. 验证安装：
```powershell
where rar.exe
# 应返回有效路径
```
