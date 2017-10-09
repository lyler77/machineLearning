f = open(r'watermelon.txt', 'r')
dataSet = []
lines = f.readlines()[1:]
for line in lines:
    dataSet.append([w for w in line.strip('\n').split(',')[1:]])
print(dataSet)