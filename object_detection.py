from google import genai
from google.genai import types
from PIL import Image, ImageDraw, ImageFont
import json
import os

# It's highly recommended to use environment variables for your API key
# instead of hardcoding it in the script.
client = genai.Client(api_key="Your API Key") # ⚠️ Replace with your API key

# --- Load Image ---
try:
    image = Image.open("/content/objects.jpg") # 👈 Replace with your image file path
except FileNotFoundError:
    print("Error: Image file not found. Please check the path.")
    exit()

# --- Create directory for detected objects ---
output_dir = "detected_objects"
os.makedirs(output_dir, exist_ok=True)

# --- Prepare Prompt and API Configuration ---
prompt = "Detect all prominent items in the image. For each item, provide a 'label' and its 'box_2d' coordinates. The box_2d should be [ymin, xmin, ymax, xmax] normalized from 0 to 1000."

config = types.GenerateContentConfig(
    response_mime_type="application/json"
)

# --- Call the Gemini API ---
print("🔍 Calling the Gemini API to detect objects...")
response = client.models.generate_content(
    model="gemini-2.5-flash", # Using gemini-1.5-flash
    contents=[image, prompt],
    config=config
)

# --- Process the Response and Draw on the Image ---
# Convert image to RGB to ensure it can be drawn on
drawable_image = image.convert("RGB")
draw = ImageDraw.Draw(drawable_image)
width, height = drawable_image.size

# Load the JSON response
bounding_boxes = json.loads(response.text)
print(f"✅ Found {len(bounding_boxes)} objects.")

# Loop through each detected object
for i, box_data in enumerate(bounding_boxes):
    # Get the label and normalized coordinates
    label = box_data["label"]
    ymin, xmin, ymax, xmax = box_data["box_2d"]

    # Convert normalized 0-1000 coordinates to absolute pixel coordinates
    abs_y1 = int(ymin / 1000 * height)
    abs_x1 = int(xmin / 1000 * width)
    abs_y2 = int(ymax / 1000 * height)
    abs_x2 = int(xmax / 1000 * width)

    # Ensure coordinates are within image bounds
    abs_x1 = max(0, abs_x1)
    abs_y1 = max(0, abs_y1)
    abs_x2 = min(width, abs_x2)
    abs_y2 = min(height, abs_y2)

    # Define the rectangle coordinates for drawing
    draw_box = [(abs_x1, abs_y1), (abs_x2, abs_y2)]

    # Draw the bounding box on the image
    draw.rectangle(draw_box, outline="cyan", width=3)

    # Draw the label text just above the box
    text_position = (abs_x1 + 5, abs_y1 - 15) # Adjust position as needed
    draw.text(text_position, label, fill="cyan", font_size=15)

    # --- Crop and save individual object ---
    # Crop the detected object from the original image
    cropped_object = image.crop((abs_x1, abs_y1, abs_x2, abs_y2))
    
    # Create a safe filename (remove special characters)
    safe_label = "".join(c for c in label if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_label = safe_label.replace(' ', '_')
    
    # Save the cropped object with a unique filename
    object_filename = f"{i+1:02d}_{safe_label}.jpg"
    object_path = os.path.join(output_dir, object_filename)
    
    # Save the cropped image
    cropped_object.save(object_path)
    print(f"💾 Saved object '{label}' to {object_path}")

# --- Display the Final Image ---
print("🖼️ Displaying the image with detected objects.")
drawable_image.show()

# You can also save the result to a file
output_path = "detected_objects_annotated.jpg"
drawable_image.save(output_path)
print(f"Annotated image saved to {output_path}")

print(f"\n📁 All detected objects saved in the '{output_dir}' directory")
