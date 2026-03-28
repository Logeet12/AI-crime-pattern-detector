function toggleAbout() {
    document.getElementById("about").classList.toggle("hidden");
}
 
// Generate Dataset
async function generateDataset() {
    const res = await fetch("/generate");
    const data = await res.json();
 
    displayTable(data, "datasetContainer");
 
    document.getElementById("analyzeBtn").classList.remove("hidden");
 
    // Clear previous analysis and charts
    document.getElementById("analysisContainer").innerHTML = "";
    document.getElementById("chartsSection").classList.add("hidden");
}
 
// Analyze Dataset + Load Charts
async function analyzeCrime() {
    // 1. Fetch analysed table
    const res = await fetch("/analyze");
    const data = await res.json();
    displayTable(data, "analysisContainer");
 
    // 2. Fetch and display EDA charts
    const chartRes = await fetch("/charts");
    const charts = await chartRes.json();
 
    const keys = ["correlation", "top_suspects", "distribution", "scatter"];
    keys.forEach(key => {
        const img = document.getElementById(`chart-${key}`);
        if (img && charts[key]) {
            img.src = charts[key];
        }
    });
 
    document.getElementById("chartsSection").classList.remove("hidden");
}
 
// Display Table
function displayTable(data, containerId) {
    if (!data || data.length === 0) {
        document.getElementById(containerId).innerHTML = "<p>No data available.</p>";
        return;
    }
 
    let table = "<table><tr>";
    for (let key in data[0]) {
        table += `<th>${key}</th>`;
    }
    table += "</tr>";
 
    data.forEach(row => {
        table += "<tr>";
        for (let key in row) {
            table += `<td>${row[key]}</td>`;
        }
        table += "</tr>";
    });
 
    table += "</table>";
    document.getElementById(containerId).innerHTML = table;
}