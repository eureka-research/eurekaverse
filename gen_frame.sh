input_folder=videos/comparisons
output_folder=videos/comparisons
# Iterate over each MP4 file in the input folder
for file in "$input_folder"/*.mp4; do
    # Extract the filename without extension
    filename=$(basename "$file")
    filename="${filename%.*}"

    # Use ffmpeg to extract the last frame and save it as PNG
    # ffmpeg -i "$file" -vf "select=gte(n\, $(ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_frames -of csv=p=0 "$file"))" -vframes 1 "$output_folder/$filename.png"
    # ffmpeg -sseof -3 -i "$file" -update 1 -q:v 1 "$output_folder/$filename.png"
    ffmpeg -i "$file" -vframes 1 "$output_folder/$filename.png"


    echo "Extracted the first frame of $file"
done
