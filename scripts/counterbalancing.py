import random as rd
import csv

def main():
    # Attention gatherers
    AGs = ["AG1", "AG2", "AG3", "AG4"]
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
    # Category names
    cat = ["A", "B"]
    # Contrast tests
    cb_tests = ["HC", "TC"]
    N_HC_sides = ["L","R"]
    N_TC_sides = ["L","R"]
    Nt_RC_sides = ["L","R"]
    # Word-learning tests
    labels = ["Gatoo","Saldie"]
    A1_sides = ["L","R"]
    A2_sides = ["L","R"]
    # Iterating over all values to create each order row
    with open('Counterbalancing.tsv', 'wb') as cb, open('ParticipantInfo.tsv', 'wb') as pi:
        cb = csv.writer(cb, delimiter='\t')
        pi = csv.writer(pi, delimiter='\t')
        # TODO: write headers (first row)
        header_cb = ["Participant"] + ["Fam"+str(i) for i in range(12)] + ["Ctr"+str(i) for i in range(3)] + ["WL"+str(i) for i in range(2)]
        header_pi = ["Participant", "First stim", "Name first stim"]

        p = 0
        while p < 48:
            row_cb = [p]
            row_pi = [p]
            for condition in conditions:
                for first_stim in (0,1):
                    for name_first_stim in (0,1):
                        rd.shuffle(order1)
                        rd.shuffle(order2)
                        for i in range(6):
                            row_cb.append(fam_stims[first_stim][conditions[condition][name_first_stim]][order1[i]])
                            row_cb.append(fam_stims[first_stim-1][conditions[condition][name_first_stim-1]][order2[i]])
                        row_pi.append([cat[first_stim], conditions[condition][name_first_stim]])
