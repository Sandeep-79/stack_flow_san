document.addEventListener("DOMContentLoaded", function () {
    fetch('/data')  // Correct API endpoint
        .then(response => response.json())
        .then(data => {
            console.log("Fetched Data:", data);  // Debugging log

            const ctx = document.getElementById('tagChart').getContext('2d');

            // Extract unique years and tags
            const years = [...new Set(data.map(item => item.Year))].sort();
            const tags = [...new Set(data.map(item => item.Tag))];

            // Create dataset for each tag
            const datasets = tags.map(tag => {
                return {
                    label: tag,
                    data: years.map(year => {
                        const record = data.find(d => d.Year == year && d.Tag === tag);
                        return record ? record.Tag_Count : 0;
                    }),
                    borderColor: '#' + Math.floor(Math.random()*16777215).toString(16), // Random color
                    borderWidth: 2,
                    fill: false
                };
            });

            // Create the Line Chart
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: years,
                    datasets: datasets
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'top',
                        }
                    },
                    scales: {
                        x: { title: { display: true, text: 'Year' } },
                        y: { title: { display: true, text: 'Tag Count' } }
                    }
                }
            });
        })
        .catch(error => console.error("Error fetching data:", error));
});
