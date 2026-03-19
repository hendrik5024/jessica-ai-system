- Use at least two machine learning algorithms and two optimization techniques.

---

```python
import numpy as np
from sklearn.cluster import KMeans
from scipy.optimize import minimize

# Helper function to simulate warehouse management problem
def simulate_warehouse_management(params, demand):
    # params: [stock_level, order_cost, holding_cost, penalty_cost]
    stock_level, order_cost, holding_cost, penalty_cost = params
    total_cost = 0
    penalties = 0
    
    for d in demand:
        if stock_level < d:
            shortage = d - stock_level
            penalties += shortage * penalty_cost
            total_cost += order_cost + shortage * holding_cost
            stock_level = 0
        else:
            stock_level -= d
            total_cost += holding_cost
    
    return total_cost + penalties

# Generate a sample demand for the warehouse
np.random.seed(0)
demand = np.random.randint(50, 150, size=30)

# Parameters for the warehouse management problem
params = [100, 100, 5, 20]

# Machine learning part: clustering the demand to identify patterns
kmeans = KMeans(n_clusters=3)
demand_clusters = kmeans.fit_predict(np.array(demand).reshape(-1, 1))

# Optimization part: optimizing the warehouse management parameters
def objective(params):
    return simulate_warehouse_management(params, demand)

# Initial guess for the optimization
initial_params = [100, 1
