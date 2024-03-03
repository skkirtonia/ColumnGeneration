from gurobipy import *
d_s = {"l3": 7, "l4": 5, "l5": 7, "l6": 12}
l_s = {"l3": 3, "l4": 4, "l5": 5, "l6": 6}
board_id = [f"r{i+1}" for i in range(25)]

model = Model('Column Generation LP')
x_sb = model.addVars(d_s.keys(), board_id, vtype=GRB.INTEGER, name="x")
y_b = model.addVars(board_id)

model.setObjective(y_b.sum(), GRB.MINIMIZE)

for b in board_id:
    model.addConstr(sum(x_sb[s, b] * l_s[s] for s in d_s.keys()) <= 10, name=f"C_{b}")

for b in board_id:
    for s in d_s.keys():
        model.addConstr(100000*y_b[b] >= x_sb[s, b], name=f"c2_{s}_{b}")

for s in d_s.keys():
    model.addConstr(sum(x_sb[s,b] for b in board_id) >= d_s[s], name=f"c3_{s}")

# model = model.relax()
model.optimize()
print(model.status)
if model.status == GRB.OPTIMAL:
    for var in model.getVars():
        if var.X == 1:
            print(var.VarName, var.X)

    # for cons in model.getConstrs():
    #     print(cons.Pi)