function toggleAbout() {
    document.getElementById("about").classList.toggle("hidden");
}

// Generate Dataset
async function generateDataset() {
    const res = await fetch("/generate");
    const data = await res.json();

    displayTable(data, "datasetContainer");

    // Show Analyse button below the dataset
    document.getElementById("analyzeBtn").classList.remove("hidden");

    // Clear any previous analysis and hide charts when regenerating
    document.getElementById("analysisContainer").innerHTML = "";
    document.getElementById("chartsSection").classList.add("hidden");
}

// Analyze Dataset + Load Charts
async function analyzeCrime() {
    // Step 1: fetch and display analysed table
    const res = await fetch("/analyze");
    const data = await res.json();
    displayTable(data, "analysisContainer");

    // Step 2: fetch charts and display them below the table
    const chartRes = await fetch("/charts");
    const charts = await chartRes.json();

    ["correlation", "top_suspects", "distribution", "scatter"].forEach(key => {
        const img = document.getElementById(`chart-${key}`);
        if (img && charts[key]) {
            img.src = charts[key];
        }
    });

    document.getElementById("chartsSection").classList.remove("hidden");
}

// Display Table Function
function displayTable(data, containerId) {
    if (!data || data.length === 0) {
        document.getElementById(containerId).innerHTML = "<p>No data available.</p>";
        return;
    }

    let table = "<table><tr>";

    // Headers
    for (let key in data[0]) {
        table += `<th>${key}</th>`;
    }
    table += "</tr>";

    // Rows
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