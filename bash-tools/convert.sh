#!/bin/bash

# Global Variables
WORD2PDF_OUTPUT_DIR="./output/pdf"
WORD2JPG_OUTPUT_DIR="./output/jpg"
WORD2MD_OUTPUT_DIR="./output/markdown"
MD2WORD_OUTPUT_DIR="./output/word"

# Ensure required dependencies
check_dependencies() {
    local dependencies=("libreoffice" "pandoc" "convert")
    for dep in "${dependencies[@]}"; do
        if ! command -v "$dep" &>/dev/null; then
            printf "Error: Required dependency '%s' is not installed.\n" "$dep" >&2
            return 1
        fi
    done
}

# Convert Word to PDF
convert_word_to_pdf() {
    local input_file="$1"
    if [[ ! -f "$input_file" ]]; then
        printf "Error: Input file '%s' does not exist.\n" "$input_file" >&2
        return 1
    fi

    mkdir -p "$WORD2PDF_OUTPUT_DIR"
    local output_file="$WORD2PDF_OUTPUT_DIR/$(basename "${input_file%.*}.pdf")"

    libreoffice --headless --convert-to pdf "$input_file" --outdir "$WORD2PDF_OUTPUT_DIR" &>/dev/null
    if [[ -f "$output_file" ]]; then
        printf "Success: PDF created at '%s'.\n" "$output_file"
    else
        printf "Error: PDF conversion failed for '%s'.\n" "$input_file" >&2
        return 1
    fi
}

# Convert Word to JPG
convert_word_to_jpg() {
    local input_file="$1"
    if [[ ! -f "$input_file" ]]; then
        printf "Error: Input file '%s' does not exist.\n" "$input_file" >&2
        return 1
    fi

    mkdir -p "$WORD2JPG_OUTPUT_DIR"
    local pdf_file
    pdf_file=$(mktemp --suffix=.pdf)

    libreoffice --headless --convert-to pdf "$input_file" --outdir "$(dirname "$pdf_file")" &>/dev/null
    if [[ ! -f "$pdf_file" ]]; then
        printf "Error: Intermediate PDF creation failed for '%s'.\n" "$input_file" >&2
        return 1
    fi

    convert -density 300 "$pdf_file" "$WORD2JPG_OUTPUT_DIR/$(basename "${input_file%.*}")-%03d.jpg"
    if [[ $? -eq 0 ]]; then
        printf "Success: JPGs created in directory '%s'.\n" "$WORD2JPG_OUTPUT_DIR"
    else
        printf "Error: JPG conversion failed for '%s'.\n" "$input_file" >&2
        return 1
    fi
    rm -f "$pdf_file"
}

# Convert Word to Markdown
convert_word_to_markdown() {
    local input_file="$1"
    if [[ ! -f "$input_file" ]]; then
        printf "Error: Input file '%s' does not exist.\n" "$input_file" >&2
        return 1
    fi

    mkdir -p "$WORD2MD_OUTPUT_DIR"
    local output_file="$WORD2MD_OUTPUT_DIR/$(basename "${input_file%.*}.md")"

    pandoc "$input_file" -o "$output_file" &>/dev/null
    if [[ -f "$output_file" ]]; then
        printf "Success: Markdown file created at '%s'.\n" "$output_file"
    else
        printf "Error: Markdown conversion failed for '%s'.\n" "$input_file" >&2
        return 1
    fi
}

# Convert Markdown to Word
convert_markdown_to_word() {
    local input_file="$1"
    if [[ ! -f "$input_file" ]]; then
        printf "Error: Input file '%s' does not exist.\n" "$input_file" >&2
        return 1
    fi

    mkdir -p "$MD2WORD_OUTPUT_DIR"
    local output_file="$MD2WORD_OUTPUT_DIR/$(basename "${input_file%.*}.docx")"

    pandoc "$input_file" -o "$output_file" &>/dev/null
    if [[ -f "$output_file" ]]; then
        printf "Success: Word file created at '%s'.\n" "$output_file"
    else
        printf "Error: Word conversion failed for '%s'.\n" "$input_file" >&2
        return 1
    fi
}

# Main Execution
main() {
    check_dependencies || exit 1

    case "$1" in
    word2pdf)
        shift
        convert_word_to_pdf "$@"
        ;;
    word2jpg)
        shift
        convert_word_to_jpg "$@"
        ;;
    word2markdown)
        shift
        convert_word_to_markdown "$@"
        ;;
    markdown2word)
        shift
        convert_markdown_to_word "$@"
        ;;
    *)
        printf "Usage: %s {word2pdf|word2jpg|word2markdown|markdown2word} <file>\n" "$0" >&2
        exit 1
        ;;
    esac
}

main "$@"