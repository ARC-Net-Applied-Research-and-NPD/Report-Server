import json 
values = []
labels = []
with open(r'json/output.json' , 'r') as fp:
    data = json.load(fp)
items = list(data.items()) 
for i in range(4, 8):
    values.append(items[i][1])
    labels.append(items[i][0])
print(values, labels)