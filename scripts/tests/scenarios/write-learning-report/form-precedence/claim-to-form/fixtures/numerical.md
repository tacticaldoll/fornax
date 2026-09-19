# Source notes — a discrete queue model

A team was confusing service capacity with actual work completed. To separate them, it stipulated
a one-second-step queue model. q[t] is the number of jobs waiting at the start of step t; a[t] is
arrivals during that step; c[t] is the maximum jobs that can be served during it. All are
nonnegative integers measured in jobs per step, with q[t] a stock in jobs. Arrivals join before
service. Actual service is min(q[t]+a[t], c[t]); the next stock is the remaining jobs and cannot
be negative. No rejection, retries, or work carried in progress are modeled.

The illustrative source case starts with 7 jobs, then has 3 arrivals and capacity 5 per step.
The source supplies the next stock as 5 jobs. A second source case starts with zero jobs, has
1 arrival and capacity 5, serves only 1 job, and leaves zero waiting. A proposed implementation
returning -4 jobs on that case violates the nonnegative-stock rule. The point is conservation
with bounded service, not a measurement of a live queue. This is an explicit hypothetical model;
no run or experimental observation is supplied.
