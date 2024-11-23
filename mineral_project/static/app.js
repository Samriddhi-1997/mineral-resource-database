// Fetch mineral data from the backend
fetch('/minerals')
    .then(response => response.json())
    .then(data => {
        // Prepare data for the chart
        const locations = data.map(d => d.location);  // Get locations
        const reserveSizes = data.map(d => d.reserve_size);  // Get reserve sizes

        // Define the chart data structure
        const chartData = [{
            x: locations,  // X-axis: locations
            y: reserveSizes,  // Y-axis: reserve sizes
            type: 'bar'  // Bar chart
        }];

        // Render the chart
        Plotly.newPlot('visualizations', chartData);
    })
    .catch(error => console.error('Error fetching data:', error));
 console.log('app.js is loaded');
     function generateReport() {
     // Make a GET request to the /generate_report route
    fetch('/generate_report')
        .then(response => {
            // Check if the response is successful
            if (response.ok) {
                return response.blob(); // Get the blob data (PDF file)
            } else {
                throw new Error('Failed to generate report');
            }
        })
         .then(blob => {
            // Create a download link for the PDF blob
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = 'report.pdf';  // Set the default filename
            link.click();  // Trigger the download
        })
        .catch(error => {
            console.error('Error:', error);
        });
}
    