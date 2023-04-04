--Fix the Date data to the appropriate type

CREATE OR REPLACE TABLE `mla-dashboard-zoom.mla_bq_zoom.hist_trends_ok` (
`keyword` STRING,
`url` STRING,
`date` TIMESTAMP,
`ranking` INTEGER
) AS (
SELECT keyword, url, cast(Date AS TIMESTAMP), Ranking
FROM `mla-dashboard-zoom.mla_bq_zoom.hist_trends`
);

-- Create a partitioned table by date
CREATE OR REPLACE TABLE mla-dashboard-zoom.mla_bq_zoom.hist_trends_partitoned
PARTITION BY
  DATE(Date) AS
SELECT * FROM mla-dashboard-zoom.mla_bq_zoom.hist_trends;


