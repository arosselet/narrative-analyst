# Narrative Analysis: AQI Forecasting

## The Stake 
Breathing safe air is a basic human expectation. City managers depend on numbers to trigger health warnings or traffic diversions.

## The Official Story 
The standard narrative is that environmental monitoring is sufficient for public safety. We measure pollution, report it, and citizens take precautions.

## The Divergence 
This monitoring is **Diagnostic**, not **Proactive**. It reports pollution levels *after* citizens have already breathed them. 

The proposal introduces a **Predictive** model that forecasts AQI 24 hours in advance, allowing city managers to act *before* the peak pollution thresholds are reached.

## The Mechanism (The Structural Machine)
1. **Atmospheric Stagnation**: Specific combinations of low wind speed and high pressure trap air.
2. **Urban Mobility**: Transit and industrial activity inject pollutants into that trapped air.
3. **Leading Indicators**: The model prioritizes these causes (Stagnation + Mobility) rather than reactive sensors.
4. **Data Fusion**: Merges geospatial, daily weather, and urban activity to train the model.
5. **Causal Shift**: Strictly **excludes current pollutant levels** to avoid temporal persistence and force the model to learn early-warning signals.
