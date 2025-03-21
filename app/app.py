from flask import Flask, request, jsonify
import libtorrent as lt
import threading
import time

app = Flask(__name__)

# Set up the torrent session
torrent_session = lt.session()
torrent_session.listen_on(6881, 6891)

# Dictionary to track torrents
torrents = {}

def add_torrent(magnet_link):
    """Adds a torrent and begins downloading."""
    params = lt.add_torrent_params()
    params.save_path = "./videos"
    params.url = magnet_link
    handle = torrent_session.add_torrent(params)
    torrents[handle.info_hash()] = handle
    return str(handle.info_hash())

def get_torrent_status(info_hash):
    """Returns the status of a torrent."""
    handle = torrents.get(info_hash)
    if not handle:
        return {"error": "Torrent not found"}
    
    status = handle.status()
    return {
        "progress": status.progress * 100,
        "download_rate": status.download_rate,
        "upload_rate": status.upload_rate,
        "state": str(status.state)
    }

@app.route("/add_torrent", methods=["POST"])
def add_torrent_api():
    data = request.json
    magnet_link = data.get("magnet")
    if not magnet_link:
        return jsonify({"error": "No magnet link provided"}), 400
    
    info_hash = add_torrent(magnet_link)
    return jsonify({"info_hash": info_hash})

@app.route("/torrent_status/<info_hash>", methods=["GET"])
def torrent_status_api(info_hash):
    return jsonify(get_torrent_status(info_hash))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
