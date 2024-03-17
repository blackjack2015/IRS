# How to Calculate Camera-to-world Pose in the OpenCV-Style Coordinate System for IRS Dataset

## 0. Code

Please check the code [prepare_irs_dataset_pose.py](./prepare_irs_dataset_pose.py) on how to generate the opencv-style camera-to-world poses from the `UE_Trace.txt` files.

## 1. Raw Camera Pose in IRS Dataset

The raw camera poses in IRS dataset are generated in the Unreal Engine (UN), and saved in the "*/UE_Trace.txt" files.

- The `UE_trace.txt` is a text file containing the translation and orientation of the camera in a fixed coordinate frame (i.e., UE coordinate here). 

- Each line in the text file contains a single pose defined in the UE coordinate system (See below).

- The number of lines/poses is the same as the number of image frames in the current folder.

- The first 7 numbers of each line are '**tx ty tz qx qy qz qw**', where

  - **tx ty tz** give the camera-to-world translation (in centimeters) in UE coordinate system.
  - **qx qy qz qw** give a camera-to-world orientation in the form of a unit quaternion.


- For example, this file `*/IRS/Auxiliary/CameraPos/Restaurant/DinerEnvironment_Dark/UE_Trace.txt` gives

```plain
562.509460 554.905151 53.445610 0.004622 0.004660 -0.704158 0.710013 0.000000 0.000000 0.000000
562.510925 554.748474 65.385399 0.004622 0.004660 -0.704158 0.710013 0.025151 -2.628278 199.982956
562.512146 554.608765 76.015526 0.004622 0.004660 -0.704158 0.710013 0.021971 -2.629248 199.983032
...
...
...
```

where, you can find

```python
tx, ty,tz = 562.509460, 554.905151, 53.445610
tx /= 100.0 # centimeters to meters
ty /= 100.0
tz /= 100.0
qz, qy, qz, qw = 0.004622, 0.004660, -0.704158, 0.710013
# now you can convert a unit quaternion to a rotation matrix and so on ...
```

- Please check the code for more details.

```python
import numpy as np
# Load the pose file:
pose_src_file = 'IRS/Auxiliary/CameraPos/Restaurant/DinerEnvironment_Dark/UE_Trace.txt'
pose_quats = np.loadtxt(pose_src_file, comments='#', 
                        usecols = (0,1,2,3,4,5,6) # read first 7 elements;
                        ).astype(np.float32)
```

## 2. UE and OpenCV-Style Coordinates

### 2.1 Unreal Engine Coordinate System

- The Unreal Engine (UE) system uses the Cartesian coordinates (x Forward, y Right, z Up) to represent a position relative to a local origin.

- It is a left-hand coordinate system.

```plain

  +z (Up) | 
            |        / +x (Forward)
            |      / 
            |    / 
            |  /
 (Origin O) |/_ _ _ _ _ _ _ _ +y (to right, East)  

    UE Coordinate, Left-hand Coordinate System,
    assuming your eye is behind the y-O-z plane and seeing +x forward.
```

### 2.2 OpenCV Coordinate System

- OpenCV coordinate system uses the Cartesian coordinates as the x-axis pointing to the right, the y-axis downward, and the z-axis forward.

```plain
                  / +z (to Forward)
                /
              /
 (Origin O) /_ _ _ _ _ _ _   +x (to Right)
            |
            |
            |
            | +y (Down)

    OpenCV Coordinate, Right-hand Coordinate System,
    assuming your eye is behind the x-O-y plane and seeing +z forward. 
```

### 2.3 Why We Need OpenCV-style Camera Pose

It is because we use the following pipeline to connect RGB, camera, and world:

RGB image $(x,y)$ with $x$ pointing to the right, $y$ down, and image `origin` in the `left-top corner`
---> camera intrinsic K and inverse invK ---> camera points $P^{c}$ = $(X^{c}, Y^{c},Z^{c})$
---> camera extrinsic E and inverse invE ---> world points $P^{w}$ = $(X^{w}, Y^{w},Z^{w})$.


### 2.4 Notation

Assume we have the following coordinate systems:

- `wue`: the world coordinate in UE (x Forward, y Right, z Up) format;
- `cned`: the camera coordinate in UE (x Forward, y Right, z Up) format;
- `w`: the world coordinate in OpenCV style (x Right, y Down, z Forward);
- `c`: the camera coordinate in OpenCV style (x Right, y Down, z Forward);


### 2.5. How to get the transformation matrix from UE to OpenCV Style

- The matrix is defined as $T^{w}_{wue}$ to map the points $P^{wue}$ to the points $P^{w}$, i.e., $P^{w}$ = $T^{w}_{wue}$ * $P^{wue}$

- The matrix is `also` defined as $T^{c}_{cue}$ to map the points $P^{cuw}$ to the points $P^{c}$, i.e., $P^{c}$ = $T^{c}_{cue}$ * $P^{cue}$

- To find $T^{w}_{wue}$ is to project (or to calculate the `dot-product` between) each axis (as a unit vector) of $x^{wue}$, $y^{wue}$, $z^{wue}$, into the axis $x^w$, $y^w$, $z^w$. 
- *You can check the details in Chapter 2.2 of the book John J. Craig, Introduction to Robotics: Mechanics and Control, Third Edition (2005).*

- Following the coordinates drawn above, we can get this matrix as:

```python
    T = np.array([
                  [0,1,0,0],
                  [0,0,-1,0],
                  [1,0,0,0],
                  [0,0,0,1]], dtype=np.float32)
```

- And we have $T^{w}_{wue}$ = $T^{c}_{ue}$ = $T$.

## 3. How to map the camera-to-world pose in UE to OpenCV-Style

- OpenCV-style camera-to-world pose: 
  - We want to find the cam-to-world pose $T^{w}_{c}$, which do the mapping $P^w = T^{w}_{c} * P^{c}$.
  - note: `$T^{w}_{c}$` etc are in LaTex style if not shown correctly.


- Apply the chain rule, we have:

$T^{w}_{c}$ = $T^{w}_{wue}$ * $T^{wue}_{cue}$ * $T^{cue}_{c}$ = $T$ * `camera-to-world-pose-UE` * inv(T)

where, the `camera-to-wolrd pose in UE` can be loaded from the `UE_trace.txt` beforementioned.

## 4. Verify the Cameara Pose You Just Got

- The generated camera poses can be verified by depth warping among multi-view images. See an example from `OfficeMedley3/l_1.png` and `OfficeMedley3/l_3.png`.

![camera poses verified](./imgs/irs-cam-pose-check.png?raw=true "Camera pose verified by multi-view image warping")

You can find the pixel highlighted by a red circle is visually correctly warped into another view highlighted by a green circle.