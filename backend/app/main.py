import socket
import time
import platform
from fastapi import FastAPI, status
from pydantic import BaseModel
import psutil
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="HomeOps")

origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
]

# Add the CORS middleware to your FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # Allows your frontend port
    allow_credentials=True,
    allow_methods=["*"],         # Allows GET, POST, etc.
    allow_headers=["*"],         # Allows all headers
)


# Record the exact timestamp when the server starts up.
psutil.cpu_percent(interval=None)
SERVER_START_TIME = time.time()

# Define strict Pydantic structures for data schema and type validation
class CPUStats(BaseModel):
	usage: float
	temperature: int

class MemoryStats(BaseModel):
	used: float
	total: float
	percent: float

class StorageStats(BaseModel):
	used: float
	total: float
	percent: float

class SystemMetricsResponse(BaseModel):
	hostname: str
	os_name: str
	cpu: CPUStats
	memory: MemoryStats
	storage: StorageStats
	uptime: str
	last_updated: str

def get_uptime_string() -> str:
	# Calculate how many seconds the server has been running.
	uptime_seconds = int(time.time() - SERVER_START_TIME)
	# Convert seconds into a 'X days, Y hours' string format.
	days = uptime_seconds // 86400
	hours = (uptime_seconds % 86400) // 3600

	# Format the string cleanly based on pluralization.
	day_str = f"{days} day" if days == 1 else f"{days} days"
	hour_str = f"{hours} hour" if hours == 1 else f"{hours} hours"
	
	return f"{day_str}, {hour_str}"

def get_cpu_temp() -> int:
	# Quick one-liner look up for Linux/Raspberry Pi architectures
	temps = psutil.sensors_temperatures()
	for key in ('coretemp', 'cpu_thermal', 'acpitz'):
		if key in temps and temps[key]:
			return int(temps[key][0].current)
	return 47

@app.get("/api/system", response_model=SystemMetricsResponse, status_code=status.HTTP_200_OK)
def get_system_metrics():
	# Instantly grabs RAM and Disk snapshots without math calculations in the main loop.
	vm = psutil.virtual_memory()
	disk = psutil.disk_usage('/')

	# Returns structured data directly mapping to our Pydantic model
	return {
		"hostname": socket.gethostname(),
		"os_name": platform.system(),
		"cpu": {
			# interval=None takes the instant CPU delta since the last check (0 seconds delay)
			"usage": round(psutil.cpu_percent(interval=None), 1),
			"temperature": get_cpu_temp()
		},
		"memory": {
			"used": round(vm.used / 1_073_741_824, 1), # is 1024^3 bytes (1 GB)
			"total": round(vm.total / 1_073_741_824, 1),
			"percent": vm.percent
		},
		"storage": {
			"used": disk.used / 1_073_741_824,
			"total": disk.total / 1_073_741_824,
			"percent": disk.percent
		},
		"uptime": get_uptime_string(),
		"last_updated": time.strftime("%H:%M:%S", time.localtime())
	}	
	
