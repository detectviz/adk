# Availability Table

Availability is generally calculated based on how long a service was unavailable over some period. Assuming no planned downtime, Table 1-1 indicates how much downtime is permitted to reach a given availability level.

- Table 1-1. Availability table

| Availability (%) | Downtime per year | Downtime per month | Downtime per week | Downtime per day |
|------------------|------------------|--------------------|-------------------|------------------|
| 99.999           | 5m 15.4s         | 25.9s              | 6.05s             | 864.3ms          |
| 99.99            | 52m 33.6s        | 4m 21.0s           | 1m 0.5s           | 8.6s             |
| 99.9             | 8h 45m 57.0s     | 43m 49.7s          | 10m 4.8s          | 1m 26.4s         |
| 99.5             | 1d 19h 47m 52.6s | 3h 39m 7.2s        | 50m 24.0s         | 4m 48.0s         |
| 99.0             | 3d 15h 39m 29.5s | 7h 18m 17.0s       | 1h 40m 48.0s      | 14m 24.0s        |
| 98.0             | 7d 7h 18m 59.0s  | 14h 36m 34.1s      | 3h 21m 36.0s      | 28m 48.0s        |
| 95.0             | 18d 6h           | 36h                | 8h 24m            | 1h 12m           |
| 90.0             | 36d 12h          | 72h                | 16h 48m           | 2h 24m           |


Using an aggregate unavailability metric (i.e., " X % of all operations failed") is more useful than focusing on outage lengths for services that may be partially available for instance, due to having multiple replicas, only some of which are unavailable and for services whose load varies over the course of a day or week rather than remaining constant.

See Equations Time-based availability and Aggregate availability in Embracing Risk for calculations.