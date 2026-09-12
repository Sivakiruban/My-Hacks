import cv2
import numpy as np

# --- CONFIG ---
VIDEO_PATH = 'output1.avi'
IMG_SHAPE = (64, 64, 3)  # Must match original
BITS_PER_FRAME = IMG_SHAPE[0] * IMG_SHAPE[1] * IMG_SHAPE[2] * 8

# --- STEP 1: Read video frames ---
cap = cv2.VideoCapture(VIDEO_PATH)
frames = []
while True:
    ret, frame = cap.read()
    if not ret:
        break
    frames.append(frame)
cap.release()

# --- STEP 2: Flatten frames to bytes ---
all_bytes = np.concatenate([f.flatten() for f in frames])

# --- STEP 3: Unpack bits and truncate to original size ---
all_bits = np.unpackbits(all_bytes)
orig_bits = all_bits[:IMG_SHAPE[0] * IMG_SHAPE[1] * IMG_SHAPE[2] * 8]
orig_bytes = np.packbits(orig_bits)

# --- STEP 4: Reshape and save image ---
img = orig_bytes.reshape(IMG_SHAPE).astype(np.uint8)
cv2.imwrite('recovered_image.jpg', img)
print("✅ Image recovered as recovered_image.jpg")