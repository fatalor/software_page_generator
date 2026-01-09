#!/usr/bin/env python3
"""
软件页面生成器 - 构建脚本
生成纯内容HTML（仅包含内容标签，无包装div）
"""

import sys
import pyperclip
import re
import os
from pathlib import Path
from typing import Dict, Any, Tuple, List

# 添加模板目录到路径
sys.path.insert(0, str(Path(__file__).parent / 'templates'))

try:
    from templates.page_template import (
        generate_wordpress_content, 
        generate_html_embed,
        parse_config_file,
        get_software_title
    )
except ImportError as e:
    print(f"导入模板模块失败: {e}")
    print("请确保 templates/page_template.py 文件存在")
    sys.exit(1)


def sanitize_filename(filename: str) -> str:
    """
    清理文件名，移除不合法字符
    
    Args:
        filename: 原始文件名
        
    Returns:
        清理后的文件名
    """
    # 移除Windows文件名不允许的字符: \ / : * ? " < > |
    filename = re.sub(r'[\\/*?:"<>|]', '', filename)
    # 替换空格为下划线
    filename = filename.replace(' ', '_')
    # 限制长度
    if len(filename) > 100:
        filename = filename[:100]
    return filename


def generate_pure_content(software_info: Dict[str, Any]) -> str:
    """
    生成纯HTML内容（仅包含内容标签，无包装div）
    
    Args:
        software_info: 软件信息字典
        
    Returns:
        纯HTML内容字符串
    """
    # 获取WordPress格式内容
    wp_content = generate_wordpress_content(software_info)
    
    # 如果额外信息为空，移除相关标签
    extra_info = software_info.get('额外信息', '')
    if not extra_info or (isinstance(extra_info, str) and not extra_info.strip()):
        # 移除空白的额外信息部分
        import re
        # 移除包含空额外信息的段落
        wp_content = re.sub(r'\n\n<p></p>\n?', '', wp_content)
        wp_content = re.sub(r'\n\n<p>\s*</p>\n?', '', wp_content)
    
    return wp_content


def generate_html_file(software_info: Dict[str, Any], output_dir: Path) -> Path:
    """
    生成纯内容HTML文件到output目录
    
    Args:
        software_info: 软件信息字典
        output_dir: 输出目录
        
    Returns:
        生成的HTML文件路径
    """
    # 获取软件标题
    software_title = software_info.get('标题', 'software')
    
    # 清理文件名
    safe_title = sanitize_filename(software_title)
    
    # 生成纯HTML内容（无包装div）
    html_content = generate_pure_content(software_info)
    
    # 确保输出目录存在
    output_dir.mkdir(exist_ok=True)
    
    # 生成HTML文件路径
    html_filename = f"{safe_title}.html"
    html_file = output_dir / html_filename
    
    # 写入HTML文件
    html_file.write_text(html_content, encoding='utf-8')
    
    return html_file


def generate_preview_file(software_info: Dict[str, Any], preview_dir: Path) -> Path:
    """
    生成预览HTML文件到previews目录
    
    Args:
        software_info: 软件信息字典
        preview_dir: 预览目录
        
    Returns:
        生成的预览文件路径
    """
    # 获取软件标题
    software_title = software_info.get('标题', 'software')
    
    # 清理文件名
    safe_title = sanitize_filename(software_title)
    
    # 生成预览HTML
    preview_html = generate_html_embed(software_info)
    
    # 确保预览目录存在
    preview_dir.mkdir(exist_ok=True)
    
    # 生成预览文件路径
    preview_filename = f"{safe_title}_preview.html"
    preview_file = preview_dir / preview_filename
    
    # 写入预览文件
    preview_file.write_text(preview_html, encoding='utf-8')
    
    return preview_file


