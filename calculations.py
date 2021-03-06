import math

def accuracy(five, ten, three, miss, r=2):

    # five = 50s
    # ten = 100s
    # three = 300s
    # miss = X

    return round(100*(50*five + 100*ten + 300*three) / (300* (five+ten+three+miss)),r)


# Funtion to determine if a score is a choke
def choke(miss, rank, avg_pp, pp, ten, combo, perfect):

    
    
    if int(perfect):
        return 0
    score = 0
    if int(miss) <= 5:
        miss_score = -2.3 * (int(miss)**2)
    else:
        miss_score = 1.2 ** -(int(miss)-25)
    if int(miss) == 0:
        score -= 50


    score += miss_score

    if int(ten) < 0.05 * int(combo):
        score += (int(combo)/3) / int(ten)  

    if int(pp) > int(avg_pp) and miss_score > 41:
        score += (int(pp)*15) / int(avg_pp)
    else:
        score *= 0.8

    if rank == "A":
        score += 15
    
    return score

