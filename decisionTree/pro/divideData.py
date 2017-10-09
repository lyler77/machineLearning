import numpy as np

f1=open(r'watermelon.txt','r')
#f1=open(r'breast-cancer-wisconsin.data','r')
f2=open(r'traindata.txt','w')
f3=open(r'testdata.txt','w')

raw=f1.readlines()
all=np.arange(len(raw))
np.random.shuffle(all)
all=list(all)
print(all)
train=int(len(raw)*0.7)
for i in range(len(raw)):
    if i < train:
        f2.write(raw[all[i]])
    else:
        f3.write(raw[all[i]])

f1.close()
f2.close()
f3.close()

