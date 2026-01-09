#!/usr/bin/env python3
"""
图片自动上传工具
自动上传图片到图床并获取URL
"""

import subprocess
import sys
import time
import json
import pyperclip
from pathlib import Path
from typing import Optional
import os

class ImageUploader:
    """图片上传器"""
    
    def __init__(self):
        self.picgo_path = self.find_picgo()
        self.setup_directories()
        self.upload_history = {}
        
    def find_picgo(self) -> Optional[Path]:
        """查找PicGo安装路径"""
        possible_paths = [
            Path(os.getenv('LOCALAPPDATA', '')) / 'Programs' / 'PicGo' / 'PicGo.exe',
            Path.home() / 'AppData' / 'Local' / 'Programs' / 'PicGo' / 'PicGo.exe',
        ]
        
        for path in possible_paths:
            if path.exists():
                print(f"✅ 找到PicGo: {path}")
                return path
        
        print("❌ 未找到PicGo安装路径")
        return None
    
    def setup_directories(self):
        """设置目录"""
        self.base_dir = Path(__file__).parent
        self.resources_dir = self.base_dir / "resources"
        self.to_upload_dir = self.resources_dir / "to_upload"
        self.uploaded_dir = self.resources_dir / "uploaded"
        
        # 创建目录
        self.resources_dir.mkdir(exist_ok=True)
        self.to_upload_dir.mkdir(exist_ok=True)
        self.uploaded_dir.mkdir(exist_ok=True)
    
    def get_url_from_clipboard(self, timeout=5) -> Optional[str]:
        """从剪贴板获取URL"""
        try:
            import pyperclip
            
            # 等待PicGo复制URL到剪贴板
            start_time = time.time()
            last_content = ""
            
            while time.time() - start_time < timeout:
                try:
                    content = pyperclip.paste()
                    
                    # 检查是否有新的URL内容
                    if content and content != last_content:
                        # 查找URL
                        if 'http://' in content or 'https://' in content:
                            # 提取第一个URL
                            import re
                            urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', content)
                            if urls:
                                url = urls[0]
                                # 确保是完整的URL
                                if not url.startswith('http'):
                                    url = 'https://' + url
                                print(f"📋 从剪贴板获取URL: {url}")
                                return url
                        last_content = content
                    
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"⚠️  读取剪贴板失败: {e}")
                    break
            
        except ImportError:
            print("⚠️  未安装pyperclip")
        
        return None
    
    def upload_and_get_url(self, image_path: Path) -> Optional[str]:
        """
        上传图片并获取URL
        """
        if not self.picgo_path:
            return None
        
        print(f"📤 上传: {image_path.name}")
        
        try:
            # 先清空剪贴板
            try:
                import pyperclip
                pyperclip.copy("")
            except:
                pass
            
            # 执行上传命令
            cmd = [str(self.picgo_path), 'upload', str(image_path.absolute())]
            
            print(f"执行命令...")
            
            # 执行命令
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            
            # 检查输出中是否有URL
            output = result.stdout + result.stderr
            if output:
                print(f"命令输出: {output[:200]}")
                
                # 尝试从输出中提取URL
                import re
                urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', output)
                if urls:
                    url = urls[0]
                    if not url.startswith('http'):
                        url = 'https://' + url
                    print(f"✅ 从输出获取URL: {url}")
                    self.upload_history[str(image_path)] = url
                    return url
            
            # 尝试从剪贴板获取URL
            url = self.get_url_from_clipboard(timeout=10)
            
            if url:
                self.upload_history[str(image_path)] = url
                return url
            
            # 检查历史记录
            if str(image_path) in self.upload_history:
                return self.upload_history[str(image_path)]
            
            return None
            
        except Exception as e:
            print(f"❌ 上传失败: {e}")
            return None
    
    def process_image(self, image_path: Path) -> bool:
        """处理单张图片"""
        print(f"\n🔄 处理: {image_path.name}")
        print("-" * 40)
        
        # 获取URL
        url = self.upload_and_get_url(image_path)
        
        if url:
            print(f"✅ 上传成功!")
            print(f"🔗 URL: {url}")
            
            # 复制URL到剪贴板
            try:
                import pyperclip
                pyperclip.copy(url)
                print("📋 URL已复制到剪贴板")
            except:
                print("⚠️  无法复制到剪贴板")
            
            # 移动文件到已上传目录
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            target_name = f"{timestamp}_{image_path.name}"
            target_path = self.uploaded_dir / target_name
            
            try:
                # 移动文件
                image_path.rename(target_path)
                print(f"📦 已移动: {target_path.name}")
                
                # 保存URL到文本文件
                url_file = self.uploaded_dir / f"{timestamp}_{image_path.stem}.txt"
                with open(url_file, 'w', encoding='utf-8') as f:
                    f.write(url)
                print(f"💾 URL已保存: {url_file.name}")
                
                # 保存到历史记录文件
                self.save_upload_record(image_path.name, url, target_name)
                
                return True
                
            except Exception as e:
                print(f"❌ 移动文件失败: {e}")
                return True
        
        else:
            print("❌ 上传失败，无法获取URL")
            print("💡 建议手动操作:")
            print("1. 打开PicGo应用")
            print("2. 将图片拖入PicGo窗口")
            print("3. PicGo会自动复制URL到剪贴板")
            return False
    
    def save_upload_record(self, filename: str, url: str, saved_name: str):
        """保存上传记录"""
        record_file = self.resources_dir / "upload_records.json"
        
        records = {}
        if record_file.exists():
            try:
                with open(record_file, 'r', encoding='utf-8') as f:
                    records = json.load(f)
            except:
                pass
        
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        records[filename] = {
            "url": url,
            "saved_as": saved_name,
            "timestamp": timestamp,
            "time": int(time.time())
        }
        
        try:
            with open(record_file, 'w', encoding='utf-8') as f:
                json.dump(records, f, indent=2, ensure_ascii=False)
            print("📝 记录已保存")
        except Exception as e:
            print(f"⚠️  保存记录失败: {e}")
    
    def monitor_directory(self):
        """监控目录"""
        print("👀 监控模式已启动")
        print(f"监控目录: {self.to_upload_dir}")
        print("将图片拖放到此目录即可自动上传")
        print("按 Ctrl+C 停止")
        print("-" * 50)
        
        processed_files = set()
        
        try:
            while True:
                # 检查新文件
                current_files = set()
                for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']:
                    for f in self.to_upload_dir.glob(f"*{ext}"):
                        if f.is_file():
                            current_files.add(f)
                    for f in self.to_upload_dir.glob(f"*{ext.upper()}"):
                        if f.is_file():
                            current_files.add(f)
                
                # 找出新文件
                new_files = current_files - processed_files
                
                for image_path in new_files:
                    print(f"\n📥 发现新图片: {image_path.name}")
                    
                    # 处理图片
                    success = self.process_image(image_path)
                    
                    if success:
                        processed_files.add(image_path)
                    else:
                        processed_files.add(image_path)
                        print("⚠️  处理失败，已跳过")
                
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\n🛑 停止监控")
        except Exception as e:
            print(f"❌ 监控出错: {e}")
    
    def process_existing_images(self):
        """处理现有图片"""
        print(f"📁 扫描目录: {self.to_upload_dir}")
        
        # 收集所有图片文件
        image_files = []
        for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']:
            image_files.extend(self.to_upload_dir.glob(f"*{ext}"))
            image_files.extend(self.to_upload_dir.glob(f"*{ext.upper()}"))
        
        if not image_files:
            print("📭 没有找到图片")
            return
        
        print(f"📷 找到 {len(image_files)} 张图片")
        
        success_count = 0
        
        for i, image_path in enumerate(image_files, 1):
            print(f"\n[{i}/{len(image_files)}] {'='*40}")
            
            success = self.process_image(image_path)
            
            if success:
                success_count += 1
            
            print("=" * 40)
        
        print(f"\n🎉 处理完成! 成功: {success_count}/{len(image_files)}")
    
    def show_help(self):
        """显示帮助信息"""
        print("\n💡 使用帮助:")
        print("1. 确保PicGo已安装并配置了图床")
        print("2. 将图片拖放到 resources/to_upload/ 目录")
        print("3. 程序会自动上传并复制URL到剪贴板")
        print("4. 上传的图片会移动到 resources/uploaded/ 目录")
        print("5. URL也会保存到同名的.txt文件中")
        print("\n📁 目录结构:")
        print(f"   {self.to_upload_dir}  - 拖放图片到这里")
        print(f"   {self.uploaded_dir}  - 已上传的图片")
        print(f"   {self.resources_dir}/upload_records.json - 上传记录")

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 图片自动上传工具")
    print("=" * 60)
    
    uploader = ImageUploader()
    
    if not uploader.picgo_path:
        print("❌ 请先安装PicGo")
        print("下载地址: https://github.com/Molunerfinn/PicGo/releases")
        return
    
    print(f"📁 资源目录: {uploader.resources_dir}")
    print(f"📤 待上传目录: {uploader.to_upload_dir}")
    print(f"📦 已上传目录: {uploader.uploaded_dir}")
    
    print("\n📋 请选择模式:")
    print("1. 处理现有图片")
    print("2. 启动监控模式（拖放自动上传）")
    print("3. 显示帮助信息")
    
    try:
        choice = input("\n请选择 (1-3): ").strip()
        
        if choice == "1":
            uploader.process_existing_images()
        elif choice == "2":
            uploader.monitor_directory()
        elif choice == "3":
            uploader.show_help()
        else:
            print("❌ 无效选择")
    
    except KeyboardInterrupt:
        print("\n👋 用户取消")

if __name__ == "__main__":
    # 检查依赖
    try:
        import pyperclip
    except ImportError:
        print("⚠️  未安装pyperclip，安装命令: pip install pyperclip")
        print("这将影响URL自动复制功能")
    
    main()