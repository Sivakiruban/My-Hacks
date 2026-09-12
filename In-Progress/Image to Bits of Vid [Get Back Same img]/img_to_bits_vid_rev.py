import cv2
import numpy as np

# Step 1: Read video frames
cap = cv2.VideoCapture('output.avi')  # Use the same filename from encoding
frames = []

while True:
    ret, frame = cap.read()
    if not ret:
        break
    frames.append(frame)

cap.release()

# Step 2: Convert frames to bits
frames_np = np.array(frames)
bits = np.unpackbits(frames_np.flatten())

# Step 3: Reconstruct original image shape
# You must know the original image shape (e.g., 64x64x3)
original_shape = (64, 64, 3)
original_size = np.prod(original_shape) * 8  # bits

# Trim excess bits
image_bits = bits[:original_size]

# Convert bits back to pixel values
image_bytes = np.packbits(image_bits).reshape(original_shape).astype(np.uint8)

# Step 4: Show and save reconstructed image
cv2.imshow('Reconstructed Image', image_bytes)
cv2.imwrite('reconstructed.jpg', image_bytes)
cv2.waitKey(0)
cv2.destroyAllWindows()