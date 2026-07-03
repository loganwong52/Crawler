# Part 3
<!-- Break down on how to proceed with engineering to Proof of Concept. | -->

<!-- What are the list of potential blockers. 
What are known and trivial and what are the estimates arrival time.

Implementation schedules. 
How to have a successful and high quality release.

Output: 
Documentations on how to proceed to next steps. 
Documentations of how to evaluate the proof of concept. 
Release plan and time estimations. -->


## Potential Blockers

### Known
Bot detectors might prevent us from visiting certain sites.

Pages might never finish loading, or timeout, due to ads or trackers. Instead of extracting metadata about the actual website, the crawler might extract information about the security verification by CloudflarePrivacy.

HTML content that might not be seen or missed.

Parsing text improperly.

Problems with Selenium. It launches a full browser instance per page, which is slower and uses up more memory/CPU than a plain HTTP request. Running k threads on 1 VM can use up a lot of memory. It also relies on a WebDriver that must match the installed browser version.

Missing metadata: not every page has the data I'm looking for, or I may have missed some edge cases on how to retrieve certain desirable metadata.

Duplication of URLs in the billions of URLs. To avoid having duplicate metadata, we could double check if that specific URL has already been visited already before deciding to pass it into crawl() or not.

If a VM crashes mid-write to a shared Parquet file, this could corrupt the whole file.

### Trivial
It'll take a long time to process all the URLs, so patience, money, energy, and time are needed.


# Release plan and time estimations

## Estimated arrival time
It takes maybe at least 10 seconds to extract metadata. If there's at least 2 billion URLs, that is 20 billion seconds, or 5,555,556 hours, or 634 years at least. To get this done in 1 week, or 168 hours, there would need to be around 33,000 parallel threads. 
$$\frac{5,555,556}{168} = 33,069$$

This can be done if there were 330 virtual machines each running 100 threads each. 1000 virtual machines running 33 threads each would also work.

## Implementation schedules

### Phase 1: Single-threaded crawler
Test a single-threaded crawler on a few sample URLs to confirm metadata extraction works.

Store metadata in data lake

Confirm retrieval of metadata using a query tool.

### Phase 2: 1 VM with multiple Threads
Run the crawler with `k` concurrent threads on 1 VM on 1000 URLs.

Measure metrics: error rate, retry success rate, resource utilization, cost burn rate, and queue backlog. 

Track and visualize metrics with Prometheus, Grafana, ELK, and PagerDuty.

Advance to next phase only if error rate is under a certain threshold and retry success rate is over a certain threshold.

### Phase 3: Multiple VMs with multiple Threads
Run 5 to 10 VMs on 1 to 10 million URLs.

Measure, track, and visualize metrics.

Confirm no duplicate URLs are processed, no Parquet write corruption under concurrent access, and extraction logic holds across all VMs.

Compare billing to see if everything will run according to budget.


### Phase 4: Full Production Run
Set `M` and `k` to the maximum allowed values to meet the deadline.

Monitor the virtual machines with a robust alert system if anything goes wrong.


### Weekly Schedule
| Week | Milestone |
|---|---|
| Week 1 | Phases 1 and 2 |
| Week 2 | Phases 2 and 3 |
| Week 3 | Phase 3 |
| Week 4 | Phase 3 and 4 |
| Week 5 | Phase 4 |
| Week 6 | Phase 4 |

## Task Estimate Breakdown
| Task | Estimate |
|---|---|
| Core crawler | 1-2 days |
| Correct Keyword extraction | 2–3 days |
| Multi-threaded single-VM version | 1–2 days |
| Multiple VMs, coordinator, and shared queue | 1 week |
| Rate-limiting and cool-down logic | 2–3 days |
| Parquet write pipeline and duplication removal | 3–5 days |
| Monitoring metrics and setting up an alert system | 2–3 days |
| Small-scale proof of concept run (thousands of URLs) | 1 day to run + 1 day to evaluate |
| Full production run | 1 or more weeks |



# How to evaluate the proof of concept

### Successful and high quality release
The way to have a successful and high quality release is to 
1. Ensure the proper metadata is extracted from all URLs, or if any metadata is missed, it can be considered as negligible.
2. Extract all metadata from the URLs by the deadline
3. Extract all the metadata from the URLs at or under budget.

To achieve this, we could first try extracting metadata from a handful of URLs whose metadata is easy, medium, and hard to extract from. Once we're confident about our results from that, it might be safe to apply our program to all of the URLs. 

# How to proceed to next steps
The next steps to do are:
1. Confirm Part 1's requirements. 
    
    Confirm the crawler correctly extracts keywords/topics for pages missing a `<meta name="keywords">` tag, since the instructions specifically asked for keywords.

2. Run single-threaded crawler on sample URLs to confirm metadata is stored correctly in the data lake and retrievable via a query tool.

3. Build concurrency and infrastructure:
    
    Multi-threading on 1 VM

    The multiple VM coordinator

    Shared queue

    Rate-limiting logic to prevent sites from detecting bots

    Track metrics: error rate, retry success rate, resource utilization, cost burn rate, and queue backlog.

4. Run multiple VM scale test on 1 to 10 million URLs. 
    Confirm no duplicate data. 
    
    Confirm Parquet write integrity under concurrency.
    
    Confirm the project stays within budget before committing to full scale.
    
    Set up full metric tracking and alert system with Prometheus, 
    
    Grafana, ELK, and PagerDuty.

5. Once Phase 3 passes its thresholds, increase `M` and `k` to maximum to run the crawlers on billions of URLs.
