
function fetchQueueStatus() {
    const dataContainer = document.getElementById('live-queue-data');
    if (!dataContainer) return;

    fetch('/api/patient_queue_status/')
        .then(response => response.json())
        .then(data => {
            if (data.active) {
                if (data.is_consulting) {
                    document.getElementById('consulting-alert').style.display = 'block';
                    dataContainer.innerHTML = '';
                } else {
                    document.getElementById('consulting-alert').style.display = 'none';
                    dataContainer.innerHTML = `
                        <div style="font-size: 1.2em; margin-bottom: 10px;">
                            <strong>Currently Serving:</strong> ${data.current_serving}
                        </div>
                        <div style="font-size: 1.2em; margin-bottom: 10px;">
                            <strong>Patients Ahead:</strong> ${data.patients_ahead}
                        </div>
                        <div style="font-size: 1.2em; margin-bottom: 10px; color: #d35400;">
                            <strong>Estimated Wait Time:</strong> ~${data.estimated_wait} minutes
                        </div>
                        <div style="font-size: 1.2em;">
                            <strong>Status:</strong> <span class="badge status-waiting">${data.status}</span>
                        </div>
                    `;
                }
            } else {
                window.location.reload();
            }
        })
        .catch(err => console.error('Error fetching queue status:', err));
}

if (document.getElementById('live-queue-data')) {
    setInterval(fetchQueueStatus, 5000);
    fetchQueueStatus();
}
