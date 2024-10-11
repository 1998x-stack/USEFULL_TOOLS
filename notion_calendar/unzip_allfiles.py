import os
import zipfile
import rarfile

def extract_files(directory: str) -> None:
    """
    遍历目录并解压缩所有的ZIP文件和RAR文件，确保文件名使用UTF-8编码。
    
    Args:
        directory (str): 要遍历的目录路径。
        
    Example:
        extract_files('/path/to/directory')
    """
    # 设置RAR文件强制使用UTF-8编码
    rarfile.UNRAR_TOOL = "unrar"  # 确保安装了unrar工具

    # 遍历目录中的所有文件
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            # 如果文件是ZIP文件
            if file.endswith('.zip'):
                try:
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        # 强制使用UTF-8编码解压缩
                        for info in zip_ref.infolist():
                            info.filename = info.filename.encode('cp437').decode('utf-8')
                        extract_dir = os.path.join(root, os.path.splitext(file)[0])
                        zip_ref.extractall(extract_dir)
                        print(f"解压缩ZIP文件: {file_path} 到 {extract_dir}")
                except zipfile.BadZipFile:
                    print(f"无法解压缩ZIP文件: {file_path}，文件可能已损坏。")
            # 如果文件是RAR文件
            elif file.endswith('.rar'):
                try:
                    with rarfile.RarFile(file_path, 'r') as rar_ref:
                        extract_dir = os.path.join(root, os.path.splitext(file)[0])
                        # 设定rarfile使用UTF-8编码
                        for info in rar_ref.infolist():
                            info.filename = info.filename.encode('cp437').decode('utf-8')
                        rar_ref.extractall(extract_dir)
                        print(f"解压缩RAR文件: {file_path} 到 {extract_dir}")
                except rarfile.BadRarFile:
                    print(f"无法解压缩RAR文件: {file_path}，文件可能已损坏。")

if __name__ == "__main__":
    directory_to_extract = '/path/to/directory'  # 修改为你要解压的目录路径
    extract_files(directory_to_extract)
