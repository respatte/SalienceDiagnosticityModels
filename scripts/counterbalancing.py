import random as rd
import csv

def main():
    # Attention gatherers
    AGs = ["AG1", "AG2", "AG3", "AG4"]
    # Category names
    tail_cat = ["A", "B"]
    head_cat = ["1", "2"]
    # t/csv file headers
    header_cb = ["Participant"] + ["Fam"+str(i) for i in range(12)] + ["Ctr"+str(i) for i in range(3)] + ["WL"+str(i) for i in range(2)]
    header_pi = ["Participant", "First fam stim", "Name first fam stim", "First contrast", "Side new HC", "Side new TC", "Side new tail RC"]
    rows_cb = [header_cb]
    rows_pi = [header_pi]
    # Label condition (twice NoLabel to get even numbers
    # in both Label and NoLabel conditions)
    conditions = {"Label":["Gatoo", "Saldie"],
                  "NoLabel":["NoLabel", "NoLabel"]
                 }
    # Familiarisation stimlus names
    fam_stims = [{"Gatoo":[["A"+str(i)+"_G1" for i in range(1,7)],
                           ["A"+str(i)+"_G2" for i in range(1,7)]],
                  "Saldie":[["A"+str(i)+"_S1" for i in range(1,7)],
                            ["A"+str(i)+"_S2" for i in range(1,7)]],
                  "NoLabel":[["A"+str(i)+"_NL1" for i in range(1,7)],
                             ["A"+str(i)+"_NL2" for i in range(1,7)]]
                 },
                 {"Gatoo":[["B"+str(i)+"_G1" for i in range(1,7)],
                           ["B"+str(i)+"_G2" for i in range(1,7)]],
                  "Saldie":[["B"+str(i)+"_S1" for i in range(1,7)],
                            ["B"+str(i)+"_S2" for i in range(1,7)]],
                  "NoLabel":[["B"+str(i)+"_NL1" for i in range(1,7)],
                             ["B"+str(i)+"_NL2" for i in range(1,7)]]
                 }
                ]
    # Familiarisation stimulus order
    order1 = list(range(6))
    order2 = list(range(6))
    # Familiarisation counterbalancing
    p = 0
    while p < 48:
        for condition in conditions:
            for first_stim in (0,1):
                for name_first_stim in (0,1):
                    # Generte random order for each category
                    rd.shuffle(order1)
                    rd.shuffle(order2)
                    # Increment participant id (to start with participant 1)
                    p += 1
                    row_cb = [p]
                    row_pi = [p]
                    for i in range(12):
                        # Repeat the order twice to get 12 pres/cat in total, with AGs
                        row_cb.append(fam_stims[first_stim][conditions[condition][name_first_stim]][order1[i%6]])
                        row_cb.append(AGs[(2*i)%4])
                        row_cb.append(fam_stims[first_stim-1][conditions[condition][name_first_stim-1]][order2[i%6]])
                        row_cb.append(AGs[(2*i+1)%4])
                    row_pi.append([tail_cat[first_stim], conditions[condition][name_first_stim]])
                    rows_cb.append(row_cb)
                    rows_pi.append(row_pi)
    # Contrast tests
    cb_tests = ["HC", "TC"]
    Oh_HC_sides = ["L","R"]
    Ot_TC_sides = ["L","R"]
    Ot_RC_sides = ["L","R"]
    # Word-learning tests
    labels = ["Gatoo","Saldie"]
    A1_sides = ["L","R"]
    A2_sides = ["L","R"]
    # Contrast tests counterbalancing
    p = 0
    while p < 48:
        for first_test in (0,1):
            for Oh_HC in (0,1):
                for Ot_TC in (0,1):
                    for Ot_RC_side in (0,1):
                        p += 1
                        Ot_HC = random.choice(tail_cat)
                        Oh_HC_side = random.choice(Oh_HC_sides)
                        Oh_TC = random.choice(head_cat)
                        Ot_TC_side = random.choice(Ot_TC_sides)
                        HC_TC = {"HC":"HC_"+tail_cat[Ot_HC]+head_cat[Oh_HC]+Oh_HC_sides[Oh_HC_side],
                                 "TC":"TC_"+tail_cat[Ot_TC]+head_cat[Oh_TC]+Ot_TC_sides[Ot_TC_side]
                                }
                        RC = "RC_"+tail_cat[Ot_TC-1]+Ot_CR_sides[Ot_RC_side]+head_cat[Oh_HC-1]+Ot_RC_sides[Ot_RC_side-1]
                        rows_cb[p].append([HC_TC[cb_tests[first_test]], HC_TC[cb_tests[first_test-1]], RC])
                        rows_pi[p].append([cb_tests[first_test], Oh_HC_sides[Oh_HC_side-1],
                                           Ot_TC_sides[Ot_Tc_side-1], Ot_RC_sides[Ot_RC_side-1]]
    # Word learning tests counterbalancing
    p = 0
    while p < 48:
        # TODO
    
    with open('Counterbalancing.tsv', 'wb') as cb, open('ParticipantInfo.tsv', 'wb') as pi:
        cb = csv.writer(cb, delimiter='\t')
        pi = csv.writer(pi)
        cb.writerows(rows_cb)
        pi.writerows(rows_pi)
