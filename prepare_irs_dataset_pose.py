import os
import numpy as np
import sys
from glob import glob

#import tqdm
from os import path as osp
from scipy.spatial.transform import Rotation

scenes = [
    'Office',
    'Home', 
    'Restaurant', 
    'Store',
    ]

""" 
# To get a 4x4 transformation matrix from 
# a translation vector (tx,ty,tz) and 
# a unit quaternion (qx qy qz qw).
"""
def pos_quat2SE_matrix(quat_data # [tx ty tz qx qy qz qw], tx,ty,tz in meter;
        ):
    SO = Rotation.from_quat(quat_data[3:7]).as_matrix()
    SE = np.eye(4)
    SE[0:3,0:3] = SO
    SE[0:3,3]   = quat_data[0:3]
    return SE

# Unreal Engine coordinates to OpenCV-style coordinates;
def ue2cam(quat_data):
    '''
    # wue: world coordinate in Unreal Engine (x Forward, y Right, z Up) format;
    # cue: camera coordinate in Unreal Engine (x Forward, y Right, z Up) format;
    # w: world coordinate in OpenCV style (x Right, y Down, z Forward);
    # c: camera coordinate in OpenCV style (x Right, y Down, z Forward);
    # To find T_wue_2_w is to project each axis of x^wue, y^wue, z^wue, 
    # into axis x^w, y^w, z^w,
    # i.e., P^w = T_{wue}^{w} * P^{wue}
    '''
    
    # To find $T^{w}_{wue}$ is to project (or to calculate the `dot-product` between) 
    # each axis (as a unit vector) of $x^{wue}$, $y^{wue}$, $z^{wue}$, 
    # into the axis $x^w$, $y^w$, $z^w$.
    # > see: You can check the details in Chapter 2.2 of the book John J. Craig, 
    # Introduction to Robotics: Mechanics and Control, Third Edition (2005).
    T = np.array([
                  [0,1,0,0],
                  [0,0,-1,0],
                  [1,0,0,0],
                  [0,0,0,1]], dtype=np.float32)
    T_wue_2_w = T
    # Similarly, we can find the transformation from cue to c;
    T_cue_2_c = T
    T_c_2_cnet = np.linalg.inv(T_cue_2_c)
    T_cue_2_wue = pos_quat2SE_matrix(quat_data)
    #NOTE: We want to find the pose between c and w in OpenCV style coordinates;
    # That is to say to find the cam-to-world pose T^{w}_{c}, 
    # which maps P^w = T^{w}_{c} * P^{c};
    # Using the chain-rule:
    # T^{w}_{c} = T^{w}_{wue} * T^{wue}_{cue} * T^{cue}_{c}
    T_cam_2_world = np.matmul(np.matmul(T_wue_2_w, T_cue_2_wue), T_c_2_cnet)
    return T_cam_2_world

if __name__ == '__main__':

    data_root = "./data/IRS"
    for seq in scenes:
        scan_paths = sorted(
            # one example: */IRS/Restaurant/DinerEnvironment_Dark/l_1.png
            glob(osp.join(data_root, seq, f"*/"))
            )
        for scan in scan_paths:
            print ("scan = ", scan)
            
            # e.g., scan = */IRS/Restaurant/DinerEnvironment_Dark/
            # to get "DinerEnvironment_Dark";
            if scan.endswith("/"):
                cur_P0X = scan[:-1].split("/")[-1] 
            else:
                cur_P0X = scan.split("/")[-1] 
            
            print ("cur_folder = ", cur_P0X)
            
            # e.g., = */IRS/Auxiliary/CameraPos/Restaurant/DinerEnvironment_Dark/UE_Trace.txt
            pose_src_file = osp.join(data_root, f'Auxiliary/CameraPos/{seq}/{cur_P0X}/UE_Trace.txt')
            if os.path.exists(pose_src_file):
                dst_pose_dir = osp.join(data_root, seq, cur_P0X, f"pose_me_left")
                #os.system(f"rm -rf {dst_pose_dir}")
                os.makedirs(dst_pose_dir, exist_ok=True)
                pose_quats = np.loadtxt(pose_src_file, comments='#', 
                                        usecols = (0,1,2,3,4,5,6) # read first 7 elements;
                                        ).astype(np.float32)
                #print ("??? pose_quats ", pose_quats.shape)
                img_paths = glob(osp.join(scan, 'l_*.png'))
                assert len(img_paths) == pose_quats.shape[0], f"Requires #image {len(img_paths)} == #pose {pose_quats.shape[0]}"
                print (f"read from {pose_src_file}, and save to {dst_pose_dir}")
                for i in range(pose_quats.shape[0]):
                    # i+1: image name starting from 1, 2, 3, ...;
                    pose_txtfile = osp.join(dst_pose_dir, f"{i+1:06d}_left.txt")
                    #if not os.path.exists(pose_txtfile):
                    quat = pose_quats[i,:7] # [tx ty tz qx qy qz qw]
                    # change tx, ty, tz from cm to meters
                    quat[:3] = quat[:3] / 100.0 # cm to meters;
                    T_cam2world_invE = ue2cam(quat)
                    np.savetxt(pose_txtfile, T_cam2world_invE)
                    #if i > 5:
                    #  sys.exit()