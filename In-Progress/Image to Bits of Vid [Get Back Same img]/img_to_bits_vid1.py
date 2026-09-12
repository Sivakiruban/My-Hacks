import cv2
import numpy as np

# --- CONFIG ---
IMG_PATH = 'image1.jpg'  # Input .jpg image
OUT_PATH = 'output1.avi'  # Output .avi video
#FRAME_SIZE = (64, 64)    # You can change this as needed
FPS = 1                  # 1 frame per second

# --- STEP 1: Load image ---
image = cv2.imread(IMG_PATH)
if image is None:
    raise FileNotFoundError(f"Image not found: {IMG_PATH}")

# Resize to FRAME_SIZE for consistency
#image = cv2.resize(image, FRAME_SIZE)
# Automatically get frame size from image
FRAME_SIZE = (image.shape[1], image.shape[0])  # (width, height)

# --- STEP 2: Convert image to bits ---
img_bytes = image.flatten()
img_bits = np.unpackbits(img_bytes)

# --- STEP 3: Encode bits into video frames ---
# Each frame will store as much of the bitstream as possible
bits_per_frame = FRAME_SIZE[0] * FRAME_SIZE[1] * 3 * 8
num_frames = int(np.ceil(len(img_bits) / bits_per_frame))

# Pad bits to fill last frame
padded_bits = np.pad(img_bits, (0, num_frames * bits_per_frame - len(img_bits)), constant_values=0)

# Each frame is a byte array of shape (FRAME_SIZE[0], FRAME_SIZE[1], 3)
frames = padded_bits.reshape((num_frames, FRAME_SIZE[0], FRAME_SIZE[1], 3, 8))
frames = np.packbits(frames, axis=-1).squeeze(-1).astype(np.uint8)

# --- STEP 4: Write frames to video ---
# Use FFV1 for lossless, fallback to MJPG if not available
# error 1
"""
fourcc = cv2.VideoWriter_fourcc(*'FFV1')
out = cv2.VideoWriter(OUT_PATH, fourcc, FPS, FRAME_SIZE)

if not out.isOpened():
    # Fallback to MJPG
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out = cv2.VideoWriter(OUT_PATH, fourcc, FPS, FRAME_SIZE)
""" # error 1
fourcc = cv2.VideoWriter_fourcc(*'MJPG')
out = cv2.VideoWriter(OUT_PATH, fourcc, FPS, FRAME_SIZE)

for frame in frames:
    out.write(frame)
out.release()
print(f"✅ Video saved as {OUT_PATH}")