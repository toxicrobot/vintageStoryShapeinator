import math
import xml.etree.ElementTree as ET
import base64
import blackboxprotobuf
import os




## this converts my cuboid to an integer by using specific bits for specific voxel locations :3
# thank you so much to enderbro3300 for this!
# also your username is the exact same scheme as the gmail I made when I was like 10 lmfao

def cuboid_to_int(c):
    xmax, ymax, zmax, xmin, ymin, zmin = c

    return (
        (zmax << 0)  |
        (ymax << 4)  |
        (xmax << 8)  |
        (zmin << 12) |
        (ymin << 16) |
        (xmin << 20)
    )


## this uses protobuf magic to convert my voxels idfk whats going on there once again thank you enderbro
def encode_voxels(voxels):
    msg = blackboxprotobuf.encode_message(
        {"1": voxels},
        {"1": {"type": "int", "name": ""}}
    )
    return base64.b64encode(msg).decode("utf-8")



def write_file(voxels, name, filename):
    # I have trust issues
    if os.path.exists(filename):
        os.remove(filename)

    root = ET.Element("PantographData")

    ET.SubElement(root, "name").text = name
    ET.SubElement(root, "voxeldata").text = encode_voxels(voxels)
    # just used some random bullshit
    ET.SubElement(root, "matdata").text = "CIo8"
    ET.SubElement(root, "materialPasteOK").text = "true"

    tree = ET.ElementTree(root)
    ET.indent(tree)

    with open(filename, "wb") as f:
        f.write(b'<?xml version="1.0" encoding="utf-8"?>\n')
        tree.write(f, encoding="utf-8")







from enum import Enum
# technically not necessary but I love enums I wish I could kiss them
class Normal(Enum):
    Y =1
    Z =2
    X = 3


##
# Generates a circle Σ:3
# radius is in blocks since that makes it easier to visualise in my head 
# height and thickness however rarely exceeds 1 block so voxels it is
# the normal defines where the circle (or any other shape) "points" to
# if the thickness is -1 it just makes a solid
##
def circleVintageStory(blockRadius, height=1, normal=Normal.Y, thickness=-1):
    # Scale to voxels
    radius = blockRadius * 16
    
    # Calculate the strict integer bounding box
    max_range = math.ceil(radius)
    max_height_range = math.ceil(height / 2)

    cx = cy = cz = radius

    voxels = []
    inner = max(0, radius - thickness) if thickness != -1 else -1
    
    # when the height is odd there will be 1 extra voxel on the bottom half
    for h_int in range(-max_height_range, max_height_range-(height%2)):
        # center of the voxel instead of the corner
        h = h_int + 0.5
        if abs(h) > height / 2:
            continue
        for a_int in range(-max_range, max_range):
            for b_int in range(-max_range, max_range):
                # same difference
                a = a_int + 0.5
                b = b_int + 0.5

                # euclidian distance 
                dist2 = a*a + b*b

                if dist2 > radius*radius:
                    continue

                if dist2 < inner*inner:
                    continue

                # Convert back to integer voxel coordinates based on the normal axis
                if normal == Normal.Y:
                    # Height goes along Y axis, circle is on X and Z
                    x, y, z = int(cx + a_int), int(cy + h_int), int(cz + b_int)
                elif normal == Normal.X:
                    # Height goes along X axis, circle is on Y and Z
                    x, y, z = int(cx + h_int), int(cy + a_int), int(cz + b_int)
                elif normal == Normal.Z:
                    # Height goes along Z axis, circle is on X and Y
                    x, y, z = int(cx + a_int), int(cy + b_int), int(cz + h_int)

                voxels.append((x, y, z))

    return voxels


