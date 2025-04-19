import os
import re
import pyperclip
import time
import subprocess

# Define the default public tunnel address
playit_address = "name-leo.gl.joinmc.link"  # Default public address

# Step 1: Detect the Minecraft LAN port from the log file
def detect_minecraft_port():
    log_path = os.path.expanduser("~\\AppData\\Roaming\\.minecraft\\logs\\latest.log")
    try:
        with open(log_path, 'r', encoding='utf-8') as log_file:
            lines = log_file.readlines()
            for line in reversed(lines):
                print("LOG >>", line.strip(), flush=True)  # Debug line
                match = re.search(r'Local game hosted on port \[(\d+)\]', line)  # Updated regex
                if match:
                    print("MATCHED:", match.group(0), flush=True)  # Debug line
                    return int(match.group(1))
    except FileNotFoundError:
        print("Minecraft log file not found.", flush=True)
    except Exception as e:
        print(f"⚠️ Unexpected error while reading log file: {e}", flush=True)
    return None

# Step 2: Restart the Playit tunnel with the new port
def restart_playit_tunnel(port):
    print(f"🌐 Restarting Playit tunnel with port: {port}", flush=True)

    try:
        # Adjust this command according to the correct Playit tunnel startup process
        subprocess.run(["playit.exe"], check=True)  # Start Playit without additional arguments
        print(f"✅ Playit tunnel updated to: {playit_address}:{port}", flush=True)
        pyperclip.copy(f"{playit_address}:{port}")
        print("🔗 Address copied to clipboard!", flush=True)
    except FileNotFoundError:
        print("⚠️ Playit executable not found. Ensure 'playit.exe' is in your PATH or specify the full path.", flush=True)
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Error restarting Playit tunnel: {e}", flush=True)
    except Exception as e:
        print(f"⚠️ Unexpected error: {e}", flush=True)

# New function: Stop the Playit tunnel
def stop_playit_tunnel():
    print("🛑 Attempting to stop Playit tunnel...", flush=True)
    try:
        subprocess.run(["taskkill", "/IM", "playit.exe", "/F"], check=True)
        print("🛑 Tunnel stopped successfully.", flush=True)
        return "🛑 Tunnel stopped successfully."
    except subprocess.CalledProcessError:
        error_message = "⚠️ Failed to stop tunnel. Playit may not be running."
        print(error_message, flush=True)
        return error_message
    except Exception as e:
        error_message = f"⚠️ Unexpected error: {e}"
        print(error_message, flush=True)
        return error_message

# Step 3: Main program that continuously monitors the Minecraft port
def main():
    previous_port = None
    
    while True:
        try:
            port = detect_minecraft_port()
            
            if port:
                if port != previous_port:
                    restart_playit_tunnel(port)
                    previous_port = port
            else:
                print("⚠️ Could not detect Minecraft LAN world.", flush=True)
            
            time.sleep(5)  # Check every 5 seconds for port changes
        except KeyboardInterrupt:
            print("\n🛑 Program terminated by user.", flush=True)
            break
        except Exception as e:
            print(f"⚠️ Unexpected error in main loop: {e}", flush=True)

if __name__ == "__main__":
    main()