def generate_content(config_name: str, output_dir: Path = None) -> Tuple[Dict[str, Any], str, Path, Path]:
    """
    生成WordPress内容和HTML文件
    
    Args:
        config_name: 配置文件名称（不带扩展名）
        output_dir: HTML输出目录，默认为项目根目录下的output文件夹
        
    Returns:
        (software_info, wordpress_content, html_file, preview_file) 元组
    """
    # 路径设置
    base_dir = Path(__file__).parent
    configs_dir = base_dir / "configs"
    
    # 默认输出目录
    if output_dir is None:
        output_dir = base_dir / "output"
    
    # 配置文件路径
    config_file = configs_dir / f"{config_name}.info"
    
    if not config_file.exists():
        print(f"错误: 配置文件 '{config_file}' 不存在！")
        return None, "", None, None
    
    try:
        # 解析配置
        print(f"正在解析配置文件: {config_file.name}")
        software_info = parse_config_file(config_file)
        
        # 获取软件标题
        software_title = software_info.get('标题', config_name)
        
        print(f"  ├─ 软件标题: {software_title}")
        print(f"  ├─ 软件名称: {software_info.get('名称', '未设置')}")
        print(f"  └─ 软件版本: {software_info.get('版本', '未设置')}")
        
        # 生成WordPress内容
        wordpress_content = generate_wordpress_content(software_info)
        
        # 保存WordPress内容文件
        content_dir = base_dir / "contents"
        content_dir.mkdir(exist_ok=True)
        content_filename = sanitize_filename(software_title) + "_wordpress.txt"
        content_file = content_dir / content_filename
        content_file.write_text(wordpress_content, encoding='utf-8')
        
        # 生成最终的HTML文件（纯内容，无包装div）
        html_file = generate_html_file(software_info, output_dir)
        
        # 生成预览文件
        preview_dir = base_dir / "previews"
        preview_file = generate_preview_file(software_info, preview_dir)
        
        print(f"  ✅ 生成文件:")
        print(f"     ├─ 内容HTML: {html_file.relative_to(base_dir)}")
        print(f"     ├─ 预览文件: {preview_file.relative_to(base_dir)}")
        print(f"     └─ WordPress内容: {content_file.relative_to(base_dir)}")
        
        # 显示生成的内容预览
        pure_content = generate_pure_content(software_info)
        print(f"\n  📋 生成内容预览（前300字符）:")
        print("  " + "-" * 56)
        preview_lines = pure_content[:300].split('\n')
        for line in preview_lines:
            if len(line) > 50:
                print(f"  {line[:50]}...")
            else:
                print(f"  {line}")
        print("  " + "-" * 56)
        
        return software_info, wordpress_content, html_file, preview_file
        
    except Exception as e:
        print(f"❌ 生成内容时出错: {e}")
        import traceback
        traceback.print_exc()
        return None, "", None, None


def generate_all_configs() -> List[Tuple[str, Path, Path]]:
    """
    生成所有配置文件的HTML
    
    Returns:
        生成的(配置名, HTML文件路径, 预览文件路径)列表
    """
    base_dir = Path(__file__).parent
    configs_dir = base_dir / "configs"
    output_dir = base_dir / "output"
    
    # 确保输出目录存在
    output_dir.mkdir(exist_ok=True)
    
    # 获取所有配置文件
    config_files = list(configs_dir.glob("*.info"))
    config_files = [f for f in config_files if f.name != "example.info"]
    
    if not config_files:
        print("⚠️  没有找到配置文件！")
        print(f"请在 {configs_dir} 目录下创建 .info 配置文件")
        return []
    
    print(f"📁 找到 {len(config_files)} 个配置文件，开始生成...")
    print("=" * 60)
    
    generated_files = []
    
    for config_file in config_files:
        config_name = config_file.stem
        print(f"\n📄 处理配置文件: {config_name}")
        print("-" * 40)
        
        software_info, _, html_file, preview_file = generate_content(config_name, output_dir)
        
        if software_info and html_file and preview_file:
            generated_files.append((config_name, html_file, preview_file))
            print(f"✅ {config_name} 生成完成")
        else:
            print(f"❌ {config_name} 生成失败")
        
        print("-" * 40)
    
    return generated_files


def list_configs() -> None:
    """列出所有可用的配置文件"""
    configs_dir = Path(__file__).parent / "configs"
    
    configs = list(configs_dir.glob("*.info"))
    configs = [f for f in configs if f.name != "example.info"]
    
    if not configs:
        print("📁 当前没有配置文件")
        print(f"请将配置文件放入: {configs_dir}")
        return
    
    print(f"📁 发现 {len(configs)} 个配置文件:")
    print("=" * 60)
    
    for i, config_file in enumerate(configs, 1):
        try:
            software_info = parse_config_file(config_file)
            title = software_info.get('标题', config_file.stem)
            name = software_info.get('名称', '未设置')
            version = software_info.get('版本', '未设置')
            
            # 检查是否已生成HTML
            output_dir = Path(__file__).parent / "output"
            safe_title = sanitize_filename(title)
            html_file = output_dir / f"{safe_title}.html"
            
            # 检查是否已生成预览
            preview_dir = Path(__file__).parent / "previews"
            preview_file = preview_dir / f"{safe_title}_preview.html"
            
            html_status = "✅ 已生成" if html_file.exists() else "⏳ 未生成"
            preview_status = "✅ 已生成" if preview_file.exists() else "⏳ 未生成"
            
            print(f"{i:2d}. {config_file.stem:20}")
            print(f"     标题: {title}")
            print(f"     名称: {name}")
            print(f"     版本: {version}")
            print(f"     内容文件: {html_status} {html_file.name if html_file.exists() else ''}")
            print(f"     预览文件: {preview_status} {preview_file.name if preview_file.exists() else ''}")
            print()
        except Exception as e:
            print(f"{i:2d}. {config_file.stem:20} ❌ 解析失败")
            print(f"     错误: {e}")
            print()