##
# Generates a sphere Σ:3 
# same difference as above 
# no height cus its a sphere 
##
def sphereVintageStory(blockRadius, thickness=-1):
    radius = blockRadius * 16
    max_range = math.ceil(radius)
    
    cx = cy = cz = radius
    voxels = []

    inner = max(0, radius - thickness) if thickness != -1 else 0

    for a_int in range(-max_range, max_range):
        for b_int in range(-max_range, max_range):
            for c_int in range(-max_range, max_range):
                a = a_int + 0.5
                b = b_int + 0.5
                c = c_int + 0.5

                dist2 = a*a + b*b + c*c

                if dist2 > radius * radius:
                    continue

                if dist2 < inner * inner:
                    continue

                x, y, z = int(cx + a_int), int(cy + b_int), int(cz + c_int)
                voxels.append((x, y, z))

    return voxels



##
# Generates a torus :) for details see above
# also note that the radius is the outer bounding circle of the shape
# so a torus with a diameter of 3 blocks will fit inside a 3x3x3 space (3x3x1 but swagever)
##
def torusVintageStory(blockRadius, smallRadius=1, normal=Normal.Y, thickness=-1):
    # Scale total outer radius to voxels
    R_outer = blockRadius * 16
    
    r = smallRadius

    # torus calculations are done with the big R in the center of the circle being "revolved" so I sqish it down
    # note that if you want to make a torus where the donut hole is the block size (useful for putting a torus over a column or something for some ottoman shit) you can just add instead!
    R = R_outer - r
    #fuck you
    if R <= 0:
        raise ValueError("height (minor radius) cannot be greater than or equal to blockRadius!")

    # Main ring plane spans up to R_outer, while the hole axis spans up to r
    max_ring_range = math.ceil(R_outer)
    max_height_range = math.ceil(r)

    cx = cy = cz = max_ring_range

    voxels = []
    
    # Inner minor radius for a hollow tube if youre nasty like that ig
    inner_r = max(0, r - thickness) if thickness != -1 else -1
    
    # Determine coordinate bounds based on the normal axis
    x_range = max_height_range if normal == Normal.X else max_ring_range
    y_range = max_height_range if normal == Normal.Y else max_ring_range
    z_range = max_height_range if normal == Normal.Z else max_ring_range

   
    for x_int in range(-x_range, x_range):
        for y_int in range(-y_range, y_range):
            for z_int in range(-z_range, z_range):
                
                # Shift to voxel centers
                dx = x_int + 0.5
                dy = y_int + 0.5
                dz = z_int + 0.5

                # Assign torus axes based on the chosen Normal vector
                # 'h' is the axis of the torus hole (woahg,,,,)
                # 'a' and 'b' form the main 2D plane of the ring
                if normal == Normal.Y:
                    a, h, b = dx, dy, dz
                elif normal == Normal.X:
                    h, a, b = dx, dy, dz
                elif normal == Normal.Z:
                    a, b, h = dx, dy, dz


                # vector math!

                # 1. Find the distance from the hole axis to the voxel in the main plane
                dist_from_axis = math.sqrt(a*a + b*b)
                
                # 2. Find the distance from the voxel to the center line of the tube
                dr_a = dist_from_axis - R
                
                # 3. Calculate final distance squared from the tube center line
                dist2_to_tube = dr_a*dr_a + h*h

                # Check if the voxel is outside the tube
                if dist2_to_tube > r * r:
                    continue

                # Check if the voxel is inside the hollow core  
                if dist2_to_tube < inner_r * inner_r:
                    continue

                x = int(cx + x_int)
                y = int(cy + y_int)
                z = int(cz + z_int)

                voxels.append((x, y, z))

    return voxels





from collections import defaultdict
import math

import math




def remove_inner_chunks(chunks):
    # Find the absolute outer boundaries of your chunk grid
    min_cx = min(cx for cx, _, _ in chunks.keys())
    max_cx = max(cx for cx, _, _ in chunks.keys())
    
    min_cy = min(cy for _, cy, _ in chunks.keys())
    max_cy = max(cy for _, cy, _ in chunks.keys())
    
    min_cz = min(cz for _, _, cz in chunks.keys())
    max_cz = max(cz for _, _, cz in chunks.keys())

    chunks_to_remove = []

    for (cx, cy, cz) in chunks.keys():
        # If it's NOT on ANY of the outer walls, it's an inner chunk.
        is_outermost = (
            ((cx == min_cx or cx == max_cx) and min_cx != max_cx) or
            ((cy == min_cy or cy == max_cy) and min_cy != max_cy) or
            ((cz == min_cz or cz == max_cz) and min_cz != max_cz) 
        )
        
        if not is_outermost:
            chunks_to_remove.append((cx, cy, cz))

    for key in chunks_to_remove:
        del chunks[key]

    return chunks



