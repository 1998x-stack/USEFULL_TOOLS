#!/bin/bash

# Function to remove duplicate files based on name pattern
remove_duplicates() {
    local dir="$1"

    # Supported file extensions
    local extensions=("*.html" "*.pdf" "*.mp3" "*.mp4")

    # Iterate over each extension to find duplicates
    for ext in "${extensions[@]}"; do
        find "$dir" -type f -name "$ext" | while read -r file; do
            # Extract the base filename without the duplicate pattern (e.g., (1), (2))
            local base_file; base_file=$(echo "$file" | sed -E 's/\([0-9]+\)(\.[a-zA-Z0-9]+)$/\1/')

            # If a non-duplicate exists and matches the base, remove the duplicate
            if [[ "$file" != "$base_file" && -e "$base_file" ]]; then
                printf "Removing duplicate: %s\n" "$file"
                rm "$file"
            fi
        done
    done
}

main() {
    if [[ $# -ne 1 ]]; then
        printf "Usage: %s <target_directory>\n" "$0" >&2
        return 1
    fi

    local target_dir="$1"

    if [[ ! -d "$target_dir" ]]; then
        printf "Error: Directory %s does not exist.\n" "$target_dir" >&2
        return 1
    fi

    remove_duplicates "$target_dir"
}

main "$@"

