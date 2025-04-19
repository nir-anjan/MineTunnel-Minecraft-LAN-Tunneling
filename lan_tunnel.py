import os
import re
import pyperclip
import time
import subprocess

# Step 1: Detect the Minecraft LAN port from the log file
def detect_minecraft_port():
    log_path = os.path.expanduser("~\\AppData\\Roaming\\.minecraft\\logs\\latest.log")
    try:
        with open(log_path, 'r', encoding='utf-8') as log_file:
            lines = log_file.readlines()
            for line in reversed(lines):
                print("LOG >>", line.strip())  # Debug line
                match = re.search(r'Local game hosted on port \[(\d+)\]', line)  # Updated regex
                if match:
                    print("MATCHED:", match.group(0))  # Debug line
                    return int(match.group(1))
    except FileNotFoundError:
        print("Minecraft log file not found.")
    except Exception as e:
        print(f"⚠️ Unexpected error while reading log file: {e}")
    return None

# Step 2: Restart the Playit tunnel with the new port
def restart_playit_tunnel(port):
    playit_address = "name-leo.gl.joinmc.link"  # Your public address
    print(f"🌐 Restarting Playit tunnel with port: {port}")

    try:
        # Adjust this command according to the correct Playit tunnel startup process
        subprocess.run(["playit.exe"], check=True)  # Start Playit without additional arguments
        print(f"✅ Playit tunnel updated to: {playit_address}:{port}")
        pyperclip.copy(f"{playit_address}:{port}")
        print("🔗 Address copied to clipboard!")
    except FileNotFoundError:
        print("⚠️ Playit executable not found. Ensure 'playit.exe' is in your PATH or specify the full path.")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Error restarting Playit tunnel: {e}")
    except Exception as e:
        print(f"⚠️ Unexpected error: {e}")

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
                print("⚠️ Could not detect Minecraft LAN world.")
            
            time.sleep(5)  # Check every 5 seconds for port changes
        except KeyboardInterrupt:
            print("\n🛑 Program terminated by user.")
            break
        except Exception as e:
            print(f"⚠️ Unexpected error in main loop: {e}")

if __name__ == "__main__":
    main()
