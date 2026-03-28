#!/bin/bash

# 目标输出文件
output_file="all.txt"

# 清空或创建输出文件
> "$output_file"

# 查找所有代码文件并处理
find . -type f \( -name "*.py" -o -name "*.html" -o -name "*.js" -o -name "*.css" \) | while read -r file; do
    # 获取相对路径
    relative_path="${file#./}"
    
    # 获取文件扩展名并转换为语言标识
    extension="${file##*.}"
    case "$extension" in
        py) lang="python" ;;
        html) lang="html" ;;
        js) lang="javascript" ;;
        css) lang="css" ;;
        *) lang="" ;;
    esac
    
    # 写入文件路径和分隔符
    echo "$relative_path" >> "$output_file"
    echo "\`\`\`$lang" >> "$output_file"
    
    # 写入文件内容（保留原始格式）
    cat "$file" >> "$output_file"
    
    # 添加代码块结束标记和空行
    echo -e "\n\`\`\`\n" >> "$output_file"
done

echo "All code files have been merged into $output_file"