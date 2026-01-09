# templates/page_template.py
"""
WordPress友好的网页模板生成模块
支持WordPress短代码格式
"""

from typing import Dict, List, Any
import configparser
from pathlib import Path


def generate_wordpress_content(software_info: Dict[str, Any]) -> str:
    """
    生成适合WordPress编辑器直接粘贴的HTML内容
    支持WordPress短代码格式
    
    Args:
        software_info: 包含软件信息的字典
        
    Returns:
        WordPress内容字符串
    """
    html_parts = []
    
    # 1. 软件介绍部分
    html_parts.append("<h3>软件介绍</h3>\n")
    description = software_info.get('描述', '')
    if description:
        # 支持多段描述
        if isinstance(description, list):
            for para in description:
                html_parts.append(f"<p>{para}</p>\n")
        else:
            html_parts.append(f"<p>{description}</p>\n")
    
    # 空行分隔
    html_parts.append("\n")
    
    # 2. 功能说明部分
    features = software_info.get('功能', [])
    if features:
        html_parts.append("<h3>功能（使用）说明</h3>\n")
        html_parts.append("<ol>\n")
        for feature in features:
            html_parts.append(f" <li>{feature}</li>\n")
        html_parts.append("</ol>\n")
        html_parts.append("\n")
    
    # 3. 软件截图部分
    screenshots = software_info.get('截图', [])
    if screenshots:
        html_parts.append("<h3>软件截图</h3>\n")
        
        for i, screenshot in enumerate(screenshots):
            # 截图可以是字符串或字典
            if isinstance(screenshot, dict):
                caption = screenshot.get('caption', f'软件截图 {i+1}')
                attribution = screenshot.get('attribution', '')
                url = screenshot.get('url', '')
                
                if attribution:
                    html_parts.append(f"[insertimg caption='{caption}' attribution='{attribution}']")
                else:
                    html_parts.append(f"[insertimg caption='{caption}']")
                
                html_parts.append(f"<img src=\"{url}\" />")
                html_parts.append("[/insertimg]\n")
            else:
                # 简单的截图URL
                html_parts.append(f"[insertimg caption='软件截图 {i+1}']")
                html_parts.append(f"<img src=\"{screenshot}\" />")
                html_parts.append("[/insertimg]\n")
        
        html_parts.append("\n")
    
    # 4. 软件下载部分
    download_links = software_info.get('下载链接', [])
    if download_links:
        html_parts.append("<h3>软件下载</h3>\n")
        html_parts.append("[downloads]\n")
        
        for i, link_info in enumerate(download_links):
            if isinstance(link_info, dict):
                url = link_info.get('url', '')
                code = link_info.get('code', '')
            else:
                # 向后兼容
                url = link_info
                code = ''
            
            if code and code.strip():
                html_parts.append(f" [link url=\"{url}\" code=\"{code}\"][/link]")
            else:
                html_parts.append(f" [link url=\"{url}\"][/link]")
            
            # 每4个链接换一行，参考示例格式
            if (i + 1) % 4 == 0:
                html_parts.append("\n")
        
        # 确保以换行结束
        if len(download_links) % 4 != 0:
            html_parts.append("\n")
        
        html_parts.append("[/downloads]\n")
    
    # 5. 额外信息部分（可选）- 只有有内容时才添加
    extra_info = software_info.get('额外信息', '')
    if extra_info:
        # 检查是否为空内容
        if isinstance(extra_info, str) and extra_info.strip():
            html_parts.append("\n")
            html_parts.append("<h3>其他信息</h3>\n")
            html_parts.append(f"<p>{extra_info}</p>\n")
        elif isinstance(extra_info, list) and extra_info:
            html_parts.append("\n")
            html_parts.append("<h3>其他信息</h3>\n")
            for para in extra_info:
                if para and para.strip():
                    html_parts.append(f"<p>{para}</p>\n")
    
    return "".join(html_parts)


