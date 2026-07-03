// 2 functions called when buttons are clicked on the frontend
let lastResult = "";

function crawl() {
    let resultEl = document.getElementById("result");
    let crawlBtn = document.getElementById("crawlBtn");
    let downloadBtn = document.getElementById("download");

    resultEl.textContent = "Loading...";
    crawlBtn.disabled = true;
    downloadBtn.style.display = "none";

    let url = document.getElementById("url").value;
    fetch("/crawl?url=" + encodeURIComponent(url))
        .then(r => r.json())
        .then(data => {
            lastResult = JSON.stringify(data, null, 2);
            resultEl.textContent = lastResult;
            downloadBtn.style.display = "inline-block";
        })
        .catch(err => {
            resultEl.textContent = "Error: " + err.message;
        })
        .finally(() => {
            crawlBtn.disabled = false;
        });
}

function downloadFile() {
    let blob = new Blob([lastResult], { type: "text/plain" });
    let a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "metadata.txt";
    a.click();
}