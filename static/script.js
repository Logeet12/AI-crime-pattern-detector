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
 
    // Clear any previous analysis when regenerating
    document.getElementById("analysisContainer").innerHTML = "";
}
 
// Analyze Dataset
async function analyzeCrime() {
    const res = await fetch("/analyze");
    const data = await res.json();
 
    // Display analysed table below the Analyse button
    displayTable(data, "analysisContainer");
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