import sys
import os
import re

ASE_file = open(sys.argv[1], 'r')
ASE_data = ASE_file.readlines()
ASE_file.close

normals_raw = [x for x in (re.findall(r'.+MESH_VERTEXNORMAL ([0-9]*)\t(.+)\t(.+)\t(.+)',line) 
            for line in ASE_data) if x != []]
tverts_raw = [x for x in (re.findall(r'.+MESH_TVERT ([0-9]*)\t(.+)\t(.+)\t(.+)',line) 
            for line in ASE_data) if x != []]
vertices_raw = [x for x in (re.findall(r'.+MESH_VERTEX *([0-9]*)\t(.+)\t(.+)\t(.+)',line) 
            for line in ASE_data) if x != []]
mface_raw =  [x for x in (re.findall(r'.+MESH_FACE *([0-9]*):.+A:.+?([0-9]+).+B:.+?([0-9]+).+C:.+?([0-9]+).+AB.+',line) 
            for line in ASE_data) if x != []]
tface_raw = [x for x in (re.findall(r'.+MESH_TFACE ([0-9]*)\t(.+)\t(.+)\t(.+)',line) 
            for line in ASE_data) if x != []]

vertices = [None] * len(vertices_raw)
normals = [None] * len(vertices_raw)
tverts = [None] * len(vertices_raw)
tfaces = [None] * len(vertices_raw)
faces = [None] * len(vertices_raw)

for i in range(len(vertices)):
    vertices[int(vertices_raw[i][0][0])] = vertices_raw[i][0][1] + " " + vertices_raw[i][0][2] + " " + vertices_raw[i][0][3]
    normals[int(normals_raw[i][0][0])] = normals_raw[i][0][1] + " " + normals_raw[i][0][3] + " " + str(float(normals_raw[i][0][2]) * -1)

for i in range(len(mface_raw)):
    faces[3 * int(mface_raw[i][0][0])] = mface_raw[i][0][1]
    faces[3 * int(mface_raw[i][0][0]) + 1] = mface_raw[i][0][2]
    faces[3 * int(mface_raw[i][0][0]) + 2] = mface_raw[i][0][3]

for i in range(len(tface_raw)):
    tfaces[3 * int(tface_raw[i][0][0])] = tface_raw[i][0][1]
    tfaces[3 * int(tface_raw[i][0][0]) + 1] = tface_raw[i][0][2]
    tfaces[3 * int(tface_raw[i][0][0]) + 2] = tface_raw[i][0][3]

for i in range(len(tverts)):
    tverts[int(faces[i])] = tverts_raw[int(tfaces[i])][0][1]  + " " + tverts_raw[int(tfaces[i])][0][2]

num_vertices = str(len(vertices))
num_faces = str(len(faces)/3)

RA2_file = open(os.path.splitext(sys.argv[1])[0] + ".bot", "wb")

BotBoilerplate = """1.12
Name: """ + os.path.basename(os.path.splitext(sys.argv[1])[0]) + """
Class: 0
0
false
1
-1
0
0
0 0 0
0 0 0 1
0 0
Chassis

3
600 600
400 600
500 400
3
600 600
400 600
500 400
0.346364 """ + num_faces + """
true
274 """ + num_vertices  + " " + num_vertices + " " + num_faces + """
1
""" + num_vertices + " " + num_faces + " " + num_vertices +""" 0
RAW
"""
tverts_pixels = [None] * len(vertices_raw)

for i in range(len(tverts)):
    tverts_pixels[i] = " ".join([str(float(x)*256) for x in tverts[i].split()])

face_groups = [None] * int(num_faces)
texture_squares = [None] * int(num_faces)
texture_groups = [None] * int(num_faces)

for i in range(int(num_faces)):
    face_groups[i] = "\n3\n" + tverts_pixels[int(faces[i * 3])] + "\n" + tverts_pixels[int(faces[i * 3 + 1])] + "\n" + tverts_pixels[int(faces[i * 3 + 2])]
    Tex_Xcoordinates = [[float(x) for x in tverts_pixels[int(faces[i * 3])].split()][0],
                       [float(x) for x in tverts_pixels[int(faces[i * 3 + 1])].split()][0],
                       [float(x) for x in tverts_pixels[int(faces[i * 3 + 2])].split()][0]]
    Tex_Ycoordinates = [[float(x) for x in tverts_pixels[int(faces[i * 3])].split()][1],
                       [float(x) for x in tverts_pixels[int(faces[i * 3 + 1])].split()][1],
                       [float(x) for x in tverts_pixels[int(faces[i * 3 + 2])].split()][1]]
    texture_squares[i] = str(i) + " " + str(int(min(Tex_Xcoordinates))) + " " + str(int(min(Tex_Ycoordinates))) + " " + str(int(round(max(Tex_Xcoordinates)))) + " " + str(int(round(max(Tex_Ycoordinates))))
    texture_groups[i] = str(i) + " " + faces[i * 3] + " " + faces[i * 3 + 1] + " " + faces[i * 3 + 2]
    
BotEndplate = """false
false
""" + num_faces + "".join(face_groups) + "\n" + num_faces + "\n" + "\n".join(texture_squares)  + "\n" + num_faces  + "\n" + "\n".join(texture_groups) + """
1
0 3 0 1 2  
1 12 0 200 0
1 1 1 1 0
0
false
0
0
0
"""
RA2_file.writelines(BotBoilerplate)
RA2_file.writelines("%s\n" % l for l in normals)
RA2_file.writelines("%s\n" % l for l in tverts)
RA2_file.writelines("%s\n" % l for l in vertices)
RA2_file.writelines("%s\n" % l for l in faces)
RA2_file.writelines(BotEndplate)
RA2_file.close()
if int(num_faces) > 86:
    print "WARNING - Over 86 faces in model will crash RA2 when bot get attacked\nPress Enter to quit..."
    raw_input()
