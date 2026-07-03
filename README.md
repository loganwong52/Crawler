# Crawler

## Running it locally
1. Inside crawler.py, set url variable equal to a string of the URL you want to visit. 
2. In the terminal, run: python crawler.py


## How to deploy it

1. To deploy it, run this:

    gcloud run deploy crawler --source . --region us-west1 --allow-unauthenticated --memory 2Gi --timeout 300

2. To see a console for print statements for debugging, open a separate terminal, and run this:

    gcloud beta run services logs tail crawler --region us-west1



## Running Live Demo
1. Visit https://crawler-880578276531.us-west1.run.app/
2. Input a URL inside the text box
3. Click the "Crawl" button
4. Click the "Download" button