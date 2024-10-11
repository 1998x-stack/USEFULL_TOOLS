#!/bin/bash

# PDFCompressor-like 脚本，查找并压缩指定目录中超过 100MB 的 PDF 文件，使用 Ghostscript 进行压缩

# 定义全局变量，大小限制为 100MB（单位：字节）
SIZE_LIMIT=$((60 * 1024 * 1024))  # 100MB 转换为字节

# 检查操作系统类型，判断是 macOS 还是 Linux
OS_TYPE=$(uname)

# 获取文件大小的函数，兼容 macOS 和 Linux
get_file_size() {
    local file_path="$1"  # 接受文件路径作为参数
    if [[ -f "$file_path" ]]; then  # 检查文件是否存在
        if [[ "$OS_TYPE" == "Darwin" ]]; then  # macOS 使用 -f "%z"
            stat -f "%z" "$file_path"  # 返回文件大小（字节）
        else  # Linux 使用 --format="%s"
            stat --format="%s" "$file_path"  # 返回文件大小（字节）
        fi
    else
        echo 0  # 如果文件不存在或无效，返回 0
    fi
}

# 使用 Ghostscript 压缩 PDF 的函数
compress_pdf() {
    local input_pdf="$1"  # 输入 PDF 文件路径
    local output_pdf="$2"  # 输出压缩后的 PDF 文件路径

    echo "正在压缩 $input_pdf -> $output_pdf"  # 显示正在进行的压缩操作

    # 使用 Ghostscript 命令压缩 PDF 文件
    gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 \
       -dPDFSETTINGS=/ebook -dNOPAUSE -dQUIET -dBATCH \
       -sOutputFile="$output_pdf" "$input_pdf"

    # 判断压缩是否成功
    if [[ $? -eq 0 ]]; then
        echo "压缩成功: $input_pdf -> $output_pdf"  # 压缩成功时输出
        return 0  # 返回成功状态码
    else
        echo "压缩过程中出错: $input_pdf" >&2  # 压缩失败时输出错误信息到标准错误
        return 1  # 返回错误状态码
    fi
}

# 删除原始 PDF 文件并重命名压缩文件的函数
finalize_compression() {
    local input_pdf="$1"  # 原始 PDF 文件路径
    local output_pdf="$2"  # 压缩后的 PDF 文件路径

    # 删除原始 PDF
    rm "$input_pdf"
    echo "已删除原始文件: $input_pdf"

    # 将压缩后的文件重命名为原始文件名
    mv "$output_pdf" "$input_pdf"
    echo "压缩文件已重命名为原始文件名: $input_pdf"
}

# 处理目标目录中的所有 PDF 文件的函数
process_pdfs_in_dir() {
    local target_dir="$1"  # 接受目标目录作为参数

    # 使用 find 命令查找目录中的所有 .pdf 文件，并对每个文件进行处理
    find "$target_dir" -type f -name "*.pdf" | while read -r pdf_file; do
        echo "正在处理文件: $pdf_file"  # 显示正在处理的 PDF 文件

        file_size=$(get_file_size "$pdf_file")  # 获取文件大小

        # 如果文件大小为 0，跳过处理
        if [[ "$file_size" -eq 0 ]]; then
            echo "文件未找到或大小为 0，跳过: $pdf_file"
            continue
        fi

        # 输出文件大小（单位为 MB）
        echo "文件大小: $((file_size / (1024 * 1024))) MB"

        # 如果文件大小超过 100MB，则进行压缩
        if [[ "$file_size" -gt "$SIZE_LIMIT" ]]; then
            echo "文件超过 100MB，正在压缩..."
            output_pdf="${pdf_file%.pdf}_compressed.pdf"  # 为压缩后的文件命名，添加后缀 "_compressed"
            if compress_pdf "$pdf_file" "$output_pdf"; then  # 调用压缩函数进行压缩
                finalize_compression "$pdf_file" "$output_pdf"  # 删除原文件并重命名压缩文件
            else
                echo "压缩失败，保留原文件: $pdf_file"  # 如果压缩失败，保留原文件
            fi
        else
            echo "文件未超过 100MB，无需压缩。"  # 文件未超过限制时无需压缩
        fi
    done
}

# 主函数
main() {
    local target_dir="$1"  # 从命令行参数获取目标目录路径

    # 检查是否提供了有效的目录路径
    if [[ -z "$target_dir" || ! -d "$target_dir" ]]; then
        echo "用法: $0 <目标目录>"
        exit 1  # 如果目录无效，退出并返回错误码
    fi

    # 调用处理函数，处理指定目录中的 PDF 文件
    process_pdfs_in_dir "$target_dir"
}

# 调用主函数，传递命令行中的第一个参数（目标目录）
main "$1"
