import cv2
import numpy as np

# Load the image
image = cv2.imread('image1.jpg')  # Replace with your image path
cv2.imshow('Original', image)

# Resize to simulate pixelation (e.g., 32x32)
pixelated = cv2.resize(image, (32, 32), interpolation=cv2.INTER_LINEAR)

# Upscale back to original size (optional, for visual effect)
pixelated_up = cv2.resize(pixelated, image.shape[1::-1], interpolation=cv2.INTER_NEAREST)
cv2.imshow('Pixelated', pixelated_up)

# Convert to grayscale and then to bits
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
_, binary = cv2.threshold(gray, 127, 1, cv2.THRESH_BINARY)

# Flatten to bit array
bit_array = binary.flatten()
print("Bit array (first 100 bits):", bit_array[:100])

cv2.waitKey(0)
cv2.destroyAllWindows()