import random as rd

def main():
    # Attention gatherers
    AGs = ["AG1", "AG2", "AG3", "AG4"]
    # Label condition (twice NoLabel to get even numbers
    # in both Label and NoLabel conditions)
    conditions = ["Gatoo", "Saldie", "NoLabel", "NoLabel"]
    # Familiarisation stimlus names
    fam_A = {"Gatoo":[["A"+str(i)+"_G1" for i in range(1,7)],
                      ["A"+str(i)+"_G2" for i in range(1,7)]],
             "Saldie":[["A"+str(i)+"_S1" for i in range(1,7)],
                       ["A"+str(i)+"_S2" for i in range(1,7)]],
             "NoLabel":[["A"+str(i)+"_NL1" for i in range(1,7)],
                        ["A"+str(i)+"_NL2" for i in range(1,7)]]
             }
    fam_B = {"Gatoo":[["B"+str(i)+"_G1" for i in range(1,7)],
                      ["B"+str(i)+"_G2" for i in range(1,7)]],
             "Saldie":[["B"+str(i)+"_S1" for i in range(1,7)],
                       ["B"+str(i)+"_S2" for i in range(1,7)]],
             "NoLabel":[["B"+str(i)+"_NL1" for i in range(1,7)],
                        ["B"+str(i)+"_NL2" for i in range(1,7)]]
             }
    # Contrast tests
    cb_tests = ["HC", "TC"]
    N_HC_sides = ["L","R"]
    N_TC_sides = ["L","R"]
    Nt_RC_sides = ["L","R"]
    # Word-learning tests
    labels = ["Gatoo","Saldie"]
    A1_sides = ["L","R"]
    A2_sides = ["L","R"]
