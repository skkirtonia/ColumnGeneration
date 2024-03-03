import random
cutting_stock_length = 100
number_of_unique_cutting_length = 25
data_file_name = "data/simulated/data_simulated_2.txt"
# Randomly generated cutting lengths
cutting_lengths = sorted(random.sample(range(1, 70), number_of_unique_cutting_length))
# print(cutting_lengths)

# generate orders randomly
orders = {}
for each_length in cutting_lengths:
    # generate a random order quantity for the cutting length
    orders[each_length] = random.randint(100, 400)

# write data to txt file
with open(data_file_name, "w") as outfile:
    outfile.write(f"{cutting_stock_length}\n")
    outfile.write(f"{len(orders)}\n")
    for each_length, count_order in orders.items():
        outfile.writelines(f"{each_length}\t{count_order}\n")