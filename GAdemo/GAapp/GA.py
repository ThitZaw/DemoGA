import itertools, pandas, random


def generate_individual(buyer, buyer_data, seller_data, seller):
    gene = []
    fitness = []

    for i in range(len(buyer)):
        gene.append(seller_data[random.randint(0, len(seller) - 1)])
    individual = dict(zip(buyer_data, gene))
    return individual


def Population(population_size, buyer, buyer_data, seller_data, seller):
    population = []
    size = population_size
    for i in range(size):
        population.append(generate_individual(buyer, buyer_data, seller_data, seller))
    return population


def totalfitness(individual, buyer, seller, seller_inventory, buyer_csv_info, seller_price, seller_discount,
                 seller_minamt):
    buyer_remainingqty = dict(zip(buyer.id.tolist(), [0] * len(buyer)))
    seller_soldamt = dict(zip(seller.id.tolist(), [0] * len(seller)))
    seller_inventory_temp = seller_inventory.copy()
    seller_original_inventory = seller_inventory.copy()
    buyer_csv_info = buyer_csv_info.copy()
    seller_price = seller_price.copy()
    totalfitness = 0
    saving = 0
    valid_pair = []
    for key, value in individual.items():
        Ind_seller = value
        Ind_buyer = key
        if seller_inventory_temp[Ind_seller] >= buyer_csv_info[Ind_buyer]:
            valid_pair.append(1)
            seller_soldamt[Ind_seller] += buyer_csv_info[Ind_buyer] * seller_price[Ind_seller]
            seller_inventory_temp[Ind_seller] -= buyer_csv_info[Ind_buyer]
        else:
            valid_pair.append(0)
            buyer_remainingqty[Ind_buyer] = buyer_csv_info[Ind_buyer] - seller_inventory_temp[Ind_seller]
            seller_soldamt[Ind_seller] += seller_inventory_temp[Ind_seller] * seller_price[Ind_seller]
            seller_inventory_temp[Ind_seller] = 0

    if all(valid_pair):
        for key, value in seller_soldamt.items():
            if seller_soldamt[key] > seller_minamt[key]:
                saving += seller_soldamt[key] * (seller_discount[key] / 100)
    return saving,seller_soldamt


def selTournament(population, k, individual_fitness):
    best = {}
    for i in range(k):
        ind = population[random.randint(0, len(population) - 1)]
        fitness_best = 0
        fitness_ind = 0
        if not best:
            for i in individual_fitness:
                if best in i:
                    fitness_best = i[1]
        for i in individual_fitness:
            if ind in i:
                fitness_ind = i[1]

        if not best or fitness_ind > fitness_best:
            best = ind
    return best


def Crossover(p1, p2):
    rate = len(p1)
    ca = random.randint(0, rate)
    cb = random.randint(0, rate)

    if ca > cb:
        temp = cb
        cb = ca
        ca = temp

    child1 = []

    mom = list(p1.values())
    dad = list(p2.values())

    for i in range(rate):
        if i < ca:
            child1.append(dad[i])

        elif i < cb:
            child1.append(mom[i])

        else:
            child1.append(dad[i])

    return child1


def changemutation(child, mutationRate, seller_data):
    rate = len(child)
    # choose the crossover point to change from the individual
    ca = random.randint(0, rate - 1)
    # choose the seller to change
    selected_seller = seller_data[random.randint(0, len(seller_data) - 1)]
    random_point = random.random()
    if (random_point < mutationRate):
        child[ca] = selected_seller

    return child


def bestfittest(individual_fitness):
    # search the best individual among population.
    best_fittest = individual_fitness[0]
    for i in range(len(individual_fitness)):
        if best_fittest[1] <= individual_fitness[i][1]:
            best_fittest = individual_fitness[i]
    return best_fittest[0],best_fittest[1]

def generate_poplation_fitness(population, buyer, seller, seller_inventory, buyer_csv_info, seller_price,
                               seller_discount, seller_minamt):
    population_fitness = []
    for i in range(len(population)):
        fitness,seller_soldamt = totalfitness(population[i], buyer, seller, seller_inventory, buyer_csv_info, seller_price,
                               seller_discount, seller_minamt)
        population_fitness.append([population[i], fitness])
    return population_fitness