CHUNK_SIZE = 16
def split_into_chunks(voxels):
    # create a dictionary!
    chunks = defaultdict(list)

    for x, y, z in voxels:
        # figures out which chunk it belongs to
        cx = x // CHUNK_SIZE
        cy = y // CHUNK_SIZE
        cz = z // CHUNK_SIZE

        # figures out where in the above figured out chunk it belongs to
        lx = x % CHUNK_SIZE
        ly = y % CHUNK_SIZE
        lz = z % CHUNK_SIZE

        #adds it to that chunk with those coordinates :3
        chunks[(cx, cy, cz)].append((lx, ly, lz))

    return chunks

import os
import shutil

def write_chunks(chunks, base_name="circle"):

    if os.path.exists(base_name):
        shutil.rmtree(base_name)

    os.makedirs(base_name, exist_ok=True)


    ## ngl I hate this whole code block I just did some bullshti until I got numbers I like

    min_cx = min(cx for cx, _, _ in chunks.keys())
    min_cy = min(cy for _, cy, _ in chunks.keys())
    min_cz = min(cz for _, _, cz in chunks.keys())

    max_cx = max(cx for cx, _, _ in chunks.keys())
    max_cy = max(cy for _, cy, _ in chunks.keys())
    max_cz = max(cz for _, _, cz in chunks.keys())

    size_x = max_cx - min_cx
    size_y = max_cy - min_cy
    size_z = max_cz - min_cz


    i = 0
    for (cx, cy, cz) in chunks.keys():
        voxels = chunks[(cx, cy, cz)]


        # dont worry about what cy cx or cz mean, I got confused a bunch and eventually it worked and I decided that it doesnt matter
        # also we dont have negative coordinates fuck that

        # normalize
        nx = cx - min_cx
        ny = cy - min_cy
        nz = cz - min_cz

        # flipped cus woops
        nx = size_x - nx    
        nz = size_z - nz    
        ny = size_y - ny 

        ## orders the file based on height first, then it goes from 

        filename = f"{base_name}/#GENERATED#+{base_name}_y{ny:d}z{nx:d}x{nz:d}"

        xmlName = f"{base_name}y{ny:d}z{nx:d}x{nz:d}"

        # this turns my points into 1x1 cuboids since vintage story usually is efficient and packs a bunch of cubes into one. Not here, sorryyy <3
        cuboids = [(x, y, z, x, y, z) for x, y, z in voxels]

        # this encodes the cuboids into the singular integer that vs then stores
        encoded = [cuboid_to_int(c) for c in cuboids]

        # this writes the file, in there it encodes it into whatever the fuck the blackboxprotobuf does
        write_file(
            encoded,
            name=f"{xmlName}",
            filename=filename
        )
        i = i+1
    print(i)


# =========================
# RUN
# =========================



if __name__ == "__main__":
    # creates my circle :) 
    voxels = torusVintageStory(
        blockRadius=3/2,
        smallRadius = 5,
        thickness=-1
    )
    # removes duplicates just in case
    voxels = list(set(voxels))

    # splits my voxels into the 16x16x16 chunks
    chunks = split_into_chunks(voxels)

    #optional! If your sphere/circle is supposed to not be circular on the inside, you can remove the inner chunks :) useful if you are making something you cant go inside of anyways, 
    # or if you want a sphere on top of a quader
    #chunks = remove_inner_chunks(chunks)

    write_chunks(chunks, base_name="circle")