def main():
    """主函数 - 默认自动生成所有HTML文件"""
    print("🚀 软件页面生成器 - 生成纯HTML内容")
    print("=" * 60)
    print("说明：")
    print("  - 生成的HTML文件仅包含内容标签（h3, p, ol, li等）")
    print("  - 无包装div，无<head><body>等结构")
    print("  - 预览文件可在 previews/ 目录查看")
    print("=" * 60)
    
    # 自动生成所有配置文件
    generated_files = generate_all_configs()
    
    if generated_files:
        print("\n" + "=" * 60)
        print(f"🎉 批量生成完成！")
        print("=" * 60)
        
        # 显示生成的文件列表
        print("\n📋 生成的文件列表:")
        for i, (config_name, html_file, preview_file) in enumerate(generated_files, 1):
            # 读取文件内容显示基本信息
            content = html_file.read_text(encoding='utf-8')
            line_count = len(content.split('\n'))
            char_count = len(content)
            
            print(f"{i:2d}. {config_name}")
            print(f"     内容: {html_file.name} ({line_count}行, {char_count}字符)")
            print(f"     预览: {preview_file.name}")
            print(f"     路径: output/{html_file.name}")
            print()
        
        print(f"📁 文件位置:")
        print(f"  - 内容文件: output/ 目录")
        print(f"  - 预览文件: previews/ 目录 (可双击查看效果)")
        print(f"  - WordPress格式: contents/ 目录")
        
        print("\n🎯 后续操作:")
        print("  1. 查看配置文件: python build.py list")
        print("  2. 重新生成所有文件: 直接再次运行本程序")
        print("  3. 查看帮助信息: python build.py help")
        print("\n💡 提示: 如需查看预览效果，请到 previews/ 目录双击对应的 .html 文件")
    else:
        print("\n⚠️  未生成任何文件")
        print("请检查 configs/ 目录下是否有正确的配置文件")
        print("\n使用帮助:")
        print("  python build.py list   查看配置文件")
        print("  python build.py help   查看详细帮助")


def cli_main():
    """命令行接口主函数，支持参数"""
    if len(sys.argv) == 1:
        # 没有参数，运行主程序自动生成所有
        main()
    else:
        command = sys.argv[1].lower()
        
        if command == "list":
            list_configs()
        elif command == "gen" or command == "generate":
            # 生成特定配置文件
            if len(sys.argv) > 2:
                config_name = sys.argv[2]
                base_dir = Path(__file__).parent
                output_dir = base_dir / "output"
                software_info, _, html_file, preview_file = generate_content(config_name, output_dir)
                if html_file:
                    print(f"\n✅ 生成完成!")
                    print(f"   内容文件: {html_file}")
                    print(f"   预览文件: {preview_file}")
                    
                    # 显示文件内容
                    content = html_file.read_text(encoding='utf-8')
                    print(f"\n📄 生成内容预览:")
                    print("-" * 60)
                    print(content[:500] + ("..." if len(content) > 500 else ""))
                    print("-" * 60)
            else:
                print("❌ 请指定配置文件名")
                print("用法: python build.py gen <配置文件名>")
        elif command == "clean":
            # 清理生成的文件
            base_dir = Path(__file__).parent
            dirs_to_clean = ["output", "previews", "contents"]
            
            print("🧹 清理生成的文件...")
            for dir_name in dirs_to_clean:
                dir_path = base_dir / dir_name
                if dir_path.exists():
                    # 删除目录下的所有文件
                    for file in dir_path.glob("*"):
                        if file.is_file():
                            file.unlink()
                    print(f"  已清理: {dir_name}/")
                else:
                    print(f"  目录不存在: {dir_name}/")
            print("✅ 清理完成")
        elif command == "help" or command == "--help" or command == "-h":
            print("""
软件页面生成器 - 帮助
            
说明：
    本工具生成仅包含内容标签的纯HTML文件，无包装div。
    适合直接嵌入其他页面或CMS系统。
            
用法:
    直接运行程序             自动生成所有配置文件的纯HTML页面
    python build.py         自动生成所有配置文件的纯HTML页面
    python build.py list    列出所有配置文件及其状态
    python build.py gen <配置文件名>  生成特定配置文件的HTML
    python build.py clean   清理所有生成的文件
    python build.py help    显示此帮助信息
            
示例:
    python build.py                     # 生成所有页面
    python build.py list                # 查看配置文件
    python build.py gen pastebar        # 生成pastebar的页面
    python build.py clean               # 清理所有生成的文件
            
文件结构:
    configs/             配置文件目录 (*.info)
    output/              生成的纯HTML文件目录 (*.html) ← 仅内容标签
    previews/            预览文件目录 (*_preview.html) ← 完整HTML页面
    contents/   WordPress格式内容文件
    templates/           模板文件目录
            
配置文件格式:
    [软件信息]
    标题 = 软件标题           # 用于生成文件名
    名称 = 软件完整名称       # 用于页面显示
    版本 = 1.0.0             # 软件版本
    描述 = 软件描述文字       # 软件介绍
            
    [额外信息]                # 可选，如果为空则不生成任何内容
    内容 = 额外说明文字
            
输出文件示例 (output/目录):
    <h3>软件介绍</h3>
    <p>软件描述文字...</p>
    <h3>功能（使用）说明</h3>
    <ol>
     <li>功能1</li>
     <li>功能2</li>
    </ol>
    ... (仅内容标签，无包装div)
            """)
        else:
            print(f"❌ 未知命令: {command}")
            print("使用 'python build.py help' 查看帮助")


if __name__ == "__main__":
    # 默认运行CLI主函数
    cli_main()