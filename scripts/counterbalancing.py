import random as rd

def main():
    AGs = ["AG1", "AG2", "AG3", "AG4"]
    labels = ["Gatoo", "Saldie", "NoLabel", "NoLabel"]
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
    cb_tests = ["HC", "TC"]
    
