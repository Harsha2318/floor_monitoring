# Deployment Guide

## Local Deployment (Single Machine)

### Windows

1. **System Preparation**
   ```powershell
   # Install Python 3.8+
   # Download from python.org and install
   
   # Clone/download project
   cd C:\Users\harsh\floor_monitoring
   
   # Run installer
   .\install.ps1
   ```

2. **Configuration**
   - Edit `app\config.py` for cameras and settings
   - Configure `ABSENCE_TIMEOUT_MINUTES`
   - Set `DETECTION_MODEL` based on hardware

3. **Start Server**
   ```powershell
   .\venv\Scripts\Activate.ps1
   python run.py
   ```

4. **Access System**
   - Open browser: http://localhost:5000
   - Configure cameras in UI
   - Start monitoring

### Linux

1. **System Preparation**
   ```bash
   # Install dependencies
   sudo apt-get update
   sudo apt-get install python3 python3-venv python3-pip
   sudo apt-get install build-essential cmake
   sudo apt-get install libopencv-dev
   
   # Clone project
   cd /opt/floor_monitoring
   
   # Run installer
   bash install.sh
   ```

2. **Configuration**
   - Edit `app/config.py`
   - Configure cameras
   - Adjust settings

3. **Start Server**
   ```bash
   source venv/bin/activate
   python run.py
   ```

## Network Deployment (Multiple Clients)

### Server Setup

1. **Configure Network Access**
   ```python
   # app/config.py
   HOST = '0.0.0.0'  # Allow external connections
   PORT = 5000
   ```

2. **Firewall Configuration**
   ```powershell
   # Windows - Allow inbound on port 5000
   New-NetFirewallRule -DisplayName "Floor Monitoring" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow
   ```
   
   ```bash
   # Linux - UFW
   sudo ufw allow 5000/tcp
   ```

3. **Start Server**
   ```powershell
   python run.py
   ```

### Client Access

- Access from other machines: `http://server-ip:5000`
- Example: `http://192.168.1.100:5000`

## Production Deployment

### Using Gunicorn (Linux)

1. **Install Gunicorn**
   ```bash
   pip install gunicorn eventlet
   ```

2. **Create systemd Service**
   ```bash
   sudo nano /etc/systemd/system/floor-monitoring.service
   ```
   
   ```ini
   [Unit]
   Description=Floor Monitoring System
   After=network.target
   
   [Service]
   Type=simple
   User=monitoring
   WorkingDirectory=/opt/floor_monitoring
   Environment="PATH=/opt/floor_monitoring/venv/bin"
   ExecStart=/opt/floor_monitoring/venv/bin/gunicorn -k eventlet -w 1 -b 0.0.0.0:5000 run:app
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```

3. **Enable and Start**
   ```bash
   sudo systemctl enable floor-monitoring
   sudo systemctl start floor-monitoring
   sudo systemctl status floor-monitoring
   ```

### Using Waitress (Windows)

1. **Install Waitress**
   ```powershell
   pip install waitress
   ```

2. **Create Startup Script** (`start_production.py`)
   ```python
   from waitress import serve
   from app import app
   
   if __name__ == '__main__':
       print("Starting Floor Monitoring System on 0.0.0.0:5000")
       serve(app, host='0.0.0.0', port=5000, threads=4)
   ```

3. **Run**
   ```powershell
   python start_production.py
   ```

4. **Create Windows Service** (Optional)
   - Use NSSM (Non-Sucking Service Manager)
   ```powershell
   nssm install FloorMonitoring "C:\Users\harsh\floor_monitoring\venv\Scripts\python.exe" "C:\Users\harsh\floor_monitoring\start_production.py"
   nssm start FloorMonitoring
   ```

## Reverse Proxy Setup

### Nginx Configuration

1. **Install Nginx**
   ```bash
   sudo apt-get install nginx
   ```

2. **Configure Site**
   ```nginx
   # /etc/nginx/sites-available/floor-monitoring
   server {
       listen 80;
       server_name monitoring.example.com;
       
       location / {
           proxy_pass http://localhost:5000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
       
       location /socket.io {
           proxy_pass http://localhost:5000/socket.io;
           proxy_http_version 1.1;
           proxy_buffering off;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "Upgrade";
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       }
   }
   ```