def flipped(valid_pair):
    flipped = {}
    for key, value in valid_pair.items():
        if value not in flipped:
            flipped[value] = [key]
        else:
            flipped[value] += [key]
    return flipped

def divide_profit(buyer_csv_info,each_buyer_saving):
    eachsellersoldamt = each_buyer_saving
    buyer_csv_info = buyer_csv_info

    buyer_saving = {}
    for i, j in eachsellersoldamt.items():
        total_group_buy_qty = 0

        # Calculate total quantity of each coalition
        for buyer in j:
            total_group_buy_qty += buyer_csv_info[buyer]


        for buyer in j:
            #calculate the percentage for each buyer in each coalition
            P = (buyer_csv_info[buyer] / total_group_buy_qty) * 100
            saving = i * (P / 100)
            buyer_saving[buyer] = round(saving, 2)

    return buyer_saving


def GAalgorithm(buyer,seller,termination,population_size,crossover,mutationRate):
    buyer = buyer
    buyer_csv_info = dict(zip(buyer.id.tolist(), buyer.quantity.tolist()))
    buyer_data = buyer.id.tolist()

    seller = seller
    seller_csv_info = seller.to_dict()
    seller_inventory = dict(zip(seller.id.tolist(), seller.inventory.tolist()))
    seller_discount = dict(zip(seller.id.tolist(), seller.discount.tolist()))
    seller_price = dict(zip(seller.id.tolist(), seller.price.tolist()))
    seller_minamt = dict(zip(seller.id.tolist(), seller.minAmount.tolist()))
    seller_data = seller.id.tolist()

    k = 5
    final_population = []
    generation = 0
    population = []
    population_fitness = []
    termination = termination
    population_size = population_size
    crossover = crossover
    mutationRate = mutationRate
    each_seller_saving = {}


    initial_population = Population(population_size, buyer, buyer_data, seller_data, seller)

    individual_fitness = generate_poplation_fitness(initial_population, buyer, seller, seller_inventory,
                                                       buyer_csv_info,
                                                       seller_price, seller_discount, seller_minamt)

    population.append(initial_population)
    population_fitness.append(individual_fitness)
    while (generation < termination):
        new_population = []
        sorted_seller_buyer = []
        best_fittest = bestfittest(population_fitness[generation])
        new_population.append(best_fittest[0])
        for i in range(population_size - 1):
            parent1 = selTournament(population[generation], k, population_fitness[generation])
            parent2 = selTournament(population[generation], k, population_fitness[generation])
            child = Crossover(parent1, parent2)
            mutated_child = changemutation(child, mutationRate, seller_data)
            new_population.append(dict(zip(buyer_data, mutated_child)))
        new_population_fittness = generate_poplation_fitness(new_population, buyer, seller, seller_inventory,
                                                                buyer_csv_info, seller_price, seller_discount,
                                                                seller_minamt)
        generation += 1
        population.append(new_population)
        population_fitness.append(new_population_fittness)
        bestfittestpair = bestfittest((population_fitness[generation]))
        total_saving, each_seller_sold_amt = totalfitness(bestfittestpair[0], buyer, seller,
                                                     seller_inventory, buyer_csv_info, seller_price, seller_discount,seller_minamt)

    for key,value in each_seller_sold_amt.items():
        if each_seller_sold_amt[key] >= seller_minamt[key]:
            each_seller_saving[key] = each_seller_sold_amt[key] * (seller_discount[key] / 100)

    seller_buyer_pair = flipped(bestfittestpair[0])
    each_buyer_saving = {}

    for seller in each_seller_saving:
        if seller in seller_buyer_pair:
           each_buyer_saving[each_seller_saving[seller]] = seller_buyer_pair[seller]

    buyer_saving = divide_profit(buyer_csv_info,each_buyer_saving)

    return bestfittestpair[0],bestfittestpair[1],seller_buyer_pair,each_buyer_saving,buyer_saving
