#!/bin/bash

#### EXAMPLE USAGE ####
# bash search_logs.sh logs/resource_recommend/2024-08-23.log 胶囊咖啡机 0


# Global variables for input arguments
FILENAME="$1"
SEARCH_STRING="$2"
MODE="$3"

# Function to check if file exists and is readable
validate_file() {
    if [[ ! -r "$FILENAME" ]]; then
        printf "Error: File '%s' does not exist or is not readable.\n" "$FILENAME" >&2
        return 1
    fi
}

# Function to search for the string and retrieve line and character positions
search_string() {
    local search_result; search_result=$(grep -n -o -m 1 "$SEARCH_STRING" "$FILENAME")
    if [[ -z "$search_result" ]]; then
        printf "Error: String '%s' not found in file '%s'.\n" "$SEARCH_STRING" "$FILENAME" >&2
        return 1
    fi

    local line_number; line_number=$(printf "%s" "$search_result" | cut -d: -f1)
    local char_position; char_position=$(printf "%s" "$search_result" | grep -b -o "$SEARCH_STRING" "$FILENAME" | head -n 1 | cut -d: -f1)

    printf "%s\n%s\n" "$line_number" "$char_position"
}

# Function to handle mode 0: output lines around the found line
output_mode_0() {
    local line_number="$1"
    local start_line=$((line_number > 20 ? line_number - 20 : 1))
    local end_line=$((line_number + 10))

    sed -n "${start_line},${end_line}p" "$FILENAME"
}

# Function to handle mode 1: output characters around the found character position
output_mode_1() {
    local char_position="$1"
    local file_size; file_size=$(stat -c %s "$FILENAME")
    local start_char=$((char_position > 3000 ? char_position - 3000 : 0))
    local end_char=$((char_position + 1000))

    if ((end_char > file_size)); then
        end_char=$file_size
    fi

    dd if="$FILENAME" bs=1 skip="$start_char" count=$((end_char - start_char)) 2>/dev/null
}

# Main function
main() {
    validate_file || return 1

    local search_result; search_result=$(search_string) || return 1
    local line_number; line_number=$(printf "%s" "$search_result" | head -n 1)
    local char_position; char_position=$(printf "%s" "$search_result" | tail -n 1)

    case "$MODE" in
        0) output_mode_0 "$line_number" ;;
        1) output_mode_1 "$char_position" ;;
        *)
            printf "Error: Invalid mode '%s'. Choose 0 or 1.\n" "$MODE" >&2
            return 1
            ;;
    esac
}

# Execute main function
main