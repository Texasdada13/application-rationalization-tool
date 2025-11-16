# Examples

This directory contains example scripts demonstrating various use cases and features of the Application Rationalization Assessment Tool.

## Available Examples

### 1. Custom Weights Example

**File:** `custom_weights_example.py`

Demonstrates how to customize scoring weights for different organizational priorities:
- Security-first organization
- Cost reduction initiative
- Digital transformation focus

**Usage:**
```bash
python examples/custom_weights_example.py
```

**What you'll learn:**
- Creating custom ScoringWeights configurations
- Running assessments with different weight profiles
- Comparing results across scenarios

---

### 2. Batch Processing Example

**File:** `batch_processing_example.py`

Shows how to process multiple application portfolios and generate comparative reports.

**Usage:**
```bash
python examples/batch_processing_example.py
```

**What you'll learn:**
- Processing multiple CSV files
- Generating comparative statistics
- Creating consolidated reports

**Customization:**
Edit the `portfolios` list in the script to add your own CSV files:

```python
portfolios = [
    {'file': Path('data/portfolio1.csv'), 'name': 'Portfolio 1'},
    {'file': Path('data/portfolio2.csv'), 'name': 'Portfolio 2'},
]
```

---

### 3. Score Breakdown Example

**File:** `score_breakdown_example.py`

Demonstrates detailed score analysis showing contribution from each criterion.

**Usage:**
```bash
python examples/score_breakdown_example.py
```

**What you'll learn:**
- Understanding what drives application scores
- Analyzing top and bottom performers
- Identifying improvement opportunities

**Output includes:**
- Detailed score breakdowns
- Top contributors to each score
- Analysis of high-value, low-score applications

---

## Creating Your Own Examples

To create a new example:

1. **Copy a template:**
   ```bash
   cp examples/custom_weights_example.py examples/my_example.py
   ```

2. **Update the imports:**
   ```python
   from src.data_handler import DataHandler
   from src.scoring_engine import ScoringEngine
   from src.recommendation_engine import RecommendationEngine
   ```

3. **Implement your logic:**
   ```python
   def main():
       # Your code here
       pass

   if __name__ == '__main__':
       main()
   ```

4. **Test it:**
   ```bash
   python examples/my_example.py
   ```

## Common Patterns

### Loading Data

```python
from src.data_handler import DataHandler

data_handler = DataHandler()
df = data_handler.read_csv('data/assessment_template.csv')
applications = df.to_dict('records')
```

### Calculating Scores

```python
from src.scoring_engine import ScoringEngine

engine = ScoringEngine()
scored_apps = engine.batch_calculate_scores(applications)
```

### Generating Recommendations

```python
from src.recommendation_engine import RecommendationEngine

rec_engine = RecommendationEngine()
results = rec_engine.batch_generate_recommendations(scored_apps)
```

### Saving Results

```python
import pandas as pd

results_df = pd.DataFrame(results)
data_handler.write_excel(results_df, 'output/my_results.xlsx')
```

## Tips

1. **Start simple**: Begin with the basic examples and gradually add complexity

2. **Use the template data**: The `data/assessment_template.csv` file is perfect for testing

3. **Check output**: Results are saved to the `output/` directory

4. **Read the docs**: See `docs/` for detailed documentation

5. **Ask for help**: Open an issue on GitHub if you get stuck

## Next Steps

After trying these examples, you might want to:

- Customize scoring weights for your organization
- Integrate with your CMDB or asset management system
- Build a dashboard or reporting tool
- Automate periodic assessments
- Create custom recommendation rules

Happy analyzing!
