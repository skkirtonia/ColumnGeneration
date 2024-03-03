import pandas as pd
from gurobipy import *
class SolverCuttingStock:
    def __init__(self, roll_length, orders):
        self.roll_length = roll_length
        self.orders = orders

        # generate initial cutting configurations
        self.configurations = {i + 1: {each_cutting_length: int(roll_length/each_cutting_length)} for i, each_cutting_length in
                  enumerate(orders.keys())}


    def solveMasterProblem(self, relaxed=True):
        model = Model('Column Generation MP')
        model.Params.OutputFlag = 0
        if relaxed:
            x = model.addVars(self.configurations.keys(), vtype=GRB.CONTINUOUS, name="x")
        else:
            x = model.addVars(self.configurations.keys(), vtype=GRB.INTEGER, name="x")
        model.setObjective(x.sum(), GRB.MINIMIZE)

        for s in self.orders.keys():
            model.addConstr(
                sum(x[c] * self.configurations[c][s] if s in self.configurations[c] else 0 for c in self.configurations.keys()) >= self.orders[s],
                name=f"C1_{s}")

        model.optimize()
        duals = {}

        if model.status == GRB.OPTIMAL:
            if relaxed:
                for each_length in self.orders.keys():
                    duals[each_length] = model.getConstrByName(f"C1_{each_length}").Pi
        else:
            print("No solution found")
        return duals, model


    def solveSubploblem(self, duals):
        model = Model('Column Generation Sub-problem')
        model.Params.OutputFlag = 0
        var_dict = {}
        for each_length in duals.keys():
            var_dict[each_length] = model.addVar(vtype=GRB.INTEGER, name=f"y_{each_length}")

        model.setObjective(sum(var_dict[length] * dual_values for length, dual_values in duals.items()), GRB.MAXIMIZE)
        model.addConstr(sum(var_dict[length] * length for length, dual_values in duals.items()) <= self.roll_length)
        model.optimize()

        # print(model.display())
        new_config = {}
        if model.status == GRB.OPTIMAL:
            reduced_cost = 1 - model.ObjVal
            # print("Iteration", iteration, "Reduced cost", reduced_cost)
            if reduced_cost < -0.000000001:
                for each_length in duals.keys():
                    if var_dict[each_length].X > 0.00001:
                        new_config[each_length] = int(var_dict[each_length].X)
            else:

                new_config = None

        else:
            print("No solution found")
        return new_config

    def solve(self):
        iteration = 0
        while True:
            duals, model = self.solveMasterProblem(relaxed=True)
            new_config = self.solveSubploblem(duals)
            if new_config is not None:
                self.configurations[max(self.configurations.keys()) + 1] = new_config
            else:
                break
            iteration = iteration + 1

        duals, model = self.solveMasterProblem(relaxed=False)
        solution = []

        for config_name in self.configurations.keys():
            var = model.getVarByName(f"x[{config_name}]")
            if var.X > 0.0001:
                solution.append((self.configurations[config_name], round(var.X)))

        return solution