def parse_download_line(line: str) -> Dict[str, str]:
    """
    解析单行下载链接配置
    格式: URL [提取码]
    
    Args:
        line: 下载链接配置行
        
    Returns:
        包含url和code的字典
    """
    line = line.strip()
    if not line:
        return {}
    
    # 分割URL和提取码
    parts = line.split()
    if len(parts) == 1:
        # 只有URL，没有提取码
        return {'url': parts[0].strip(), 'code': ''}
    elif len(parts) >= 2:
        # 第一个是URL，第二个是提取码，后面的可能是注释
        url = parts[0].strip()
        code = parts[1].strip()
        return {'url': url, 'code': code}
    
    return {}


def parse_config_file(config_path: Path) -> Dict[str, Any]:
    """
    解析配置文件
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        包含软件信息的字典，包含标题字段
    """
    software_info = {}
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        current_section = None
        temp_downloads = []
        temp_features = []
        temp_screenshots = []
        
        for line in lines:
            line = line.strip()
            
            # 跳过空行和注释
            if not line or line.startswith('#'):
                continue
            
            # 检查是否是节标题
            if line.startswith('[') and line.endswith(']'):
                current_section = line[1:-1].strip()
                continue
            
            # 根据当前节处理内容
            if current_section == '软件信息':
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key == '标题':
                        software_info['标题'] = value
                    elif key == '名称':
                        software_info['名称'] = value
                    elif key == '版本':
                        software_info['版本'] = value
                    elif key == '描述':
                        # 描述可以是多段文本
                        if '||' in value:
                            software_info['描述'] = [para.strip() for para in value.split('||')]
                        else:
                            software_info['描述'] = value
            
            elif current_section == '功能介绍':
                if '=' in line:
                    # 格式: 编号 = 功能描述
                    _, feature = line.split('=', 1)
                    temp_features.append(feature.strip())
                else:
                    # 也支持直接每行一个功能描述
                    temp_features.append(line.strip())
            
            elif current_section == '软件截图':
                if '=' in line:
                    # 格式: 编号 = 标题|来源|URL 或 编号 = URL
                    _, value = line.split('=', 1)
                    value = value.strip()
                    
                    if '|' in value:
                        parts = value.split('|')
                        if len(parts) >= 3:
                            screenshot_info = {
                                'caption': parts[0].strip(),
                                'attribution': parts[1].strip(),
                                'url': parts[2].strip()
                            }
                        elif len(parts) == 2:
                            screenshot_info = {
                                'caption': parts[0].strip(),
                                'url': parts[1].strip()
                            }
                        else:
                            screenshot_info = {'url': value}
                    else:
                        screenshot_info = {'url': value}
                    temp_screenshots.append(screenshot_info)
            
            elif current_section == '下载链接':
                # 每行一个下载链接，格式: URL [提取码]
                if line and not line.startswith('#'):
                    link_info = parse_download_line(line)
                    if link_info:
                        temp_downloads.append(link_info)
            
            elif current_section == '额外信息':
                if not '额外信息' in software_info:
                    software_info['额外信息'] = []
                software_info['额外信息'].append(line)
        
        # 保存处理后的数据
        if temp_features:
            software_info['功能'] = temp_features
        
        if temp_screenshots:
            software_info['截图'] = temp_screenshots
        
        if temp_downloads:
            software_info['下载链接'] = temp_downloads
        
        # 如果没有标题，使用配置文件名或名称作为标题
        if '标题' not in software_info:
            if '名称' in software_info:
                software_info['标题'] = software_info['名称']
            else:
                software_info['标题'] = config_path.stem
        
        # 如果没有名称，使用标题作为名称
        if '名称' not in software_info:
            software_info['名称'] = software_info.get('标题', '未命名软件')
        
        # 如果没有版本，设置默认版本
        if '版本' not in software_info:
            software_info['版本'] = '1.0.0'
        
        # 如果没有描述，设置空描述
        if '描述' not in software_info:
            software_info['描述'] = ''
        
    except Exception as e:
        print(f"解析配置文件时出错: {e}")
        # 返回基本结构
        software_info = {
            '标题': config_path.stem,
            '名称': '未知软件', 
            '版本': '1.0.0', 
            '描述': '解析配置文件出错'
        }
    
    return software_info


