// Wait for the HTML to fully load before running any JavaScript
document.addEventListener('DOMContentLoaded', async () => {
// --- Cluster Options ---
const clusterSelect = document.getElementById('n_clusters');
if (clusterSelect) {
    for (let i = 2; i <= 6; i++) {
        let option = document.createElement('option');
        option.value = i;
        option.text = i;
        clusterSelect.appendChild(option);
    }
    // Attach listener safely inside the check
    clusterSelect.addEventListener('change', runClustering);
} else {
    console.error("Select element with id 'n_clusters' not found.");
}

// --- Frequency Options ---
const frequencySelect = document.getElementById('frequency');
    const freqList = ['Monthly', 'Monthly (de-seasoned)', 'Yearly'];
    
    if (frequencySelect) {
        // Use forEach for cleaner array iteration
        freqList.forEach(freq => {
            let option = document.createElement('option');
            option.value = freq;
            option.text = freq;
            frequencySelect.appendChild(option);
        });
        // Attach listener safely inside the check
        frequencySelect.addEventListener('change', runClustering);
    } else {
        console.error("Select element with id 'frequency' not found.");
    }

    
// --- Type Options ---

    async function fetchTypeOptions() {
        try {
            const response = await fetch('/api/get_cols');
            const data = await response.json();
            const cols = data.cols;
            console.log("Data received from Flask:", data); 

            const typeSelect = document.getElementById('type-checkboxes');

            cols.forEach(col => {
                const div = document.createElement('div');
                div.className = 'form-check mb-2'; // Combined classList and className

                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.id = `cb-${col}`;
                checkbox.value = col; // Removed the leading space you had here
                checkbox.checked = false;

                checkbox.addEventListener('change', renderSelectedCharts);

                const label = document.createElement('label');
                label.className = 'form-check-label ms-2';
                label.htmlFor = `cb-${col}`;
                label.textContent = col;   

                div.appendChild(checkbox);
                div.appendChild(label);
                typeSelect.appendChild(div);
            });
        } catch (error) {
            console.error("Failed to load column checkboxes:", error);
        }
    }

    let globalChartsData = {}; // Global variable to store individual charts data

        document.getElementById('btn-select-all').addEventListener('click', () => {
        document.querySelectorAll('#type-checkboxes input[type="checkbox"]').forEach(cb => cb.checked = true);
        renderSelectedCharts(); // Redraw instantly!
    });

    document.getElementById('btn-clear-all').addEventListener('click', () => {
        document.querySelectorAll('#type-checkboxes input[type="checkbox"]').forEach(cb => cb.checked = false);
        renderSelectedCharts(); // Redraw instantly!
    });

    function renderSelectedCharts() {
    const container = document.getElementById('scatter-plot');
    container.innerHTML = ''; // Clear out the old charts

    const checkedBoxes = document.querySelectorAll('#type-checkboxes input[type="checkbox"]:checked');
    checkedBoxes.forEach(cb => {
        const Type = cb.value.trim();

        if(globalChartsData[Type]) {
            const chartDiv = document.createElement('div');
            chartDiv.id = `chart-${Type}`;

            container.appendChild(chartDiv);

            const chartData = JSON.parse(globalChartsData[Type]);
            Plotly.newPlot(chartDiv.id, chartData.data, chartData.layout);
        }
    });
}


// --- Fetch parameter and run analysis ---
    async function runClustering() {
        const optiomalClusterInfo = document.getElementById('optimal-cluster-info');
        optiomalClusterInfo.innerHTML = ''; // Clear previous optimal cluster info

        // Safely parse values
        const payload = {
            n_clusters: parseInt(document.getElementById('n_clusters').value, 10),
            frequency: document.getElementById('frequency').value,
            type: Array.from(document.querySelectorAll('#type-checkboxes input[type="checkbox"]:checked'))
                       .map(cb => cb.value.trim())
        };
        
        console.log("Payload to be sent to Flask:", payload); 

        const loadingMessage = document.getElementById('loading-message');
        loadingMessage.textContent = '⏳ Running analysis... Please wait.';
        loadingMessage.style="color: #007bff; font-weight: bold; margin-bottom: 15px;"
        loadingMessage.style.display = 'block';

        const doenMessage = document.getElementById('done-message');
        doenMessage.style.display = 'none';
        const tableBody = document.getElementById('detailed-scores');
        tableBody.innerHTML = ''; // Clear out old data
        try {
            const response = await fetch('/api/run_clustering', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            const nClusters = data.n_clusters_range;
            const dbScores = data.db_scores;
            const optimal_n_clusters = data.optimal_n_clusters;
            const dbScoresOptimal = dbScores[optimal_n_clusters - 2]; // Adjusting index for 0-based array
            

            const doenMessage = document.getElementById('done-message');
            doenMessage.style.display = 'block';

            const optiomalClusterInfo = document.getElementById('optimal-cluster-info');
            optiomalClusterInfo.textContent = `Optimal number of clusters: ${optimal_n_clusters} (with DB Score: ${dbScoresOptimal.toFixed(4)})`;



            // Build the HTML rows
            for (let i = 0; i < nClusters.length; i++) {
                const clusterCount = nClusters[i];
                const score = dbScores[i].toFixed(4);

                if (clusterCount == optimal_n_clusters) {
                    const rowHtml = `
                        <tr style="color: #ff8892; font-style: italic">
                            <td>${clusterCount}</td>
                            <td>${score}</td>
                        </tr>
                        `;
                    tableBody.insertAdjacentHTML('beforeend', rowHtml);
                    } else {
                    const rowHtml = `
                        <tr>
                            <td>${clusterCount}</td>
                            <td>${score}</td>
                        </tr>
                        `;
                    tableBody.insertAdjacentHTML('beforeend', rowHtml);
                    }
            }


        // Draw mnain chart
            const mainChartData = JSON.parse(data.main_chart);
            Plotly.newPlot('main-chart', mainChartData.data, mainChartData.layout);

        // Store individual charts data for later use
            globalChartsData = data.scatter_plots; // Store the individual charts data globally
            renderSelectedCharts(); // Render the charts based on the current selections

        } catch (error) {
            console.error("Error occurred while fetching clustering results:", error);
        } finally {
            const loadingMessage = document.getElementById('loading-message');
            loadingMessage.style.display = 'none';
        }
    }

    await fetchTypeOptions(); // Load the type options first, then run clustering with default settings
    runClustering();
});