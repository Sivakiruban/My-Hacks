import cv2
import numpy as np

# Step 1: Load and resize image
image = cv2.imread('image1.jpg')  # Replace with your image path
resized = cv2.resize(image, (64, 64))  # Keep it small for demo

# Step 2: Convert image to bitstream
bitstream = np.unpackbits(resized.flatten())

# Step 3: Prepare video frames (1 frame = 64x64 pixels = 12288 bytes = 98304 bits)
frame_size = 64 * 64 * 3 * 8  # bits per frame
num_frames = int(np.ceil(len(bitstream) / frame_size))

# Pad bitstream to fit full frames
padded = np.pad(bitstream, (0, num_frames * frame_size - len(bitstream)), constant_values=0)

# Step 4: Convert bits back to frames
frames = padded.reshape((num_frames, 64, 64, 3, 8))
frames = np.packbits(frames, axis=-1).squeeze(-1).astype(np.uint8)

# Step 5: Write video
fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Use 'MJPG' or 'FFV1' for lossless
out = cv2.VideoWriter('output.avi', fourcc, 1, (64, 64))

for frame in frames:
    out.write(frame)

out.release()
print("✅ Video saved as output.avi")