def get_software_title(software_info: Dict[str, Any], config_path: Path = None) -> str:
    """
    获取软件标题，用于文件名
    
    Args:
        software_info: 软件信息字典
        config_path: 配置文件路径（可选）
        
    Returns:
        用于文件名的标题字符串
    """
    # 优先使用配置文件中的标题字段
    title = software_info.get('标题', '')
    
    if title:
        # 清理标题，移除不适用于文件名的字符
        import re
        # 移除Windows文件名不允许的字符: \ / : * ? " < > |
        title = re.sub(r'[\\/*?:"<>|]', '', title)
        # 替换空格为下划线
        title = title.replace(' ', '_')
        return title
    
    # 如果没有标题，使用名称
    if '名称' in software_info:
        name = software_info['名称']
        import re
        name = re.sub(r'[\\/*?:"<>|]', '', name)
        name = name.replace(' ', '_')
        return name
    
    # 最后使用配置文件名
    if config_path:
        return config_path.stem
    
    return 'software'


def generate_html_embed(software_info: Dict[str, Any]) -> str:
    """
    生成完整HTML预览页面
    
    Args:
        software_info: 包含软件信息的字典
        
    Returns:
        完整的HTML预览字符串
    """
    content = generate_wordpress_content(software_info)
    
    # 获取软件标题用于页面标题
    page_title = software_info.get('标题', software_info.get('名称', '软件页面'))
    
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_title} - WordPress预览</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Microsoft YaHei', sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f0f2f5;
        }}
        .preview-box {{
            background: white;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        }}
        h3 {{
            color: #1a1a1a;
            border-left: 4px solid #007cba;
            padding-left: 12px;
            margin: 25px 0 15px;
        }}
        h3 img {{
            width:95%;
            hight:auto;
            display: block;
            margin: 10px auto;
        }}
        .code-block {{
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            padding: 15px;
            border-radius: 6px;
            margin: 20px 0;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 14px;
            white-space: pre-wrap;
            word-wrap: break-word;
            line-height: 1.4;
        }}
        .instructions {{
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
            padding: 15px;
            margin: 20px 0;
            border-radius: 0 4px 4px 0;
        }}
        .file-info {{
            background: #f1f8e9;
            border-left: 4px solid #7cb342;
            padding: 10px 15px;
            margin: 15px 0;
            border-radius: 0 4px 4px 0;
        }}
    </style>
</head>
<body>
    <div class="preview-box">
        <h2 style="color: #0073aa; margin-top: 0; border-bottom: 2px solid #eee; padding-bottom: 10px;">
            WordPress内容生成器
        </h2>
        
        <div class="file-info">
            <strong>文件信息：</strong><br>
            软件标题: {software_info.get('标题', '未设置')}<br>
            软件名称: {software_info.get('名称', '未设置')}<br>
            软件版本: {software_info.get('版本', '1.0.0')}<br>
            生成文件: {software_info.get('标题', 'software').replace(' ', '_')}.html
        </div>
        
        <div class="instructions">
            <strong>使用说明：</strong>
            <ol style="margin: 10px 0 0 20px; padding: 0;">
                <li>复制下方代码框中的所有内容</li>
                <li>在WordPress编辑器中切换到<strong>文本模式</strong></li>
                <li>粘贴内容并发布</li>
                <li>确保您的WordPress主题支持 [insertimg] 和 [downloads] 短代码</li>
            </ol>
        </div>
        
        <h3>生成的内容：</h3>
        <div class="code-block" onclick="this.select()" style="cursor: pointer;">
{content}
        </div>
        
        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
            <small>
                <strong>提示：</strong> 点击上方代码框可全选内容，然后按 Ctrl+C 复制。
                如果您的主题不支持短代码，可能需要手动替换为相应的HTML代码。
            </small>
        </div>
    </div>
    
    <script>
        // 自动选择代码方便复制
        document.querySelectorAll('.code-block').forEach(block => {{
            block.addEventListener('click', function() {{
                const range = document.createRange();
                range.selectNodeContents(this);
                const selection = window.getSelection();
                selection.removeAllRanges();
                selection.addRange(range);
            }});
        }});
    </script>
</body>
</html>"""