3. **Enable Site**
   ```bash
   sudo ln -s /etc/nginx/sites-available/floor-monitoring /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

## SSL/HTTPS Setup

### Using Let's Encrypt

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d monitoring.example.com

# Auto-renewal is configured automatically
```

## Database Backup

### Automated Backup Script

**Windows** (`backup.ps1`):
```powershell
$date = Get-Date -Format "yyyyMMdd_HHmmss"
$backupDir = ".\data\backup"
$dbFile = ".\data\monitoring.db"

if (-not (Test-Path $backupDir)) {
    New-Item -ItemType Directory -Path $backupDir
}

Copy-Item $dbFile "$backupDir\monitoring_$date.db"

# Keep only last 30 days
Get-ChildItem $backupDir -Filter *.db | 
    Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-30)} | 
    Remove-Item
```

**Linux** (`backup.sh`):
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./data/backup"
DB_FILE="./data/monitoring.db"

mkdir -p $BACKUP_DIR
cp $DB_FILE "$BACKUP_DIR/monitoring_$DATE.db"

# Keep only last 30 days
find $BACKUP_DIR -name "*.db" -mtime +30 -delete
```

### Schedule Backups

**Windows Task Scheduler**:
```powershell
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-File C:\Users\harsh\floor_monitoring\backup.ps1"
$trigger = New-ScheduledTaskTrigger -Daily -At 2am
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "Floor Monitoring Backup" -Description "Daily database backup"
```

**Linux Cron**:
```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /opt/floor_monitoring/backup.sh
```

## Monitoring and Maintenance

### Log Rotation

**Linux** (`/etc/logrotate.d/floor-monitoring`):
```
/opt/floor_monitoring/data/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 monitoring monitoring
    sharedscripts
    postrotate
        systemctl reload floor-monitoring
    endscript
}
```

### Health Check Script

```python
# healthcheck.py
import requests
import sys

try:
    response = requests.get('http://localhost:5000/api/system/status', timeout=5)
    if response.status_code == 200:
        print("System healthy")
        sys.exit(0)
    else:
        print(f"System unhealthy: {response.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"System down: {e}")
    sys.exit(1)
```

## Scaling Considerations

### Multiple Cameras
- Distribute cameras across multiple servers
- Each server handles 2-4 cameras
- Central database for aggregation

### Performance Optimization
- Use GPU for YOLO detection
- Increase FRAME_SKIP for lower CPU usage
- Reduce resolution for faster processing
- Use multiple processing threads

## Security Best Practices

1. **Change Secret Key**
   ```python
   # app/config.py
   SECRET_KEY = 'generate-random-key-here'
   ```

2. **Disable Debug Mode**
   ```python
   DEBUG = False
   ```

3. **Add Authentication** (recommended for production)
   - Implement Flask-Login
   - Add user management
   - Require login for access

4. **Secure Camera Credentials**
   - Store in environment variables
   - Use secrets management
   - Never commit to version control

5. **Network Security**
   - Use HTTPS
   - Firewall rules
   - VPN for remote access
   - Regular security updates

## Troubleshooting Deployment

### Server Won't Start
- Check port availability
- Verify Python environment
- Review error logs
- Check permissions

### Can't Access from Other Computers
- Verify HOST = '0.0.0.0' in config
- Check firewall rules
- Confirm network connectivity
- Verify correct IP address

### Performance Issues
- Reduce number of cameras
- Increase FRAME_SKIP
- Lower resolution
- Use lighter detection model
- Check system resources

### Database Locked Errors
- Only one process should write
- Check for zombie processes
- Restart system
- Restore from backup if corrupted

## Update Procedure

1. **Backup Current System**
   ```powershell
   # Backup database
   copy data\monitoring.db data\backup\
   
   # Backup configuration
   copy app\config.py app\config.py.backup
   ```

2. **Stop System**
   ```powershell
   # Stop the service/application
   ```

3. **Update Code**
   ```powershell
   git pull origin main
   # or download new version
   ```

4. **Update Dependencies**
   ```powershell
   pip install -r requirements.txt --upgrade
   ```

5. **Test**
   ```powershell
   pytest
   ```

6. **Start System**
   ```powershell
   python run.py
   ```

## Rollback Procedure

If update fails:

1. Stop system
2. Restore code from backup
3. Restore database from backup
4. Restore configuration
5. Restart system

Always test updates in a staging environment first!
