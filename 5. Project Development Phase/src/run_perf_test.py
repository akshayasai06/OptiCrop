import subprocess
import urllib.request
import urllib.error
import json
import time
import threading
import os
import sys

def run_load_test():
    # Start Flask server
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    app_path = os.path.join(base_dir, "app.py")
    python_path = os.path.join(os.path.dirname(base_dir), "venv", "bin", "python")
    
    home_url = "http://127.0.0.1:5000/"
    predict_url = "http://127.0.0.1:5000/predict"
    
    # Payload for prediction
    payload = {
        "N": 90.0,
        "P": 42.0,
        "K": 43.0,
        "temperature": 20.87,
        "humidity": 82.0,
        "ph": 6.5,
        "rainfall": 202.9
    }
    data_bytes = json.dumps(payload).encode('utf-8')
    
    already_running = False
    proc = None
    
    # Check if server is already running
    try:
        req = urllib.request.Request(home_url)
        with urllib.request.urlopen(req, timeout=1) as response:
            if response.getcode() == 200:
                print("Found existing Flask server running on port 5000. Using it.")
                already_running = True
    except Exception:
        pass
        
    if not already_running:
        print(f"Starting Flask server at {app_path} with {python_path}...")
        env = os.environ.copy()
        env["FLASK_DEBUG"] = "false"
        env["PORT"] = "5000"
        
        # Open log file
        log_file = open("/tmp/flask_server.log", "w")
        
        proc = subprocess.Popen(
            [python_path, "-u", app_path],
            stdout=log_file,
            stderr=log_file,
            cwd=base_dir,
            env=env,
            preexec_fn=os.setsid
        )
        
        # Wait for server to start and check connection
        time.sleep(12)
        
        try:
            req = urllib.request.Request(home_url)
            with urllib.request.urlopen(req, timeout=3) as response:
                print(f"Server response code: {response.getcode()}")
        except Exception as e:
            print(f"Could not connect to Flask server: {e}")
            if os.path.exists("/tmp/flask_server.log"):
                with open("/tmp/flask_server.log", "r") as lf:
                    print("--- Flask Server Logs ---")
                    print(lf.read())
                    print("-------------------------")
            if proc:
                try:
                    os.killpg(os.getpgid(proc.pid), 9)
                except Exception:
                    pass
            return
            
    print("Connection successful! Running performance scenarios...")
    
    results = {}
    
    # Monitor CPU and Memory of the Flask process if we started it
    max_cpu = 0.0
    max_mem = 0.0
    
    def monitor_resources():
        nonlocal max_cpu, max_mem
        if not proc:
            return
        while proc.poll() is None:
            try:
                cmd = f"ps -p {proc.pid} -o %cpu,%mem --no-headers"
                out = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
                if out:
                    parts = out.split()
                    if len(parts) >= 2:
                        cpu = float(parts[0])
                        mem = float(parts[1])
                        max_cpu = max(max_cpu, cpu)
                        max_mem = max(max_mem, mem)
            except Exception:
                pass
            time.sleep(0.2)
            
    if proc:
        monitor_thread = threading.Thread(target=monitor_resources, daemon=True)
        monitor_thread.start()
    
    # Helper to send a request
    def send_request(url, data=None):
        start = time.time()
        try:
            if data:
                req = urllib.request.Request(
                    url, 
                    data=data, 
                    headers={'Content-Type': 'application/json'}
                )
            else:
                req = urllib.request.Request(url)
                
            with urllib.request.urlopen(req, timeout=10) as response:
                status = response.getcode()
                response.read()
                elapsed = time.time() - start
                return elapsed, status == 200
        except urllib.error.HTTPError as e:
            elapsed = time.time() - start
            return elapsed, False
        except Exception as e:
            elapsed = time.time() - start
            return elapsed, False

    # Scenarios:
    # 1. Homepage Load: 1 Virtual User (VU), 50 total requests, sequential
    # 2. Predict Load: 10 VUs, 100 requests (10 reqs per user)
    # 3. Predict Stress: 50 VUs, 500 requests (10 reqs per user)
    # 4. Predict Spike: 100 VUs, 1000 requests (10 reqs per user)
    
    scenarios = [
        {"id": 1, "name": "Homepage Load Test", "users": 1, "requests_per_user": 50, "url": home_url, "use_post": False},
        {"id": 2, "name": "Predict API Load Test", "users": 10, "requests_per_user": 10, "url": predict_url, "use_post": True},
        {"id": 3, "name": "Predict API Stress Test", "users": 50, "requests_per_user": 10, "url": predict_url, "use_post": True},
        {"id": 4, "name": "Predict API Spike Test", "users": 100, "requests_per_user": 10, "url": predict_url, "use_post": True}
    ]
    
    all_latencies = []
    total_errors = 0
    total_requests_run = 0
    
    print("\n--- Running Scenarios ---")
    for sc in scenarios:
        num_users = sc["users"]
        reqs_per_user = sc["requests_per_user"]
        total_reqs = num_users * reqs_per_user
        print(f"\nScenario {sc['id']}: {sc['name']}")
        print(f"Virtual Users: {num_users} | Total Requests: {total_reqs}")
        
        latencies = []
        errors = [0] # List so it can be mutated in thread
        
        def user_thread():
            user_errors = 0
            for _ in range(reqs_per_user):
                post_data = data_bytes if sc["use_post"] else None
                elapsed, success = send_request(sc["url"], post_data)
                latencies.append(elapsed)
                if not success:
                    user_errors += 1
            # Add to main error count thread-safely-ish
            errors[0] += user_errors
        
        threads = []
        start_time = time.time()
        
        for _ in range(num_users):
            t = threading.Thread(target=user_thread)
            threads.append(t)
            t.start()
            
        for t in threads:
            t.join()
            
        duration = time.time() - start_time
        avg_lat = sum(latencies) / len(latencies) if latencies else 0
        max_lat = max(latencies) if latencies else 0
        throughput = len(latencies) / duration if duration > 0 else 0
        error_rate = (errors[0] / len(latencies)) * 100 if latencies else 0
        
        print(f"Duration: {duration:.2f} seconds")
        print(f"Avg Response Time: {avg_lat * 1000:.2f} ms")
        print(f"Max Response Time: {max_lat * 1000:.2f} ms")
        print(f"Throughput: {throughput:.2f} req/sec")
        print(f"Error Rate: {error_rate:.2f}%")
        
        results[sc["id"]] = {
            "name": sc["name"],
            "users": num_users,
            "duration_sec": duration,
            "avg_latency_sec": avg_lat,
            "max_latency_sec": max_lat,
            "throughput_req_sec": throughput,
            "error_rate_percent": error_rate,
            "errors": errors[0],
            "total_reqs": total_reqs
        }
        
        all_latencies.extend(latencies)
        total_errors += errors[0]
        total_requests_run += total_reqs

    # Stop server
    print("\nStopping Flask server...")
    if proc:
        try:
            os.killpg(os.getpgid(proc.pid), 9)
        except Exception:
            pass
        proc.wait()
    
    # Calculate overall metrics
    overall_avg_lat = sum(all_latencies) / len(all_latencies) if all_latencies else 0
    overall_max_lat = max(all_latencies) if all_latencies else 0
    overall_error_rate = (total_errors / total_requests_run) * 100 if total_requests_run else 0
    
    print("\n=== PERFORMANCE TEST SUMMARY ===")
    print(f"Overall Avg Latency: {overall_avg_lat * 1000:.2f} ms")
    print(f"Overall Max Latency: {overall_max_lat * 1000:.2f} ms")
    print(f"Overall Error Rate: {overall_error_rate:.2f}%")
    print(f"Max CPU Observed: {max_cpu:.2f}%")
    print(f"Max Memory Observed: {max_mem:.2f}%")
    
    # Write report file
    report_path = os.path.join(base_dir, "perf_test_results.json")
    with open(report_path, "w") as f:
        json.dump({
            "scenarios": results,
            "overall": {
                "avg_latency_sec": overall_avg_lat,
                "max_latency_sec": overall_max_lat,
                "error_rate_percent": overall_error_rate,
                "max_cpu_percent": max_cpu,
                "max_mem_percent": max_mem
            }
        }, f, indent=4)
    print(f"Results saved to {report_path}")

if __name__ == "__main__":
    run_load_test()
