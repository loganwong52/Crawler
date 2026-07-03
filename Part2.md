# PART 2
Logan wong

<!-- Provide design documentation to operationalize the collection of billions of URLs using the code
developed. 
Propose the next steps
how to further optimize for:
- cost
- reliability
- performance
- scale

Input:
List of billions of URLs send in via a text file and/or in MySQL for a given year month 
    e.g. billions of URLs for , , etc for July

Output: 
Design storage of the metadata and content. 
Design for unified data schema. 
Define SLOs and SLAs. 
Elaborate on the key monitoring metrics and tools you would employ to effectively track the system's progress. -->


## Input:
List of billions of URLs as a text file and/or in MySQL for a given year/month


## Optimizing Scale
To deal with billions of URLs, it would be best to not go through a frontend UI. Morever, instead of using a for loop to go through each URL, it would be better to use parallel processing via multiple threads, especially since there is no sequential aspect to this task. 

Each URL is independent of the others. Multiple threads can be run on a cloud virtual machine. Furthermore,  multiple threads can be run on a virtual machine. I would run hundereds of threads on hundreds of cloud virtual machines so they can run for however long is necessary and not rely on a local machine. 

1. A coordinator reads URLs from files/MySQL
2. The coordinator adds the URL to a queue
3. A thread gets a URL from the queue
4. Each thread runs on a loop: 
    1. Pass URLs into crawl() using parallel threads
    2. Save extracted metadata to storage
    3. Repeat

The number of virtual machines necessary will depend on time, computational resources, and budget.

## Optimizing Cost
It probably costs a few cents per hour to use a cloud virtual machine.

It takes a few seconds to extract metadata from 1 URL.

First, calculate how many total seconds it might take to extract info from all the URLs.
$$T_{sec} = N \times t$$
- $N$ = number of URLs
- $t$ = seconds to extract metadata from 1 URL

Then, convert that number of seconds into hours.
$$H_{total} = \frac{T_{sec}}{3600} = \frac{N \times t}{3600}$$

Then find how much it'll cost to use 1 cloud virtual machine for that long.
$$Cost = H_{total} \times c$$
- $c$ = cost per VM per hour

I'm assuming there's a set budget and that the total cost will be less than the total budget, $$Cost \le B$$ 

If the cost is too high, we'll have to find a cheaper virtual machine.

Of course, virtual machines aren't necessary, since threads can be run locally on computers.

It's important to note that parllelism only reduces time, not cost. So as far as I can tell, there isn't a way to reduce costs by increasing parallelism. Costs can be reduced if we use virtual machines with the lowest hourly rates.

It's more likely that there is a dadline for when the data needs to be processed. So there should be a given target completion time, $H_{target}$, rather than a target number of virtual machines to use.

So to find how many virtual machines are necessary:
$$M = \frac{H_{total}}{H_{target}} = \frac{N \times t}{3600 \times H_{target}}$$

Assuming there is an unlimited number of virtual machines, this is fine. However, if only a few machines are available, then we could do them in batches at a time.

Moreover, if there is a limited number of machines, but there's unlimited time, then to determine how long it will take to process all the URLs is:
$$H_{target} = \frac{H_{total}}{M} = \frac{N \times t}{3600 \times M}$$

Once M is determined, the number of URLs each virtual machine aka thread should handle is:
$$N_{thread} = \frac{N}{M}$$

Finally, k = number of concurrent threads running on 1 VM
$$total parallel threads = M \times k$$
So if each virtual machine has k threads rather than just 1, it will result in a faster completion time, so $$H_{target} = \frac{N \times t}{3600 \times M \times k}$$

N and k are both known constants, and as M and k increase, H_{target} approaches 0. Maxing M and k will result in the fastest completion time.


## Optimizing Performance
If multiple bots from the same IP address visit the same website too often in quick succession, all the bots might be detected and blocked. To avoid this, each thread will have a shared history of websites they've visted. A thread gets a URL from the list, it checks if it's allowed to visit or not. Basically this creates a cool-down period for visiting a website. If the website was visited recently, the thread will put that URL back in the list and get another one.

Throughput is how many URLs can be visited per hour. To maximize this value, increase M and k to their max, while decreasing t, the time it takes to extract metadata from the URL, to a minimum. M and k might be limited by the platform that offers virtual machines. 

