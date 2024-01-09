import json
import os
    
from module.convert_to_mp4 import convert_to_mp4

def process_videos( **kwargs):
    json_file = kwargs.get('json_file_path')
    output_path = kwargs.get('output_path')
    limit_video = (kwargs.get('limit_video', None))
    file_filter = kwargs.get('file_filter')
    print(limit_video)
    
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
        
    if file_filter != None:
        filter_path = [item for item in data if item['type'].lower() == file_filter]
    else:
        filter_path = [item for item in data if item['type'].lower() != 'mp4'] 
    
    
    if limit_video is not None:
        limit_video = int(limit_video)
        limited_data = filter_path[:limit_video]
    else:
        limited_data = filter_path
    
    count = 0
    for item in limited_data:
        if count >= len(limited_data):
            break

        if item['transfer_status'] == 'none':
            output_file = os.path.join(output_path, os.path.splitext(os.path.basename(item['file_path']))[0] + '.mp4')
            print('intput:',item['file_path'])    
            print('output:', output_file)
            
            if convert_to_mp4(item['file_path'], output_file):
                item['transfer_status'] = 'success'
            count += 1
        
        # count += 1

    with open(json_file, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

parameter = {
    'output_path': r'F:\files_transfer_project\output_video',
    'json_file_path': r'F:\files_transfer_project\file_details.json',
    'limit_video': None,
    # 'limit_video': 20,
    'file_filter' : None,
    # 'file_filter' : 'ts',
}

process_videos(**parameter)