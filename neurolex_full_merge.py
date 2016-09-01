import csv

#reference_list = [0, 98, 160, 89, 121, 48, 156, 148, 50, 49, 84, 69, 1, 68, 70, 34, 35, 103, 151, 59, 31, 25, 26, 104, 105, 120, 115, 116, 109, 180, 181]



with open('neurolex_full.csv', 'rt') as source1, open('neuron_data_curated.csv', 'rt') as source2:
    reader1=csv.reader(source1)
    reader2=csv.reader(source2)
    r1 = next(reader1)
    r2 = next(reader2)

reference_list = []

for r in r2:
    if r in r1:
        reference_list.append(r1.index(r))
    if r=='Species/taxa':
        reference_list.append(r1.index('Species'))
    else:
        pass

myReader = csv.reader(open('neuron_data_curated.csv'))

neuron_quick_ref = {}
for r in myReader:
    key = r[0]
    neuron_quick_ref[key] = r[1:]

with open('neurolex_full.csv', 'rt') as source, open('neurolex_full_merged.csv', 'wt') as result:
    reader=csv.reader(source)
    writer=csv.writer(result, lineterminator='\n')
    for row in reader:
        if (neuron_quick_ref.get(row[0],'none')!='none' and row[0]!='Categories'):
            my_updates = neuron_quick_ref[row[0]]
            new_row = row
            i = 0
            for my_ref in reference_list:
                if my_ref!=0:
                    new_row[my_ref] = my_updates[i]
                    i+=1
            writer.writerow(new_row)

        else:
            writer.writerow(row)






#add column for phenotypes
#combine the info of the two files (add neuron_data_curated to neurolex_full) with the big file

#replace old row with new row on ones that have been changed
#add column for phenotypes


#add to phenotypes branch of nlxeol

#updating rows
#check which columns exist and what column number they are equivalent to

