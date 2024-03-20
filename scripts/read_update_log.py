import os
import json

root_dir = os.getcwd()
log_dir = os.path.join(root_dir, "logs")

log_file_name = "768194318584471b89cbb8c3146d0079.json"
log_file_path = os.path.join(log_dir, log_file_name)
log_data = []
with open(log_file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for line in lines:
        line = eval(line)
        kwargs = eval(line['kwargs'])
        if "log_type" in kwargs and kwargs['log_type'] == "Support update":
            log_data.append(line)
        if "log_type" in kwargs and kwargs['log_type'] == "Relation status":
            log_data.append(line)

save_dir = os.path.join(root_dir, "process_logs/update_logs")
if not os.path.exists(save_dir):
    os.makedirs(save_dir)
save_file = os.path.join(save_dir, log_file_name)
with open(save_file, 'a', encoding='utf-8') as f:
    for line in log_data:
        f.write(json.dumps(line, ensure_ascii=False) + '\n')