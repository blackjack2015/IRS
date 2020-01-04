dataset=irs
net=dispnormnet

model=models/dispnormnet-irs/model_best.pth
outf=detect_results/${net}-${dataset}/

filelist=lists/IRSDataset_TEST.list
filepath=data

CUDA_VISIBLE_DEVICES=2 python detecter.py --model $model --rp $outf --filelist $filelist --filepath $filepath --devices 0 --net ${net} --disp-on --norm-on
