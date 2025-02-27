import os

UPLOAD_FOLDER = "C:/Users/DELL/Documents/kars/static/uploads"

# Ensure the directory exists before saving the file
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Now construct the full file path
photo=logo.jpg
filename = "example.jpg"  # Replace with your dynamic filename
file_path = os.path.join(UPLOAD_FOLDER, filename)

# Save the uploaded file
photo.save(file_path)