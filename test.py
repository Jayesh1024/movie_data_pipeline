import re
running_time='2 hr 18 min'
running_time_pattern=r'(\d)\s*hr\s*(\d*)\s*min'
re_match=re.findall(pattern=running_time_pattern,string=running_time)

print(str(minutes))