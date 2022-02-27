# MICROSERVICE FOR CATRINA'S BUDGETING APP
# Written by: Emily Tchai
# CS361 Software Engineering I (Winter 2022)

#reads values.txt and adds contents to an array
with open('values.txt', 'r') as read_f:   #using 'with' closes file after execution
    values_arr = list(map(float, read_f.readlines()))

#calculate sum array
if values_arr:  #if values_arr is not null/empty
    sums_arr=[values_arr[0]]
    n = len(values_arr)

    for i in range(1, n):
        values_arr[i] += values_arr[i-1]
        sums_arr.append(values_arr[i])

    # print(sums_arr)

# write running totals to sums.txt file
with open('sums.txt', 'w+') as write_f:
    for sum_value in sums_arr:
        write_f.write(str(sum_value)+'\n')
