from module.list_files import list_files
from module.save_to_json import save_to_json

parameter = {
                'directory_path' : 'G:/',
                'output_json_file' : 'F:/files_transfer_project/file_details.json',
                'file_type' : 'ts',
                'limit' : '5', #default as ''
                }

file_details = list_files(parameter['directory_path'], parameter['file_type'],parameter['limit'])
save_to_json(file_details, parameter['output_json_file'])
