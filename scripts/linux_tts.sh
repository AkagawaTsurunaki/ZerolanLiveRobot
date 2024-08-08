source activate GPTSoVits
# 注意修改您自己的 GPT-SoVits 路径
project_dir="../GPT-SoVITS"
cd $project_dir || { echo -e "Cannot find the project folder $project_dir. \nTo solve this problem, you may try:\n1. Check if the directory exists. \n2. Download GPT-SoVITS from https://github.com/AkagawaTsurunaki/GPT-SoVITS"; exit; }        
python3 api.py -p 11006