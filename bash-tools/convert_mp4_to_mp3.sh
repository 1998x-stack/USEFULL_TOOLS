#!/bin/bash

# Global variable to store the target directory
TARGET_DIR="$1"

# Function to convert MP4 to MP3 and delete MP4 regardless of success
convert_and_remove_mp4() {
    local mp4_file mp3_file
    mp4_file="$1"

    # Derive the MP3 file name from the MP4 file name, ensuring safe output
    mp3_file="${mp4_file%.mp4}.mp3"

    # Perform the conversion using ffmpeg with better error handling
    if ffmpeg -i "$mp4_file" -vn -acodec libmp3lame -q:a 2 "$mp3_file" >/dev/null 2>&1; then
        printf "Successfully converted: %s -> %s\n" "$mp4_file" "$mp3_file"
    else
        printf "Error converting: %s, removing MP4 anyway\n" "$mp4_file" >&2
    fi

    # Remove the original MP4 file regardless of conversion success
    if rm -f "$mp4_file"; then
        printf "Removed: %s\n" "$mp4_file"
    else
        printf "Failed to remove: %s\n" "$mp4_file" >&2
    fi
}

# Main function to find and process all .mp4 files in the target directory
main() {
    # Ensure the target directory is provided and valid
    if [[ -z "$TARGET_DIR" || ! -d "$TARGET_DIR" ]]; then
        printf "Usage: %s <directory>\n" "$0" >&2
        return 1
    fi

    # Find all MP4 files and process each
    find "$TARGET_DIR" -type f -name "*.mp4" -print0 | while IFS= read -r -d '' mp4_file; do
        convert_and_remove_mp4 "$mp4_file"
    done
}

# Run the main function
main