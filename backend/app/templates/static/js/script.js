async function fetchData() {
    try {
        const response = await fetch('http://192.168.1.14:8000/api/system');
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        updateDashboard(data);
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

function updateDashboard(data) {
    // Update the dashboard with the fetched data
    const isolatedHostname = data.hostname;

    document.getElementById('display-hostname').textContent = isolatedHostname;
    document.getElementById('display-os').textContent = data.os_name;
    document.getElementById('display-uptime').textContent = data.uptime;
    document.getElementById('display-cpu').textContent = data.cpu.usage + '%';
    document.getElementById('display-memory').textContent = data.memory.percent + '%';
    document.getElementById('display-storage').textContent = data.storage.percent + '%';    
    document.getElementById('display-temperature').textContent = data.cpu.temperature + '°C';    
    document.getElementById('display-last-updated').textContent = data.last_updated;    

}

// Call fetchData when the page loads
window.addEventListener('load', fetchData);