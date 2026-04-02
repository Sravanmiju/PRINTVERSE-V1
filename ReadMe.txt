2D to 3D Model Generation – Summary & Workflow
Summary
This project converts one or more 2D images into a fully textured 3D model using a local pretrained neural network model. The system does not use any external API for inference. It loads a pretrained Triplane + NeRF-style model locally (weights downloaded once from HuggingFace) and performs 3D reconstruction entirely on the user's machine. The workflow includes preprocessing, triplane encoding, volumetric rendering, mesh extraction, texture baking, and exporting final outputs such as OBJ, PLY, or GLB.
Workflow
1. Input 2D images are loaded.
2. Background is optionally removed using rembg.
3. Images are resized and centered.
4. A pretrained Triplane-based 3D model is loaded from HuggingFace (local inference, no online API).
5. Images are encoded into a Triplane representation (3 orthogonal feature planes).
6. NeRF-style volumetric rendering is used to generate 3D color + density fields.
7. Marching Cubes converts the density field into a 3D mesh.
8. xatlas + OpenGL baking create UV + texture maps.
9. Final 3D model is exported as OBJ / GLB / PLY along with texture images.


Actual technical workflow (what your system really does)
1️⃣ Image input

User uploads a single RGB/RGBA image

Image is loaded as a PIL image

2️⃣ Background removal (preprocessing)

Background is removed using rembg

Foreground object is:

Centered

Rescaled (foreground ratio)

Placed on a neutral background

📌 Purpose: isolate the object so the model focuses on shape, not clutter

3️⃣ Image normalization

Converted to RGB

Alpha channel filled

Resized to model-expected format

4️⃣ Image → latent 3D representation

The TripoSR model encodes the image

Produces a latent 3D scene code

This code represents the object as a continuous 3D field

🧠 This is where the “AI magic” happens

5️⃣ Implicit surface prediction

The model defines a function over 3D space

Determines where the surface of the object exists

Instead of vertices:

“Is this point inside or outside the object?”

6️⃣ Mesh extraction (Marching Cubes)

A 3D grid is sampled at chosen resolution

Marching Cubes converts the field into triangles

Higher resolution → more detail, slower speed

7️⃣ Orientation correction

Mesh is rotated to match Gradio’s coordinate system

Prevents flipped previews

8️⃣ Export formats

Mesh is exported as:

OBJ (classic, editable)

GLB (compact, web-friendly)

Saved as temporary files.

9️⃣ Display & download

Models are rendered in Gradio’s 3D viewer

User can rotate, inspect, and download