from flask import Flask, jsonify, request
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)

# Configure the data directory path
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <title>Top 10 Tags Trend Analysis</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #1a202c 0%, #2d3748 100%);
            color: #f7fafc;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: rgba(255, 255, 255, 0.1);
            padding: 30px;
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        h1 {
            text-align: center;
            margin-bottom: 30px;
            color: #f7fafc;
        }
        
        .chart-container {
            height: 600px;
            margin: 20px 0;
            background-color: rgba(255, 255, 255, 0.05);
            padding: 20px;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .summary {
            margin-top: 20px;
            padding: 15px;
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            font-size: 0.9em;
            line-height: 1.6;
        }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Top 10 Most Used Tags Over Time</h1>
            <div class="chart-container">
                <canvas id="myChart"></canvas>
            </div>
            <div class="summary" id="summary">
                <!-- Will be populated dynamically -->
            </div>
        </div>

        <script>
            let myChart = null;

            function getColors(count) {
                const colors = [
                    '#4299e1', '#48bb78', '#ed8936', '#9f7aea', '#f56565',
                    '#38b2ac', '#ed64a6', '#667eea', '#d69e2e', '#4a5568'
                ];
                return colors.slice(0, count);
            }

            function createChart() {
                fetch('/data')
                    .then(response => response.json())
                    .then(data => {
                        if (myChart) {
                            myChart.destroy();
                        }

                        const colors = getColors(data.tags.length);
                        const datasets = data.tags.map((tag, index) => ({
                            label: tag,
                            data: data.percentages[tag],
                            borderColor: colors[index],
                            backgroundColor: colors[index] + '20',
                            tension: 0.4,
                            pointRadius: 4,
                            pointHoverRadius: 6
                        }));

                        const ctx = document.getElementById('myChart').getContext('2d');
                        myChart = new Chart(ctx, {
                            type: 'line',
                            data: {
                                labels: data.years,
                                datasets: datasets
                            },
                            options: {
                                responsive: true,
                                maintainAspectRatio: false,
                                interaction: {
                                    intersect: false,
                                    mode: 'index'
                                },
                                scales: {
                                    y: {
                                        beginAtZero: true,
                                        grid: {
                                            color: 'rgba(255, 255, 255, 0.1)'
                                        },
                                        ticks: {
                                            color: '#f7fafc',
                                            callback: function(value) {
                                                return value + '%';
                                            }
                                        },
                                        title: {
                                            display: true,
                                            text: 'Percentage of Questions (%)',
                                            color: '#f7fafc'
                                        }
                                    },
                                    x: {
                                        grid: {
                                            color: 'rgba(255, 255, 255, 0.1)'
                                        },
                                        ticks: {
                                            color: '#f7fafc'
                                        },
                                        title: {
                                            display: true,
                                            text: 'Year',
                                            color: '#f7fafc'
                                        }
                                    }
                                },
                                plugins: {
                                    legend: {
                                        position: 'top',
                                        labels: {
                                            color: '#f7fafc',
                                            padding: 20,
                                            usePointStyle: true,
                                            pointStyle: 'circle'
                                        }
                                    },
                                    tooltip: {
                                        backgroundColor: 'rgba(26, 32, 44, 0.9)',
                                        titleColor: '#f7fafc',
                                        bodyColor: '#f7fafc',
                                        borderColor: 'rgba(255, 255, 255, 0.1)',
                                        borderWidth: 1,
                                        callbacks: {
                                            label: function(context) {
                                                return `${context.dataset.label}: ${context.raw}%`;
                                            }
                                        }
                                    }
                                }
                            }
                        });

                        // Update summary
                        const summaryDiv = document.getElementById('summary');
                        const tagsList = data.tags.map((tag, index) => 
                            `${index + 1}. ${tag}: ${data.tag_percentages[tag]}%`
                        ).join('<br>');
                        
                        summaryDiv.innerHTML = `
                            <strong>Top 10 Tags Summary:</strong><br>
                            ${tagsList}<br><br>
                            Total Records: ${data.total_records}<br>
                            Years Analyzed: ${data.years[0]} to ${data.years[data.years.length - 1]}
                        `;
                    });
            }

            // Initialize chart
            createChart();
        </script>
    </body>
    </html>
    '''

@app.route('/data')
def get_data():
    try:
        df = pd.read_csv('data.csv')
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Extract year from date
        df['Year'] = df['Date'].dt.year
        
        # Get top 10 tags
        tag_counts = df['Tag'].value_counts()
        top_10_tags = tag_counts.head(10)
        
        # Get unique years
        years = sorted(df['Year'].unique())
        
        # Calculate percentages
        percentages = {}
        
        # Calculate percentages by year for each tag
        for tag in top_10_tags.index:
            yearly_data = []
            for year in years:
                year_total = len(df[df['Year'] == year])
                tag_count = len(df[(df['Year'] == year) & (df['Tag'] == tag)])
                percentage = round((tag_count / year_total * 100), 2) if year_total > 0 else 0
                yearly_data.append(percentage)
            percentages[tag] = yearly_data
        
        # Calculate overall percentages for each tag
        total_questions = len(df)
        tag_percentages = {tag: round((count / total_questions * 100), 2) 
                         for tag, count in top_10_tags.items()}
        
        return jsonify({
            'years': [str(year) for year in years],
            'tags': top_10_tags.index.tolist(),
            'percentages': percentages,
            'tag_percentages': tag_percentages,
            'total_records': total_questions
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Ensure the data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)
    app.run() 
