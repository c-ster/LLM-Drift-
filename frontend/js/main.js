document.addEventListener('DOMContentLoaded', () => {
    // Element selectors
    const questionSelect = document.getElementById('question-select');
    const app = document.getElementById('app');
    const driftChartCanvas = document.getElementById('drift-chart');
    const modal = document.getElementById('questions-modal');
    const showQuestionsBtn = document.getElementById('show-questions-btn');
    const closeBtn = document.querySelector('.close-btn');
    const questionsList = document.getElementById('questions-list');

    // State variables
    let driftChart;
    let allResponses = [];
    let uniqueQuestions = [];

    // --- Modal Logic ---
    showQuestionsBtn.onclick = () => {
        questionsList.innerHTML = ''; // Clear previous list
        uniqueQuestions.forEach(q => {
            const li = document.createElement('li');
            li.textContent = q;
            questionsList.appendChild(li);
        });
        modal.style.display = 'block';
    };

    closeBtn.onclick = () => {
        modal.style.display = 'none';
    };

    window.onclick = (event) => {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    };

    // --- Data Fetching and Initial Render ---
    fetch('/api/responses/')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            allResponses = data;
            uniqueQuestions = [...new Set(allResponses.map(r => r.question))];
            
            // Populate dropdown
            questionSelect.innerHTML = ''; // Clear existing options
            uniqueQuestions.forEach(question => {
                const option = document.createElement('option');
                option.value = question;
                option.textContent = question;
                questionSelect.appendChild(option);
            });

            // Initial render if data is available
            if (uniqueQuestions.length > 0) {
                render();
            }

            // Add event listener for dropdown changes
            questionSelect.addEventListener('change', render);
        })
        .catch(error => {
            console.error('Error fetching data:', error);
            app.innerHTML = '<p>Failed to load data. Please check the console for more information. Is the backend running?</p>';
        });

    // --- Main Render Function ---
    function render() {
        const selectedQuestion = questionSelect.value;
        const filteredResponses = allResponses.filter(r => r.question === selectedQuestion);
        renderTable(filteredResponses);
        renderChart(filteredResponses);
    }

    // --- Table Rendering ---
    function renderTable(responses) {
        app.innerHTML = ''; // Clear previous table
        if (!responses || responses.length === 0) {
            app.innerHTML = '<p>No responses found for this question yet.</p>';
            return;
        }

        const table = document.createElement('table');
        table.className = 'response-table';

        const thead = document.createElement('thead');
        thead.innerHTML = `
            <tr>
                <th>Timestamp</th>
                <th>LLM</th>
                <th>Response</th>
                <th>Drift Score</th>
            </tr>
        `;
        table.appendChild(thead);

        const tbody = document.createElement('tbody');
        const sortedResponses = responses.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
        sortedResponses.forEach(res => {
            const row = document.createElement('tr');
            const driftScore = res.similarity_score !== null ? `${(res.similarity_score * 100).toFixed(2)}%` : 'N/A';
            row.innerHTML = `
                <td>${new Date(res.timestamp).toLocaleString()}</td>
                <td>${res.llm_name}</td>
                <td>${res.response}</td>
                <td>${driftScore}</td>
            `;
            tbody.appendChild(row);
        });

        table.appendChild(tbody);
        app.appendChild(table);
    }

    // --- Chart Rendering ---
    function renderChart(responses) {
        const llms = [...new Set(responses.map(r => r.llm_name))];
        
        const datasets = llms.map(llm => {
            const llmResponses = responses
                .filter(r => r.llm_name === llm && r.similarity_score !== null)
                .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
            
            return {
                label: llm,
                data: llmResponses.map(r => ({ x: new Date(r.timestamp), y: r.similarity_score })),
                fill: false,
                borderColor: getRandomColor(),
                tension: 0.1
            };
        });

        if (driftChart) {
            driftChart.destroy();
        }

        driftChart = new Chart(driftChartCanvas, {
            type: 'line',
            data: {
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        type: 'time',
                        title: {
                            display: true,
                            text: 'Timestamp'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        max: 1,
                        title: {
                            display: true,
                            text: 'Similarity Score'
                        }
                    }
                }
            }
        });
    }

    // --- Utility Function ---
    function getRandomColor() {
        const letters = '0123456789ABCDEF';
        let color = '#';
        for (let i = 0; i < 6; i++) {
            color += letters[Math.floor(Math.random() * 16)];
        }
        return color;
    }


});
