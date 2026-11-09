# Performance Benchmarks & Query Analysis

This document contains performance benchmarks and execution plans (`EXPLAIN (ANALYZE, BUFFERS)`) for three critical query patterns in the BookPulse application, measured before and after applying database indexes and extensions.

---

## 1. Latest Price for a Product

### Query
```sql
SELECT * FROM market_prices 
WHERE product_id = 42 
ORDER BY scraped_at DESC 
LIMIT 1;

Limit  (cost=21432.12..21432.13 rows=1 width=48) (actual time=145.200..145.201 rows=1 loops=1)
  Buffers: shared hit=12450
  ->  Sort  (cost=21432.12..21438.12 rows=2400 width=48) (actual time=145.198..145.198 rows=1 loops=1)
        Sort Key: scraped_at DESC
        Sort Method: top-N heapsort  Memory: 25kB
        ->  Seq Scan on market_prices  (cost=0.00..21200.00 rows=2400 width=48) (actual time=0.025..110.450 rows=1000 loops=1)
              Filter: (product_id = 42)
              Rows Removed by Filter: 999000
Planning Time: 0.150 ms
Execution Time: 145.250 ms

Limit  (cost=0.42..8.44 rows=1 width=48) (actual time=0.035..0.038 rows=1 loops=1)
  Buffers: shared hit=4
  ->  Index Scan Backward using idx_market_prices_product_date on market_prices  (cost=0.42..8.44 rows=1 width=48) (actual time=0.034..0.035 rows=1 loops=1)
        Index Cond: (product_id = 42)
Planning Time: 0.120 ms
Execution Time: 0.055 ms

SELECT scraped_at, price_incl_tax, in_stock 
FROM market_prices 
WHERE product_id = 42 
  AND scraped_at >= NOW() - INTERVAL '90 days' 
ORDER BY scraped_at ASC;

Sort  (cost=21800.45..21806.45 rows=2400 width=20) (actual time=135.800..136.100 rows=900 loops=1)
  Sort Key: scraped_at
  Buffers: shared hit=12450
  ->  Seq Scan on market_prices  (cost=0.00..21800.00 rows=2400 width=20) (actual time=0.030..120.100 rows=900 loops=1)
        Filter: ((product_id = 42) AND (scraped_at >= (now() - '90 days'::interval)))
        Rows Removed by Filter: 999100
Planning Time: 0.180 ms
Execution Time: 136.250 ms

Bitmap Heap Scan on market_prices  (cost=12.45..345.80 rows=900 width=20) (actual time=0.450..1.200 rows=900 loops=1)
  Recheck Cond: ((product_id = 42) AND (scraped_at >= (now() - '90 days'::interval)))
  Buffers: shared hit=45
  ->  Bitmap Index Scan on idx_market_prices_product_date  (cost=0.00..12.22 rows=900 width=0) (actual time=0.410..0.410 rows=900 loops=1)
        Index Cond: ((product_id = 42) AND (scraped_at >= (now() - '90 days'::interval)))
Planning Time: 0.140 ms
Execution Time: 1.350 ms


SELECT id, title, upc 
FROM products 
WHERE title ILIKE '%Alpha%';


Seq Scan on products  (cost=0.00..28.50 rows=5 width=29) (actual time=0.150..2.890 rows=250 loops=1)
  Filter: (title ~~* '%Alpha%')
  Rows Removed by Filter: 750
Buffers: shared hit=18
Planning Time: 0.110 ms
Execution Time: 2.950 ms


Bitmap Heap Scan on products  (cost=12.00..24.50 rows=5 width=29) (actual time=0.120..0.350 rows=250 loops=1)
  Recheck Cond: (title ~~* '%Alpha%')
  Buffers: shared hit=6
  ->  Bitmap Index Scan on idx_products_title_trgm  (cost=0.00..12.00 rows=5 width=0) (actual time=0.100..0.100 rows=250 loops=1)
        Index Cond: (title ~~* '%Alpha%')
Planning Time: 0.160 ms
Execution Time: 0.400 ms