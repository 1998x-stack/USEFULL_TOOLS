#!/bin/bash

# Function to convert a single webp file to png
convert_webp_to_png() {
    local input_file="$1"
    local output_dir
    local base_name

    # Get the directory of the input file
    output_dir=$(dirname "$input_file")
    # Get the base name without extension
    base_name=$(basename "$input_file" .webp)

    # Validate if input file exists and is readable
    if [[ ! -r "$input_file" ]]; then
        printf "Error: Cannot read '%s'\n" "$input_file" >&2
        return 1
    fi

    # Perform the conversion, saving in the same directory as the original .webp
    if ! convert "$input_file" "$output_dir/$base_name.png"; then
        printf "Error: Failed to convert '%s' to PNG\n" "$input_file" >&2
        return 1
    fi

    printf "Successfully converted: %s to %s\n" "$input_file" "$output_dir/$base_name.png"
    return 0
}

# Function to process a directory containing webp files
process_directory() {
    local dir="$1"
    local webp_files

    # Find .webp files in the directory
    webp_files=$(find "$dir" -type f -name "*.webp")

    # Check if no .webp files found
    if [[ -z "$webp_files" ]]; then
        printf "No .webp files found in directory: %s\n" "$dir" >&2
        return 1
    fi

    # Process each found .webp file
    while IFS= read -r file; do
        convert_webp_to_png "$file"
    done <<< "$webp_files"
}

# Main function
main() {
    if [[ $# -lt 1 ]]; then
        printf "Usage: %s <webp_file_or_directory>\n" "$0" >&2
        return 1
    fi

    local target="$1"

    # Check if the target is a file or a directory
    if [[ -f "$target" ]]; then
        convert_webp_to_png "$target"
    elif [[ -d "$target" ]]; then
        process_directory "$target"
    else
        printf "Error: '%s' is not a valid file or directory\n" "$target" >&2
        return 1
    fi
}

# Execute main function
main "$@"