t depends on internet speed, target server latency, and local parsing efficiency. Internt speed can be increased by having good wifi. Target server latency is how long the website's server takes to respond to a request. There might not be much one can do easily regarding this. Local parsing efficiency is how long the code takes to extract metadata. Parsing efficiency can depend on the library method used to read HTML because some HTML parsers are fasters than others. It also depends on what metadata is being extracted. While it's easy to extract the \<head\> and \<title\>, it will take longer to parse the entire \<body\>.

## Optimizing Reliability
I would optimize reliability by choosing the virtual machine platform that has the best user reviews while remaining under budget. 

Silent data loss, or silent failure, would be bad too. So if threads fail, I'd make it write a message about why it failed, then have another thread that was in the reserves pick up where the first thread failed.

Also, if metadata has no useful information (such as the JSON being full of null values), then the thread should set it aside for manual human inspection later and debugging.

Lastly, to store metadata, one might consider using a PostgreSQL database. However, to handle billions of metadata, a data lake would be better. It can store raw files, rather than needing to format things into columns. Moreover, multiple metadata can be stored in 1 file, known as Parquet files. So billions of URLs doesn't become billions of metadata files, but only thounsands of files. Once stored, they can be queried with a separate query tool.


## Output: 

### Storage of Metadata and Content
Billions of JSON metadata can be stored in thousands of Parquet files in a data lake and queried by a separate query tool, such as Apache Spark, DuckDB, Trino, or Amazon Athena.

### Unified Data Schema
The extracted metadata is the original URL, website name, page title, description, keywords, author, topics, Open Graph title, Open Graph description, Open Graph image, and the page body. Website name is the the domain name between www. and .com, .org, .net, etc. Title is the HTML title tag inside \<head\>.  Description is inside \<meta name="description" content="..."\> inside \<head\>. Keywords are the meta keywords. Topics is my own generated keywords extracted from the totality of title + description + body if keywords is None. Even if keywords do exist, they may or may not match topics, so I've included both. Author is inside \<meta name="author" content="..."\>. Open Graph title, description, and image are extracted from the respective Open Graph tags.

### SLOs and SLAs
<!-- SLO (Service Level Objective): A target you set internally for a metric. -->
Service Level Objectives are targets set internally for a metric. So this would be the exact number of URLs (in the billions), the number of virtual machines that can be used, and the number of threads each virtual machine will run in parallel. Additional SLOs would be the throughput, latency, and freshness.

<!-- SLA (Service Level Agreement): A promise to your users/customers, usually with consequences if broken. -->
Service Level Agreements are promises made to users/customers/company, and the consequences if that promise is broken. The SLAs are the deadline for when all the metadata needs to be extracted by, as well as accuracy, or correctness, that the extracted metadata is in face the desired metadata by the client.

### Key monitoring metrics
The key monitoring metrics are error rate, retry success rate, resource utilization, cost burn rate, and queue backlog.

Error Rate measures how many URL requests failed.

$$Error Rate = \frac{\text{failed requests}}{\text{total requests attempted}} \times 100$$

Retry Success Rate measures how many failed requests were retried and eventually succeeded 

$$Retry Success Rate = \frac{\text{retries that succeeded}}{\text{total retries attempted}} \times 100$$

Resource Utilization metrics include CPU usage, memory usage, and network I/O usage per VM. This will help identify bottlenecks.

Cost burn rate tracks the money spent per hour on the virtual machines. This will help ensure we don't go over budget and can help us determine budgets for future projects similar to this.

Queue backlog measures how many URLs remain to be processed, and its slope shows how fast or slow that number is changing.


### Tools to track system progress
Common tools to track system progress are Prometheus, Grafana, ELK, and PagerDuty. These are open-source DevOps tools used to monitor system performance. Monitored data includes performance metrics like system health, analyze logs, and  incident responses.

Prometheus is a way to monitor a system. It collects and stores data over a period of time. Grafana is a dashboard that shows the performance of something over a period of time, namely, the data collected by Prometheus. ELK is used to analyze system logs. E stands for elasticsearch, which is a search engine that stores tons of unstructred text data with instant search time. L stands for logstash, which is a pipeline to collect logs from various apps, process them, and send them to elasticsearch. K stands for kibana, which is a UI that lets users search, filter, and visualize log data. PagerDuty is a cloud-based incident response platform that uses AI to alert people that there's a problem.

Basically, the crawler would extract data from billions of URLs and Prometheus gets metrics for the crawler like URLs visited per hour, CPU usage, memory usage, and HTTP error rate. Grafana would display this data in a graph. ELK would store logs, which include error messages, and PagerDuty would alert humans if there is a problem, such as if the crawler stops processing URLs, or if the error rate exceeds a certain threshold.

