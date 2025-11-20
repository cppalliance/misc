## Request: BigQuery Access for Boost Library Investigation

### Overview
We need to investigate GitHub projects using the C++ Boost library. This requires access to Google BigQuery, which hosts the public GitHub dataset.

### Current Google Cloud Environment
- There is an existing Google Cloud project named `boost`.
- Multiple Google Cloud products are already enabled in this `boost` project.
- For the purposes of this request, we assume that BigQuery is already enabled in the `boost` project.

### Requested Actions

#### 1. Create a Separate Test Project
- Create a new Google Cloud **oss_stats** (separate from the main `boost` project) to use as a **test environment**.
- This test project will be used to experiment with BigQuery queries and configuration as much as needed, without impacting the main `boost` project.
- I will access this test project using my existing `cppalliance.org` Google account.

#### 2. Ensure BigQuery and Billing Are Available in the Test Project
- Confirm that BigQuery is enabled in the new test project (or enable it if needed).
- Ensure billing is configured so that paid BigQuery usage is allowed within the agreed budget.

### Budget and Cost Expectations (Per Iteration)
This work may involve multiple iterations / trials (e.g. refining queries, re-running scans, or adjusting the analysis). The cost and budget below are **per iteration**.

- **Budget Recommendation (per iteration)**: $5 is sufficient for each iteration of the investigation.
- The first 1 TiB of query processing per month is **free** per billing account.
- **Estimated Scan Size per Iteration**: ~1–1.4 TiB (C++ files in the GitHub dataset).
- **Overage per Iteration**: ~0–0.4 TiB (if scan exceeds the 1 TiB free tier).
- **Expected Cost per Iteration**: $0–2.50
  - If scan is ≤ 1 TiB: $0 (covered by the free tier)
  - If scan is 1.4 TiB: 0.4 TiB × $6.25/TiB = $2.50
- **Maximum Cost per Iteration**: $2.50
- **Budget Set per Iteration**: $5 (provides a safety margin)

### Why This Is Needed
- Google BigQuery provides access to the complete GitHub public dataset.
- This allows us to efficiently search millions of repositories for Boost library usage.
- The analysis will identify C++ projects using Boost across GitHub and support further reporting and decision-making.

### Timeline
Once the separate test project is created and billing is enabled, we can proceed immediately with the first iteration of the investigation. Additional iterations can be run later as needed, within the same per-iteration budget framework described above.
