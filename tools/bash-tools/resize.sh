#!/bin/bash
# 图片动态缩放脚本 - 支持正方形/矩形尺寸
# 用法: ./resize.sh <输入文件> <尺寸模式> [输出文件]
# 尺寸模式: 
#   - 正方形: 输入单个数字 (e.g., 300)
#   - 矩形: 输入"宽x高" (e.g., 800x600)

# 检查参数数量
if [ $# -lt 2 ]; then
  echo "错误：参数不足！"
  echo "用法: $0 <输入文件> <尺寸> [输出文件]"
  echo "示例:"
  echo "  $0 image.jpg 300          # 生成300x300的正方形"
  echo "  $0 image.jpg 800x600      # 生成800x600的矩形"
  exit 1
fi

input_file="$1"
size="$2"
output_file="${3:-${input_file%.*}_resized.${input_file##*.}}"  # 默认输出文件名

# 验证输入文件是否存在
if [ ! -f "$input_file" ]; then
  echo "错误：文件 '$input_file' 不存在！"
  exit 1
fi

# 解析尺寸参数
if [[ "$size" == *"x"* ]]; then
  # 矩形模式 (宽x高)
  width=$(echo "$size" | cut -d'x' -f1)
  height=$(echo "$size" | cut -d'x' -f2)
else
  # 正方形模式 (单数字)
  width="$size"
  height="$size"
fi

# 使用ImageMagick进行缩放
if command -v convert &> /dev/null; then
  convert "$input_file" -resize "${width}x${height}!" "$output_file"
  echo "缩放完成: $input_file → ${width}x${height} → $output_file"
else
  echo "错误：请先安装ImageMagick！"
  echo "安装命令: sudo apt install imagemagick  # Debian/Ubuntu"
  echo "          brew install imagemagick    # macOS"
  exit 1
fi