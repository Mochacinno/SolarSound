import numpy as np

# Given arrays
array1 = [4, 3, 9, 0, 9, 3, 9, 0, 5, 3, 9, 7, 8, 1, 5, 3, 8, 2, 0, 8, 6, 0, 7, 8, 1, 4]
array3 = np.array([0.60371882, 6.6176870, 21.84997732, 22.36081633, 32.25251701, 32.74013605, 
                   42.46929705, 42.9569161, 53.15047619, 63.87809524, 75.99891156, 77.81006803, 
                   98.4061678, 98.89378685, 119.1415873, 124.83047619, 139.50548753, 140.41106576, 
                   160.03192744, 177.53977324, 180.92988662, 186.61877551, 187.10639456, 207.0523356, 
                   208.0275737, 228.11283447, 241.20888889])

array2 = np.diff(array3)
print(array2)

# [ 6.01396818 15.23229032  0.51083901  9.89170068  0.48761904  9.729161
#   0.48761905 10.19356009 10.72761905 12.12081632  1.81115647 20.59609977
#   0.48761905 20.24780045  5.68888889 14.67501134  0.90557823 19.62086168
#  17.5078458   3.39011338  5.68888889  0.48761905 19.94594104  0.9752381
#  20.08526077 13.09605442]

res = []
for k in range(len(array1)):
    res.append("None")

for i in range(len(array1)):
    match = False
    for j in range(i+1, len(array1)):
        if array1[i] == array1[j]:
            if array2[i] > 3:
                if abs(array2[i] - array2[j]) < 1:
                    res[i] = array1[i]
                    res[j] = array1[j]
                    match = True
print(res)
res2 = []
for l in range(len(res)):
    if res[l] != "None":
        value = array3[l]+array2[l]
        res2.append([array3[l], array3[l]+array2[l]])
        
print(res2)

filtered_res = [x for x in res if x != 'None']
print(filtered_res)



